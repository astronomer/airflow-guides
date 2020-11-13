---
title: "Dynamically Generating DAGs in Airflow"
description: "Using a base DAG template to create multiple DAGs."
date: 2018-05-21T00:00:00.000Z
slug: "dynamically-generating-dags"
heroImagePath: "https://assets.astronomer.io/website/img/guides/dynamicdags.png"
tags: ["DAGs", "Best Practices"]
---
The simplest way of creating a DAG in Airflow is to define it in the DAGs folder. Anything with a .py suffix will be scanned to see if it contains the definition of a new DAG.

```python
from datetime import datetime

from airflow import DAG

from airflow.operators.python_operator import PythonOperator

default_args = {'owner': 'airflow',
                'start_date': datetime(2018, 1, 1)
               }

dag = DAG('hello_world',
          schedule_interval='@daily',
          default_args=default_args,
          catchup=False)


def hello_world_py():
    print('Hello World')


with dag:
    t1 = PythonOperator(
        task_id='hello_world',
        python_callable=hello_world_py)
```

![title](https://assets.astronomer.io/website/img/guides/hello_world.png)

## Add DAGs dynamically based on input parameter

Multiple DAGs can be registered from the same file, but to improve maintainability and avoid namespace conflicts, it is advisable to keep one file per one unique DAG. However, if multiple unique DAGs are required with the same base code, it is possible to create these DAGs dynamically based on any number of configuration parameters.

A common use case for this is when pulling data from multiple APIs or database that have a similar incoming structure, require similar transform logic, and need to be loaded according to a similar pattern.

### Create_DAG method

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

## Adding DAGs based on Variable value

Taking this a step further, the input parameters don't have to exist in the dag file itself. Another common form of generating dags is by setting values in a Variable object.

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

## Adding DAGs based on Connections

Creating DAGs based on a varible or set of variables is a very powerful feature of Airflow. But what if we want our number of DAGs to correspond to the number of connections (to an API, database, etc.) that are created in the "Connections" tab? In that case, we wouldn't want to have to create an additional variable uncessarily every time we made a new connection -- that would be redundant.

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
