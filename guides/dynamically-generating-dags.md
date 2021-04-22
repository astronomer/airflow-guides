---
title: "Dynamically Generating DAGs in Airflow"
description: "Using a base DAG template to create multiple DAGs."
date: 2018-05-21T00:00:00.000Z
slug: "dynamically-generating-dags"
heroImagePath: "https://assets.astronomer.io/website/img/guides/dynamicdags.png"
tags: ["DAGs", "Best Practices"]
---
## Overview
In Airflow, [DAGs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#dags) are defined as Python code; Airflow will execute all Python code in the `DAG_FOLDER`, and any `DAG` object that appears in `globals()` will be loaded. The simplest and probably most common way of creating DAGs is to develop a Python file for each one.

However, sometimes manually defining all DAGs isn't practical. Maybe you have hundreds or even thousands of DAGs that do similar things with just a parameter changing between them. Or maybe you know you need a set of DAGs to load tables, but those tables might change frequently and you don't want to manually manage the DAGs every time something changes. In these cases, and others, it can make more sense to dynamically generate DAGs. 

One of the great benefits of Airflow is that because everything is code, you have the full power of Python to define your DAGs in a way that works for you. As long as a `DAG` object is created by Python code that lives in the `DAG_FOLDER`, Airflow will load it. It follows that there are many ways in which you could dynamically generate DAGs; in this guide we will cover a few common patterns for doing so. We'll also discuss when dynamic generation is a good option, and some pitfalls to watch out for when doing this at scale.


## Single-File Methods
One pattern for dynamically generating DAGs is to have a single Python file which dynamically creates the DAGs based on some external criteria (e.g. a list of APIs or database tables). A common use case for this is an ETL or ELT type pipeline where there are many data sources or destinations resulting in many DAGs, but which all follow a similar pattern.

Benefits of single-file methods include:
 - It's simple and easy to implement.
 - It can accomodate external criteria from many different sources (see examples below).
 - Adding or removing DAGs is nearly instantaneous since it only requires changing the external criteria.

But, there are also drawbacks, including:
 - Since a DAG file isn't actually being created, your visibility into the code behind that specific DAG is limited.
 - There can be performance issues with this method when scaled; for more on this see the Scalability section below.

Below, we show a few different examples of how to implement this pattern using different criteria sources for creating the DAGs.

### Generate DAGs From Input Parameter

Multiple DAGs can be registered from the same file, but to improve maintainability and avoid namespace conflicts, it is advisable to keep one file per one unique DAG. However, if multiple unique DAGs are required with the same base code, it is possible to create these DAGs dynamically based on any number of configuration parameters.



#### Create_DAG Method

To create new dags, we're going to create a dag template within the `create_dag` function. The code here is almost identical to the previous code above when only one dag was being created but now it is wrapped in a method that allows for custom parameters to be passed in.

```python
from datetime import datetime

from airflow import DAG

from airflow.operators.python_operator import PythonOperator


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

We can then set a simple loop (`range(1, 10)`) to generate these unique parameters and pass them to the global scope, thereby registering them as valid DAGs to the Airflow scheduler.

```python
from datetime import datetime

from airflow import DAG

from airflow.operators.python_operator import PythonOperator


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


# build a dag for each number in range(10)
for n in range(1, 10):
    dag_id = 'hello_world_{}'.format(str(n))

    default_args = {'owner': 'airflow',
                    'start_date': datetime(2018, 1, 1)
                    }

    schedule = '@daily'

    dag_number = n

    globals()[dag_id] = create_dag(dag_id,
                                  schedule,
                                  dag_number,
                                  default_args)
```

![title](https://assets.astronomer.io/website/img/guides/hello_world_1_thru_10.png)

### Generate DAGs From Variables

Taking the above example a step further, the input parameters don't have to exist in the DAG file itself. Another common form of generating dags is by setting values in a Variable object.

![title](https://assets.astronomer.io/website/img/guides/dag_number_var.png)

We can retrieve this value by importing the Variable class and passing it into our `range`. Because we want the interpreter to register this file as valid regardless of whether the variable exists, the `default_var` is set to 10.

```python
from datetime import datetime

from airflow import DAG
from airflow.models import Variable

from airflow.operators.python_operator import PythonOperator


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


number_of_dags = Variable.get('dag_number', default_var=10)
number_of_dags = int(number_of_dags)

for n in range(1, number_of_dags):
    dag_id = 'hello_world_{}'.format(str(n))

    default_args = {'owner': 'airflow',
                    'start_date': datetime(2018, 1, 1)
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

Then we can go to the main UI and see all of the new DAGs that have been created.

![title](https://assets.astronomer.io/website/img/guides/hello_world_1_thru_15.png)

### Generate DAGs From Connections

Creating DAGs based on a variable or set of variables is a very powerful feature of Airflow. But what if we want our number of DAGs to correspond to the number of connections (to an API, database, etc.) that are created in the "Connections" tab? In that case, we wouldn't want to have to create an additional variable unnecessarily every time we made a new connection -- that would be redundant.

Instead, we can pull the connections we have in our database by instantiating the "Session" and querying the "Connection" table. We can even filter our query so that this only pulls connections that match a certain criteria.

![title](https://assets.astronomer.io/website/img/guides/connections.png)

```python
from datetime import datetime

from airflow import DAG, settings
from airflow.models import Connection

from airflow.operators.python_operator import PythonOperator


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


session = settings.Session()

conns = (session.query(Connection.conn_id)
                .filter(Connection.conn_id.ilike('%MY_DATABASE_CONN%'))
                .all())

for conn in conns:
    dag_id = 'hello_world_{}'.format(conn[0])

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
Another pattern for dynamically generating DAGs is to 

## Scalability