---
title: "Cross-DAG Dependencies"
description: "How to implement dependencies between your Airflow DAGs."
date: 2021-06-07T00:00:00.000Z
slug: "cross-dag-dependencies"
tags: ["DAGs", "Subdags", "Dependencies", "Sensors", "Dataset"]
---

When designing Airflow DAGs, it is often best practice to put all related tasks in the same DAG. However, it's sometimes necessary to create dependencies between your DAGs. In this scenario, one node of a DAG is its own complete DAG, rather than just a single task. Throughout this guide, we'll use the following terms to describe DAG dependencies:

- Upstream DAG: A DAG that must reach a specified state before a downstream DAG can run
- Downstream DAG: A DAG that cannot run until an upstream DAG reaches a specified state

According to the Airflow documentation on [cross-DAG dependencies](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/external_task_sensor.html#cross-dag-dependencies), designing DAGs in this way can be useful when:

- A DAG should only run after one or more datasets have been updated by tasks in other DAGs.
- Two DAGs are dependent, but they have different schedules.
- Two DAGs are dependent, but they are owned by different teams.
- A task depends on another task but for a different execution date.

For any scenario where you have dependent DAGs, we've got you covered! In this guide, we'll discuss multiple methods for implementing cross-DAG dependencies, including how to implement dependencies if your dependent DAGs are located in different Airflow deployments.

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/cross-dag-dependencies-tutorial).

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- Dependencies in Airflow. See [Managing Dependencies in Apache Airflow](https://www.astronomer.io/guides/managing-dependencies/).
- Airflow DAGs. See [Introduction to Airflow DAGs](https://www.astronomer.io/guides/dags/).
- Airflow operators. See [Operators 101](https://www.astronomer.io/guides/what-is-an-operator/).
- Airflow sensors. See [Sensors 101](https://www.astronomer.io/guides/what-is-a-sensor/).

## Implementing Cross-DAG Dependencies

There are multiple ways to implement cross-DAG dependencies in Airflow, including:

- [Dataset driven scheduling](https://www.astronomer.io/guides/airflow-datasets/).
- The [TriggerDagRunOperator](https://registry.astronomer.io/providers/apache-airflow/modules/triggerdagrunoperator).
- The [ExternalTaskSensor](https://registry.astronomer.io/providers/apache-airflow/modules/externaltasksensor).
- The [Airflow API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html).

In this section, we detail how to use each method and ideal scenarios for each, as well as how to view dependencies in the Airflow UI.

> **Note:** It can be tempting to use SubDAGs to handle DAG dependencies, but we highly recommend against doing so as SubDAGs can create performance issues. Instead, use one of the other methods described below.

### Dataset dependencies

In Airflow 2.4+, you can use datasets to create data-driven dependencies between DAGs. This means that DAGs which access the same data can have explicit, visible relationships, and DAGs can be scheduled based on updates to this data.

You should use this method if you have a downstream DAG that should only run after a dataset has been updated by an upstream DAG, especially if those updates can be very irregular. This type of dependency also provides you with increased observability into the dependencies between your DAGs and datasets in the Airflow UI.

Using datasets requires knowledge of the following scheduling concepts:

- **Producing task**: A task that updates a specific dataset, defined by its `outlets` parameter.
- **Consuming DAG**: A DAG that will run as soon as a specific dataset(s) are updated.

Any task can be made into a producing task by providing one or more datasets to the `outlets` parameter as shown below.

```python
dataset1 = Dataset('s3://folder1/dataset_1.txt')

# producing task in the upstream DAG
EmptyOperator(
    task_id="producing_task",
    outlets=[dataset1]  # flagging to Airflow that dataset1 was updated
)
```

The downstream DAG is scheduled to run after `dataset1` has been updated by providing it to the `schedule` parameter.

```python
dataset1 = Dataset('s3://folder1/dataset_1.txt')

# consuming DAG
with DAG(
    dag_id='consuming_dag_1',
    catchup=False,
    start_date=datetime.datetime(2022, 1, 1),
    schedule=[dataset1]
) as dag:
```

In the Airflow UI, the **Next Run** column for the downstream DAG shows how many datasets the DAG depends on and how many of those have been updated since the last DAG run. The screenshot below shows that the DAG `dataset_dependent_example_dag` runs only after two different datasets have been updated. One of those datasets has already been updated by an upstream DAG.

![DAG Dependencies View](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/2_4_DatasetDependentDAG.png)

Check out the [Datasets and Data Driven Scheduling in Airflow](https://www.astronomer.io/guides/airflow-datasets/) guide to learn more and see an example implementation of this feature.

### TriggerDagRunOperator

The TriggerDagRunOperator is an easy way to implement cross-DAG dependencies from the upstream DAG. This operator allows you to have a task in one DAG that triggers another DAG in the same Airflow environment. Read more in-depth documentation about this operator on the [Astronomer Registry](https://registry.astronomer.io/providers/apache-airflow/modules/triggerdagrunoperator).

You can trigger a downstream DAG with the TriggerDagRunOperator from any point in the upstream DAG. If you set the operator's  `wait_for_completion` parameter to `True`, the upstream DAG will pause and resume only once the downstream DAG has finished running.

A common use case for this implementation is when an upstream DAG fetches new testing data for a machine learning pipeline, runs and tests a model, and publishes the model's prediction. In case of the model underperforming, the TriggerDagRunOperator is used to kick off a separate DAG that retrains the model while the upstream DAG waits. Once the model is retrained and tested by the downstream DAG, the upstream DAG resumes and publishes the new model's results.

Below is an example DAG that implements the TriggerDagRunOperator to trigger the `dependent-dag` between two other tasks. The `trigger-dagrun-dag` will wait until `dependent-dag` has finished its run until it moves onto running `end_task`, since `wait_for_completion` in the `TriggerDagRunOperator` has been set to `True`.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

def print_task_type(**kwargs):
    """
    Dummy function to call before and after dependent DAG.
    """
    print(f"The {kwargs['task_type']} task has completed.")

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'trigger-dagrun-dag',
    start_date=datetime(2021, 1, 1),
    max_active_runs=1,
    schedule_interval='@daily',
    default_args=default_args,
    catchup=False
) as dag:

    start_task = PythonOperator(
        task_id='starting_task',
        python_callable=print_task_type,
        op_kwargs={'task_type': 'starting'}
    )

    trigger_dependent_dag = TriggerDagRunOperator(
        task_id="trigger_dependent_dag",
        trigger_dag_id="dependent-dag",
        wait_for_completion=True
    )

    end_task = PythonOperator(
        task_id='end_task',
        python_callable=print_task_type,
        op_kwargs={'task_type': 'ending'}
    )

    start_task >> trigger_dependent_dag >> end_task
```

In the following graph view, you can see that the `trigger_dependent_dag` task in the middle is the TriggerDagRunOperator, which runs the `dependent-dag`.

![Trigger DAG Graph](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/trigger_dag_run_graph.png)

Note that if your dependent DAG requires a config input or a specific execution date, these can be specified in the operator using the `conf` and `execution_date` params respectively.

### ExternalTaskSensor

To create cross-DAG dependencies from a downstream DAG, consider using one or more [ExternalTaskSensors](https://registry.astronomer.io/providers/apache-airflow/modules/externaltasksensor). The downstream DAG will pause until a task is completed in the upstream DAG before resuming.

This method of creating cross-DAG dependencies is especially useful when you have a downstream DAG with different branches that depend on different tasks in one or more upstream DAGs. Instead of defining an entire DAG as being downstream of another DAG like with datasets, you can set a specific task in a downstream DAG to wait for a task to finish in an upstream DAG.

For example, you could have upstream tasks modifying different tables in a data warehouse and one downstream DAG running one branch of data quality checks for each of those tables. You can use one ExternalTaskSensor at the start of each branch to make sure that the checks running on each table only start, once the update to that specific table has finished.

> **Note**: In Airflow 2.2+, a deferrable version of the ExternalTaskSensor is available, the [ExternalTaskSensorAsync](https://registry.astronomer.io/providers/astronomer-providers/modules/externaltasksensorasync). For more info on deferrable operators and their benefits, see [this guide](https://www.astronomer.io/guides/deferrable-operators/)

An example DAG using three ExternalTaskSensors at the start of three parallel branches in the same DAG is shown below.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

def downstream_function_branch_1():
    print('Upstream DAG 1 has completed. Starting tasks of branch 1.')

def downstream_function_branch_2():
    print('Upstream DAG 2 has completed. Starting tasks of branch 2.')

def downstream_function_branch_3():
    print('Upstream DAG 3 has completed. Starting tasks of branch 3.')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'external-task-sensor-dag',
    start_date=datetime(2022, 8, 1),
    max_active_runs=3,
    schedule='*/1 * * * *',
    catchup=False
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    ets_branch_1 = ExternalTaskSensor(
        task_id="ets_branch_1",
        external_dag_id='upstream_dag_1',
        external_task_id='my_task',
        allowed_states=['success'],
        failed_states=['failed', 'skipped']
    )

    task_branch_1 = PythonOperator(
        task_id='task_branch_1',
        python_callable=downstream_function_branch_1,
    )

    ets_branch_2 = ExternalTaskSensor(
        task_id="ets_branch_2",
        external_dag_id='upstream_dag_2',
        external_task_id='my_task',
        allowed_states=['success'],
        failed_states=['failed', 'skipped']
    )

    task_branch_2 = PythonOperator(
        task_id='task_branch_2',
        python_callable=downstream_function_branch_2,
    )

    ets_branch_3 = ExternalTaskSensor(
        task_id="ets_branch_3",
        external_dag_id='upstream_dag_3',
        external_task_id='my_task',
        allowed_states=['success'],
        failed_states=['failed', 'skipped']
    )

    task_branch_3 = PythonOperator(
        task_id='task_branch_3',
        python_callable=downstream_function_branch_3,
    )

    start >> [ets_branch_1, ets_branch_2, ets_branch_3]

    ets_branch_1 >> task_branch_1
    ets_branch_2 >> task_branch_2
    ets_branch_3 >> task_branch_3

    [task_branch_1, task_branch_2, task_branch_3] >> end
```

In this DAG

- `ets_branch_1` waits for the `my_task` task of `upstream_dag_1` to complete before moving on to execute `task_branch_1`.
- `ets_branch_2` waits for the `my_task` task of `upstream_dag_2` to complete before moving on to execute `task_branch_2`.
- `ets_branch_3` waits for the `my_task` task of `upstream_dag_3` to complete before moving on to execute `task_branch_3`.

These processes happen in parallel and independent of each other. The graph view shows the state of the DAG after `my_task` in `upstream_dag_1` has finished which caused `ets_branch_1` and `task_branch_1` to run. `ets_branch_2` and `ets_branch_3` are still waiting for their upstream tasks to finish.

![ExternalTaskSensor 3 Branches](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/2_4_external_task_sensor_graph_3_branches.png)

If you want the downstream DAG to wait for the entire upstream DAG to finish instead of a specific task, you can set the `external_task_id` to `None`. In the example above, we specify that the external task must have a state of `success` for the downstream task to succeed, as defined by the `allowed_states` and `failed_states`.

Also note that in the example above, the upstream DAG (`example_dag`) and downstream DAG (`external-task-sensor-dag`) must have the same start date and schedule interval. This is because the ExternalTaskSensor will look for completion of the specified task or DAG at the same `logical_date` (previously called `execution_date`). To look for completion of the external task at a different date, you can make use of either of the `execution_delta` or `execution_date_fn` parameters (these are described in more detail in the documentation linked above).

### Airflow API

The [Airflow API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html) is another way of creating cross-DAG dependencies. This is especially useful in [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0), which has a fully stable REST API. To use the API to trigger a DAG run, you can make a POST request to the `DAGRuns` endpoint as described in the [Airflow API documentation](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run).

This method is useful if your dependent DAGs live in different Airflow environments (more on this in the Cross-Deployment Dependencies section below). The task triggering the downstream DAG will complete once the API call is complete.

Using the API to trigger a downstream DAG can be implemented within a DAG by using the [SimpleHttpOperator](https://registry.astronomer.io/providers/http/modules/simplehttpoperator) as shown in the example DAG below:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime, timedelta
import json

# Define body of POST request for the API call to trigger another DAG
date = '{{ execution_date }}'
request_body = {
  "execution_date": date
}
json_body = json.dumps(request_body)

def print_task_type(**kwargs):
    """
    Dummy function to call before and after downstream DAG.
    """
    print(f"The {kwargs['task_type']} task has completed.")
    print(request_body)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'api-dag',
    start_date=datetime(2021, 1, 1),
    max_active_runs=1,
    schedule_interval='@daily',
    catchup=False
) as dag:

    start_task = PythonOperator(
        task_id='starting_task',
        python_callable=print_task_type,
        op_kwargs={'task_type': 'starting'}
    )

    api_trigger_dependent_dag = SimpleHttpOperator(
        task_id="api_trigger_dependent_dag",
        http_conn_id='airflow-api',
        endpoint='/api/v1/dags/dependent-dag/dagRuns',
        method='POST',
        headers={'Content-Type': 'application/json'},
        data=json_body
    )

    end_task = PythonOperator(
        task_id='end_task',
        python_callable=print_task_type,
        op_kwargs={'task_type': 'ending'}
    )

    start_task >> api_trigger_dependent_dag >> end_task
```

This DAG has a similar structure to the TriggerDagRunOperator DAG above, but instead uses the SimpleHttpOperator to trigger the `dependent-dag` using the Airflow API. The graph view looks like this:

![API Graph View](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/api_graph.png)

In order to use the SimpleHttpOperator to trigger another DAG, you need to define the following:

- `endpoint`: This should be of the form `'/api/v1/dags/<dag-id>/dagRuns'` where `<dag-id>` is the ID of the DAG you want to trigger.
- `data`: To trigger a DAG run using this endpoint, you must provide an execution date. In the example above, we use the `execution_date` of the upstream DAG, but this can be any date of your choosing. You can also specify other information about the DAG run as described in the API documentation linked above.
- `http_conn_id`: This should be an [Airflow connection](https://www.astronomer.io/guides/connections/) of [type HTTP](https://airflow.apache.org/docs/apache-airflow-providers-http/stable/connections/http.html), with your Airflow domain as the Host. Any authentication should be provided either as a Login/Password (if using Basic auth) or as a JSON-formatted Extra. In the example below, we use an authorization token.

![Http Connection](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/http_connection.png)

## DAG Dependencies View

In [Airflow 2.1](https://airflow.apache.org/docs/apache-airflow/stable/changelog.html#airflow-2-1-0-2021-05-21), a new cross-DAG dependencies view was added to the Airflow UI. This view shows all dependencies between DAGs in your Airflow environment as long as they are implemented using one of the following methods:

- Using dataset driven scheduling
- Using a TriggerDagRunOperator
- Using an ExternalTaskSensor

Dependencies can be viewed in the UI by going to **Browse** → **DAG Dependencies** or by clicking on the **Graph** button from within the Datasets tab. The screenshot below shows the dependencies created by the TriggerDagRunOperator and ExternalTaskSensor example DAGs in the sections above.

![DAG Dependencies View](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/dag_dependencies_view.png)

When DAGs are scheduled depending on datasets, both the DAG containing the producing task, as well as the dataset itself will be shown upstream of the consuming DAG.

![DAG Dependencies View Datasets](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/2_4_CrossGuide_Dependencies.png)

In Airflow 2.4 an additional **Datasets** tab was added, which shows all dependencies between datasets and DAGs.

![DAG Dependencies View Datasets](https://assets2.astronomer.io/main/guides/cross-dag-dependencies/2_4_Datasets.png)

## Cross-Deployment Dependencies

It is sometimes necessary to implement cross-DAG dependencies where the DAGs do not exist in the same Airflow deployment. The TriggerDagRunOperator, ExternalTaskSensor, and dataset methods described above are designed to work with DAGs in the same Airflow environment, so they are not ideal for cross-Airflow deployments. The Airflow API, on the other hand, is perfect for this use case. In this section, we'll focus on how to implement this method on Astro, but the general concepts will likely be similar wherever your Airflow environments are deployed.

### Cross-Deployment Dependencies with Astronomer

To implement cross-DAG dependencies on two different Airflow environments on Astro, we can follow the same general steps for triggering a DAG using the Airflow API described above. It may be helpful to first read our documentation on [making requests to the Airflow API](https://docs.astronomer.io/software/airflow-api) from Astronomer. When you're ready to implement a cross-deployment dependency, follow these steps:

1. In the upstream DAG, create a SimpleHttpOperator task that will trigger the downstream DAG. Refer to the section above for details on configuring the operator.
2. In the downstream DAG Airflow environment, [create a Service Account](https://docs.astronomer.io/software/ci-cd#step-1-create-a-service-account) and copy the API key.
3. In the upstream DAG Airflow environment, create an Airflow connection as shown in the Airflow API section above. The Host should be `https://<your-base-domain>/<deployment-release-name>/airflow` where the base domain and deployment release name are from your downstream DAG's Airflow deployment. In the Extras, use `{"Authorization": "api-token"}` where `api-token` is the service account API key you copied in step 2.
4. Ensure the downstream DAG is turned on, then run the upstream DAG.
