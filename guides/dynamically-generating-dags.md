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

In Airflow, [DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags) are defined as Python code; Airflow will execute all Python code in the `DAG_FOLDER`, and any `DAG` object that appears in `globals()` will be loaded. The simplest way of creating DAGs is to develop a static Python file for each one.

However, sometimes manually defining all DAGs isn't practical. Maybe you have hundreds or even thousands of DAGs that do similar things with just a parameter changing between them. Or maybe you know you need a set of DAGs to load tables, but those tables might change frequently and you don't want to manually manage the DAGs every time something changes. In these cases, and others, it can make more sense to dynamically generate DAGs. 

One of the great benefits of Airflow is that because everything is code, you have the full power of Python to define your DAGs in a way that works for you. As long as a `DAG` object in `globals()` is created by Python code that lives in the `DAG_FOLDER`, Airflow will load it. It follows that there are many ways in which you could dynamically generate DAGs; in this guide we will cover a few common patterns for doing so. We'll also discuss when dynamic generation is a good option, and some pitfalls to watch out for when doing this at scale.


## Single-File Methods

One pattern for dynamically generating DAGs is to have a single Python file which dynamically creates the DAGs based on some input parameter(s) (e.g. a list of APIs or tables). A common use case for this is an ETL or ELT type pipeline where there are many data sources or destinations resulting in many DAGs, but which all follow a similar pattern.

Benefits of single-file methods include:

- It's simple and easy to implement.
- It can accommodate input parameters from many different sources (see a few examples below).
- Adding DAGs is nearly instantaneous since it only requires changing the input parameters.

But, there are also drawbacks, including:

- Since a DAG file isn't actually being created, your visibility into the code behind any specific DAG is limited.
- Since this method requires a Python file in the `DAG_FOLDER` to dynamically generate the DAGs, the code will be executed on every scheduler heartbeat. This can cause performance issues if the total number of DAGs is large, or if the code is connecting to an external system such as a database. For more on this see the Scalability section below.

Below, we show a few different examples of how to implement this pattern using different input parameters for creating the DAGs.


### Create_DAG Method

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

With the code above, the input parameters can come from any source that the Python script can access. For this first example, we set a simple loop (`range(1, 4)`) to generate these unique parameters and pass them to the global scope, thereby registering them as valid DAGs to the Airflow scheduler. That code looks like this:

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

![title](https://assets.astronomer.io/website/img/guides/hello_world_1_thru_10.png)

### Example: Generate DAGs From Variables

Taking the above example a step further, as mentioned above, the input parameters don't have to exist in the DAG file itself. Another common form of generating DAGs is by setting values in a Variable object.

![title](https://assets.astronomer.io/website/img/guides/dag_number_var.png)

We can retrieve this value by importing the Variable class and passing it into our `range`. Because we want the interpreter to register this file as valid regardless of whether the variable exists, the `default_var` is set to 10.

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

If we look at the scheduler logs, we can see this variable is being pulled into the DAG and added an additional DAG to the DagBag based on the value.

![title](https://assets.astronomer.io/website/img/guides/dag_logs.png)

Then we can go to the Airflow UI and see all of the new DAGs that have been created.

![title](https://assets.astronomer.io/website/img/guides/hello_world_1_thru_15.png)

### Example: Generate DAGs From Connections

Another way to define input parameters that are used to dynamically create your DAGs is by defining Airflow connections. This can be a good option if each of your DAGs connects to a database or an API; since you will be setting up the connections anyway, creating the DAGs from that source avoids any redundant work. 

To implement this method, we can pull the connections we have in our Airflow metadata database by instantiating the "Session" and querying the "Connection" table. We can also filter this query so that it only pulls connections that match a certain criteria.

![title](https://assets.astronomer.io/website/img/guides/connections.png)

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

![title](https://assets.astronomer.io/website/img/guides/connection_dags.png)

We can see that all of the connections that match our filter have now been created as a unique DAG. The one connection we had which did not match (`SOME_OTHER_DATABASE`) has been ignored.

## Multiple-File Methods

Another pattern for dynamically generating DAGs is to use code to actually generate Python files for each DAG. The end result of this method is having one Python file per DAG in your `DAG_FOLDER`, but rather than manually create all the files, they are dynamically generated from some external script. 

One way of implementing this method in production is to have a Python script that generates DAG files, which gets executed as part of a CI/CD workflow. The DAGs get generated during the CI/CD build and then deployed to Airflow. You could also have another DAG that runs the generation script periodically.

Some benefits of this method include:

- It's more scalable than single-file methods. Because the DAG files aren't being generated by parsing code in the `DAG_FOLDER`, the DAG generation code isn't executed on every scheduler heartbeat. 
- Since DAG files are being explicitly created before deploying to Airflow, you have full visibility into the DAG code.

On the other hand, drawbacks of this method include:

- It can be complex to set up.
- Changes to DAGs or additional DAGs won't be generated until the script is run, which in some cases requires a deployment.

Below we'll show a simple example of how this method could be implemented.

### Example: Generate DAGs From JSON Config Files

One way of implementing a multiple-file method is using a Python script to generate DAG files based on a set of JSON configuration files. For this simple example, we will assume that all DAGs will have the same structure; each will have a single task that uses the `PostgresOperator` to execute a query. This use case might be relevant for a team of analysts who need to schedule SQL queries, where the DAG is mostly the same, but the query and the schedule are changing.

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

Now to generate our DAG files, we can either run this script ad-hoc, as part of our CI/CD workflow, or we could create another DAG that would run it periodically. After running the script, our final directory would look like the example below, where the `include/` directory contains the files shown above, and the `dags/` directory contains the two dynamically generated DAGs:

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

This is obviously a simple starting example that only works if all of the DAGs follow the same pattern. However, it could be expanded to allow for even more dynamic inputs to define more tasks, dependencies, different operators, etc.

## DAG Factory

A notable implementation of dynamically creating DAGs from the community is [dag-factory](https://github.com/ajbosco/dag-factory). `dag-factory` is an open source Python library for dynamically generating Airflow DAGs from YAML files.

To use `dag-factory` you can install the package in your Airflow environment, and then create YAML configuration files that will provide the specifics of your DAGs. You can then build the DAGs by calling the `dag-factory.generate_dags()` method in a Python script, like this example from the `dag-factory` README:

```python
from airflow import DAG
import dagfactory

dag_factory = dagfactory.DagFactory("/path/to/dags/config_file.yml")

dag_factory.clean_dags(globals())
dag_factory.generate_dags(globals())

```

## Scalability

As mentioned above, sometimes dynamically generating DAGs can cause performance issues when used at scale. Whether or not any particular method will cause problems is highly dependent on the total number of DAGs and your Airflow configuration and infrastructure. Here are a few general things to look out for:

- Any code in the `DAG_FOLDER` will be executed on every scheduler heartbeat. Methods where code in that folder is what is dynamically generating DAGs, like described in the Single-File Methods section, are more likely to cause performance issues at scale.
- If the DAG parsing time (i.e. the time to parse all code in the `DAG_FOLDER`) is greater than the scheduler heartbeat interval, the scheduler can get locked up and tasks won't be executed. If you are dynamically generating DAGs and tasks aren't running, this is a good metric to review to start troubleshooting. 

In general, upgrading to Airflow 2.0 to make use of the [HA Scheduler](https://www.astronomer.io/blog/airflow-2-scheduler) should help with performance issues. But, note that it can still take some optimization work depending on the scale of the dynamic DAGs. There is no single right way to implement or scale dynamically generated DAGs, but the flexibility of Airflow means there are many ways to arrive at a solution that works for a particular use case.
