---
title: "Using Airflow Datastores"
description: "Use Apache Airflow's internal datastores to build more powerful DAGs"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-datastores"
heroImagePath: "https://assets.astronomer.io/website/img/guides/datastores.png"
tags: ["Datastores", "Airflow"]
---

_Built in methods of storing data._

In theory, all data processing and storage should be done in external systems with Airflow only containing workflow metadata.

In practice, this is much easier said than done. Depending on the architecture Airflow is running on, certain data stores may be more reliable than others.

Balance between what processing Airflow does and what processing is done by something else should depend on the setup and available tools—there’s no hard and fast rule.

## Variables and XComs

_Static and Dynamic information stores_

### XComs

_Cross Communication_

XComs, or short for "cross communication" are stores of key, value, and timestamps meant to communicate between tasks. XComs are stored in Airflow's metadata database with an associated `execution_date`, `TaskInstance` and `DagRun`.

XComs can be "pushed" or "pulled" by all TaskInstances (by using `xcom_push()` or `xcom_pull()`, respectively).

All values that are returned by an Operator's `execute()` method, or from a PythonOperator's `python_callable` are pushed to XCom.

```python
def generate_values(**kwargs):
    values = list(range(0, 100000))
    return values

with dag:

    t1 = PythonOperator(
        task_id='push_values',
        python_callable=generate_values,
        provide_context=True)
```

_**What gets pushed to XCom?**_

Information about where to pull the xcom value from is found in the task's context.

```python
def manipulate_values(**kwargs):
    ti = kwargs['ti']
    v1 = ti.xcom_pull(key=None, task_ids='push_values')

    return [x / 2 for x in v1]
...
t2 = PythonOperator(
        task_id='pull_values',
        python_callable=manipulate_values,
        provide_context=True)
```

### Variables

_Static Values_

Similar to XComs, Variables are key-value stores in Airflow's metadata database. However, Variables are just key-value stores - they don't store the "conditions" (`execution_date`, `TaskInstance`, etc.) that led to a value being produced.

Variables can be pushed and pulled in a similar fashion to `XComs`:

```python
config = Variable.get("db_config")

set_confg = Variable.set(db_config)
```

Variables can also be created from the UI.

![variable_ui](https://assets.astronomer.io/website/img/guides/variable_ui.png)

**Note:** Although variables are fernet key encrypted in the database, they are accessible in the UI and therefore should not be used to store passwords or other sensitve data.

### When to use each

In general - since XComs are meant to be used to communicate between tasks, and store the "conditions" that led to that value being created, they should be used for values that are going to be changing each time a workflow runs.

Variables on the other hand are much more natural places for constants like a list of tables that need to be synced, a configuration file that needs to be pulled from, or a list of IDs to dynamically generate tasks from.

Both can be very powerful where appropriate, but can also be dangerous if misused.

## Manipulating XCom Data

_Everything is stored in the database._

In the example above - XCom values can be seen for every task.

![task_instance](https://assets.astronomer.io/website/img/guides/xcom_push.png)

Under "View Logs"
![view_xcom](https://assets.astronomer.io/website/img/guides/xcom_encrypt.png)

**Note:** Encryption and character settings may show misleading values in the UI. However, the values will be preserverd when working with them:

![view_xcom](https://assets.astronomer.io/website/img/guides/xcom_pull_logs.png)

XCom data can be deleted straight from the database.

## Generating DAGs from Variables

Variables can be used as static value stores to generate DAGs from config files.

Define the variable:

```json
[{
  "table": "users",
  "schema":"app_one",
 "s3_bucket":"etl_bucket",
 "s3_key":"app_one_users",
 "redshift_conn_id":"postgres_default" },
 {
   "table": "users",
   "schema":"app_two",
 "s3_bucket":"etl_bucket",
 "s3_key":"app_two_users",
 "redshift_conn_id":"postgres_default"}]
 ```

<br>
Call the Variable in the dag file
<br>

```python
sync_config = json.loads(Variable.get("sync_config"))

with dag:
    start = DummyOperator(task_id='begin_dag')
    for table in sync_config:
        d1 = RedshiftToS3Transfer(
            task_id='{0}'.format(table['s3_key']),
            table=table['table'],
            schema=table['schema'],
            s3_bucket=table['s3_bucket'],
            s3_key=table['s3_key'],
            redshift_conn_id=table['redshift_conn_id']
        )
        start >> d1
```

![variable_dag](img/variable_dag.png)

This can be an especially powerful method of defining any database sync workflows - the first step in the DAG can generate a list of tables and schemas with their corresponding transformation, and downstream tasks can perform the necessary queries.
