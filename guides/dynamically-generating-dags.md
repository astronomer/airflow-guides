---
title: "Dynamically Generating DAGs in Airflow"
description: "Using a base DAG template to create multiple DAGs."
date: 2018-05-21T00:00:00.000Z
slug: "dynamically-generating-dags"
heroImagePath: "https://assets.astronomer.io/website/img/guides/dynamicdags.png"
tags: ["DAGs", "Best Practices"]
---
> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/dynamic-dags-tutorial).

## Overview

In Airflow, [DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags) are defined as Python code. Airflow executes all Python code in the `dags_folder` and loads any `DAG` objects that appear in `globals()`. The simplest way of creating a DAG is to write it as a static Python file. 

However, sometimes manually writing DAGs isn't practical. Maybe you have hundreds or thousands of DAGs that do similar things with just a parameter changing between them. Or maybe you need a set of DAGs to load tables, but don't want to manually update DAGs every time those tables change. In these cases, and others, it can make more sense to dynamically generate DAGs. 

Because everything in Airflow is code, you can dynamically generate DAGs using Python alone. As long as a `DAG` object in `globals()` is created by Python code that lives in the `dags_folder`, Airflow will load it. In this guide, we'll cover a few of the many ways you can generate DAGs. We'll also discuss when DAG generation is a good option, and some pitfalls to watch out for when doing this at scale.


## Single-File Methods

One method for dynamically generating DAGs is to have a single Python file which generates DAGs based on some input parameter(s) (e.g. a list of APIs or tables). A common use case for this is an ETL or ELT-type pipeline where there are many data sources or destinations. This requires creating many DAGs that all follow a similar pattern.

Some benefits of the single-file method:

- It's simple and easy to implement.
- It can accommodate input parameters from many different sources (see a few examples below).
- Adding DAGs is nearly instantaneous since it requires only changing the input parameters.

However, there are also drawbacks:

- Since a DAG file isn't actually being created, your visibility into the code behind any specific DAG is limited.
- Since this method requires a Python file in the `dags_folder`, the generation code will be executed every time the dag is parsed. How frequently this occurs is controlled by the parameter `min_file_process_interval` ([see Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#min-file-process-interval)). This can cause performance issues if the total number of DAGs is large, or if the code is connecting to an external system such as a database. For more on this, see the Scalability section below.

In the following examples, the single-file method is implemented differently based on which input parameters are used for generating DAGs.


### Example: Use a Create_DAG Method

To dynamically create DAGs from a file, we need to define a Python function that will generate the DAGs based on an input parameter. In this case, we're going to define a DAG template within a `create_dag` function. The code here is very similar to what you would use when creating a single DAG, but it is wrapped in a method that allows for custom parameters to be passed in.

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime


def create_dag(dag_id,
               schedule,
               dag_number,
               default_args):

    def hello_world_py(*args):
        print('Hello World')
        print('This is DAG: {}'.format(str(dag_number)))

    dag = DAG(dag_id,
              schedule_interval=schedule,
              default_args=default_args)

    with dag:
        t1 = PythonOperator(
            task_id='hello_world',
            python_callable=hello_world_py,
            dag_number=dag_number)

    return dag
```

In this example, the input parameters can come from any source that the Python script can access. We can then set a simple loop (`range(1, 4)`) to generate these unique parameters and pass them to the global scope, thereby registering them as valid DAGs to the Airflow scheduler:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime


def create_dag(dag_id,
               schedule,
               dag_number,
               default_args):

    def hello_world_py(*args):
        print('Hello World')
        print('This is DAG: {}'.format(str(dag_number)))

    dag = DAG(dag_id,
              schedule_interval=schedule,
              default_args=default_args)

    with dag:
        t1 = PythonOperator(
            task_id='hello_world',
            python_callable=hello_world_py)

    return dag


# build a dag for each number in range(10)
for n in range(1, 4):
    dag_id = 'loop_hello_world_{}'.format(str(n))

    default_args = {'owner': 'airflow',
                    'start_date': datetime(2021, 1, 1)
                    }

    schedule = '@daily'
    dag_number = n

    globals()[dag_id] = create_dag(dag_id,
                                  schedule,
                                  dag_number,
                                  default_args)
```

And if we look at the Airflow UI we can see the DAGs have been created:

![DAGs from Loop](https://assets2.astronomer.io/main/guides/dynamic-dags/dag_from_loop_zoom.png)

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/blog/7-common-errors-to-check-when-debugging-airflow-dag?banner=learn-more-banner-click">7 Common Errors to Check when Debugging Airflow DAGs</a></li>
    <li data-icon="→"><a href="/events/webinars/trigger-dags-any-schedule?banner=learn-more-banner-click">Scheduling In Airflow Webinar</a></li>
    <li data-icon="→"><a href="/events/webinars/dynamic-dags?banner=learn-more-banner-click">Dynamic DAGs Webinar</a></li>
    <li data-icon="→"><a href="/guides/dag-best-practices?banner=learn-more-banner-click">DAG Writing Best Practices in Apache Airflow</a></li>
</ul>

### Example: Generate DAGs From Variables

As mentioned above, the input parameters don't have to exist in the DAG file itself. Another common form of generating DAGs is by setting values in a Variable object.

![Airflow UI variables tab with a DAG Number variable](https://assets2.astronomer.io/main/guides/dynamic-dags/dag_number_variable.png)

We can retrieve this value by importing the Variable class and passing it into our `range`. Because we want the interpreter to register this file as valid regardless of whether the variable exists, the `default_var` is set to 3.

```python
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from datetime import datetime


def create_dag(dag_id,
               schedule,
               dag_number,
               default_args):

    def hello_world_py(*args):
        print('Hello World')
        print('This is DAG: {}'.format(str(dag_number)))

    dag = DAG(dag_id,
              schedule_interval=schedule,
              default_args=default_args)

    with dag:
        t1 = PythonOperator(
            task_id='hello_world',
            python_callable=hello_world_py)

    return dag


number_of_dags = Variable.get('dag_number', default_var=3)
number_of_dags = int(number_of_dags)

for n in range(1, number_of_dags):
    dag_id = 'hello_world_{}'.format(str(n))

    default_args = {'owner': 'airflow',
                    'start_date': datetime(2021, 1, 1)
                    }

    schedule = '@daily'
    dag_number = n
    globals()[dag_id] = create_dag(dag_id,
                                  schedule,
                                  dag_number,
                                  default_args)

```

We can then go to the Airflow UI and see all of the new DAGs that have been created.

![DAGs from Variables in the Airflow UI](https://assets2.astronomer.io/main/guides/dynamic-dags/dag_from_variables.png)

### Example: Generate DAGs From Connections

Another way to define input parameters for dynamically generating DAGs is by defining Airflow connections. This can be a good option if each of your DAGs connects to a database or an API. Because you will be setting up those connections anyway, creating the DAGs from that source avoids redundant work. 

To implement this method, we can pull the connections we have in our Airflow metadata database by instantiating the "Session" and querying the "Connection" table. We can also filter this query so that it only pulls connections that match a certain criteria.

![List of connections in the Airflow UI](https://assets2.astronomer.io/main/guides/dynamic-dags/connections.png)

```python
from airflow import DAG, settings
from airflow.models import Connection
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def create_dag(dag_id,
               schedule,
               dag_number,
               default_args):

    def hello_world_py(*args):
        print('Hello World')
        print('This is DAG: {}'.format(str(dag_number)))

    dag = DAG(dag_id,
              schedule_interval=schedule,
              default_args=default_args)

    with dag:
        t1 = PythonOperator(
            task_id='hello_world',
            python_callable=hello_world_py)

    return dag


session = settings.Session()
conns = (session.query(Connection.conn_id)
                .filter(Connection.conn_id.ilike('%MY_DATABASE_CONN%'))
                .all())

for conn in conns:
    dag_id = 'connection_hello_world_{}'.format(conn[0])

    default_args = {'owner': 'airflow',
                    'start_date': datetime(2018, 1, 1)
                    }

    schedule = '@daily'
    dag_number = conn

    globals()[dag_id] = create_dag(dag_id,
                                  schedule,
                                  dag_number,
                                  default_args)

```

Notice that like before we are accessing the Models library to bring in the `Connection` class (as we did previously with the `Variable` class). We are also accessing the `Session()` class from `settings`, which will allow us to query the current database session.

![DAGs created from connections](https://assets2.astronomer.io/main/guides/dynamic-dags/dag_from_connections.png)

We can see that all of the connections that match our filter have now been created as a unique DAG.

## Multiple-File Methods

Another method for dynamically generating DAGs is to use code to generate full Python files for each DAG. The end result of this method is having one Python file per generated DAG in your `dags_folder`.

One way of implementing this method in production is to have a Python script that generates DAG files when executed as part of a CI/CD workflow. The DAGs are generated during the CI/CD build and then deployed to Airflow. You could also have another DAG that runs the generation script periodically.

Some benefits of this method:

- It's more scalable than single-file methods. Because the DAG files aren't being generated by parsing code in the `dags_folder`, the DAG generation code isn't executed on every scheduler heartbeat. 
- Since DAG files are being explicitly created before deploying to Airflow, you have full visibility into the DAG code, including from the Code button in the Airflow UI.

On the other hand, this method includes drawbacks:

- It can be complex to set up.
- Changes to DAGs or additional DAGs won't be generated until the script is run, which in some cases requires a deployment.

Below we'll show a simple example of how this method could be implemented.

### Example: Generate DAGs From JSON Config Files

One way of implementing a multiple-file method is using a Python script to generate DAG files based on a set of JSON configuration files. For this simple example, we will assume that all DAGs will have the same structure: each will have a single task that uses the `PostgresOperator` to execute a query. This use case might be relevant for a team of analysts who need to schedule SQL queries, where the DAG is mostly the same but the query and the schedule are changing.

To start, we will create a DAG 'template' file that defines the DAG's structure. This looks just like a regular DAG file, but we have added specific variables where we know information is going to be dynamically generated, namely the `dag_id`, `scheduletoreplace`, and `querytoreplace`. 

```python
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime

default_args = {'owner': 'airflow',
                'start_date': datetime(2021, 1, 1)
                }

dag = DAG(dag_id,
            schedule_interval=scheduletoreplace,
            default_args=default_args,
            catchup=False)

with dag:
    t1 = PostgresOperator(
        task_id='postgres_query',
        postgres_conn_id=connection_id
        sql=querytoreplace)

```

Next we create a `dag-config` folder that will contain a JSON config file for each DAG. The config file should define the parameters that we noted above, the DAG Id, schedule interval, and query to be executed.

```Json
{
    "DagId": "dag_file_1",
    "Schedule": "'@daily'",
    "Query":"'SELECT * FROM table1;'"
}
```

Finally, we create a Python script that will create the DAG files based on the template and the config files. The script loops through every config file in the `dag-config/` folder, makes a copy of the template in the `dags/` folder, and overwrites the parameters in that file with the ones from the config file.

```python
import json
import os
import shutil
import fileinput

config_filepath = 'include/dag-config/'
dag_template_filename = 'include/dag-template.py'

for filename in os.listdir(config_filepath):
    f = open(filepath + filename)
    config = json.load(f)
    
    new_filename = 'dags/'+config['DagId']+'.py'
    shutil.copyfile(dag_template_filename, new_filename)
    

    for line in fileinput.input(new_filename, inplace=True):
        line.replace("dag_id", "'"+config['DagId']+"'")
        line.replace("scheduletoreplace", config['Schedule'])
        line.replace("querytoreplace", config['Query'])
        print(line, end="")

```

Now to generate our DAG files, we can either run this script ad-hoc or as part of our CI/CD workflow. After running the script, our final directory would look like the example below, where the `include/` directory contains the files shown above, and the `dags/` directory contains the two dynamically generated DAGs:

```bash
dags/
├── dag_file_1.py
├── dag_file_2.py
include/
├── dag-template.py
├── generate-dag-files.py
└── dag-config
    ├── dag1-config.json
    └── dag2-config.json
```

This is obviously a simple starting example that works only if all of the DAGs follow the same pattern. However, it could be expanded upon to have dynamic inputs for tasks, dependencies, different operators, etc.

## DAG Factory

A notable tool for dynamically creating DAGs from the community is [dag-factory](https://github.com/ajbosco/dag-factory). `dag-factory` is an open source Python library for dynamically generating Airflow DAGs from YAML files.

To use `dag-factory`, you can install the package in your Airflow environment and create YAML configuration files for generating your DAGs. You can then build the DAGs by calling the `dag-factory.generate_dags()` method in a Python script, like this example from the `dag-factory` README:

```python
from airflow import DAG
import dagfactory

dag_factory = dagfactory.DagFactory("/path/to/dags/config_file.yml")

dag_factory.clean_dags(globals())
dag_factory.generate_dags(globals())

```

## Scalability

Dynamically generating DAGs can cause performance issues when used at scale. Whether or not any particular method will cause problems is dependent on your total number of DAGs, your Airflow configuration, and your infrastructure. Here are a few general things to look out for:

- Any code in the `dags_folder` will be executed either every `min_file_processing_interval` or as fast as the dag file processor can, whichever is less frequent. Methods where that code is dynamically generating DAGs, such as the single-file method, are more likely to cause performance issues at scale.
- If you are reaching out to a database to create your DAGs (e.g. grabbing Variables from the metadata database), this means you will be querying quite frequently. Be conscious of your database's ability to handle such frequent connections and any costs you may incur per request from your data provider.
- To help with potential performance issues, you can increase the `min_file_processing_interval` to a much higher value. Consider this option if you know that your DAGs are not changing frequently and if you can tolerate some delay in the dynamic DAGs changing in response to the external source that generates them.

Upgrading to Airflow 2.0 to make use of the [HA Scheduler](https://www.astronomer.io/blog/airflow-2-scheduler) should help with these performance issues. But it can still take some additional optimization work depending on the scale you're working at. There is no single right way to implement or scale dynamically generated DAGs, but the flexibility of Airflow means there are many ways to arrive at a solution that works for a particular use case.

<!-- markdownlint-disable MD033 -->
### Dynamic DAGs in Action

<iframe src="https://fast.wistia.net/embed/iframe/1fkd7hcqfu" title="dynamic_dags_part_1 Video" allow="autoplay; fullscreen" allowtransparency="true" frameborder="0" scrolling="no" class="wistia_embed" name="wistia_embed" allowfullscreen msallowfullscreen width="100%" height="450"></iframe>

That was the easiest and fastest way for creating DAGs.

Now if you are looking for the better and scalable way to create DAGs dynamically, try out Astronomer's [Academy Course on Dynamic DAGs](https://academy.astronomer.io/dynamic-dags) for free today.

See you there! ❤️
