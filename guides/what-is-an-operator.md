---
title: "Operators 101"
description: "An introduction to Operators in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-an-operator"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "Basics"]
---

## Operators

Operators are the main building blocks of Airflow DAGs. They are classes that encapsulate logic to do a unit of work.

When you create an instance of an operator in a DAG and provide it with it's required parameters, it becomes a task. Many tasks can be added to a DAG along with their dependencies. When Airflow executes that task for a given `execution_date`, it becomes a task instance.


### BashOperator

```Python
t1 = BashOperator(
        task_id='bash_hello_world',
        dag=dag,
        bash_command='echo "Hello World"'
        )
```

This `BashOperator` simply runs a bash command and echos "Hello World"

[BashOperator Code](https://github.com/apache/airflow/blob/master/airflow/operators/bash_operator.py)

### Python Operator

```python
def hello(**kwargs):
    print('Hello from {kw}'.format(kw=kwargs['my_keyword']))

t2 = PythonOperator(
        task_id='python_hello',
        dag=dag,
        python_callable=hello,
        op_kwargs={'my_keyword': 'Airflow'}
        )
```

The `PythonOperator` will call a python function defined earlier in our code. You can pass parameters to the function via the `op_kwargs` parameter. This task will print "Hello from Airflow" when it runs.

[PythonOperator Code](https://github.com/apache/airflow/blob/master/airflow/operators/python_operator.py)

### Postgres Operator

```python
t3 = PostgresOperator(
        task_id='PythonOperator',
        sql='CREATE TABLE my_table (my_column varchar(10));',
        postgres_conn_id='my_postgres_connection',
        autocommit=False
    )
```

This operator will issue a sql statement against a postgres database. Credentials for the database are stored in an airflow connection called `my_postgres_connection`. If you look at the code for the `PostgresOperator`, it uses a `PostgresHook` to actually interact with the database.

[PostgresOperator](https://github.com/apache/airflow/blob/master/airflow/operators/postgres_operator.py)

### SSH Operator

```python
t4 = SSHOperator(
        task_id='SSHOperator',
        ssh_conn_id='my_ssh_connection',
        command='echo "Hello from SSH Operator"'
    )
```

Like the `BashOperator`, the `SSHOperator` allows you to run a bash command, but has built in support to ssh into a remote machine to run commands there.

The private key to authenticate to the remote server is stored in Airflow Connections as `my_ssh_conenction`. This key can be referred to in all DAGs, so the operator itself only needs the command you want to run. This operator uses an `SSHHook` to establish the ssh connection and run the command.

[SSHOperator Code](https://github.com/apache/airflow/blob/master/airflow/contrib/operators/ssh_operator.py)

### S3 To Redshift Operator

```python
t5 = S3ToRedshiftTransfer(
        task_id='S3ToRedshift',
        schema='public',
        table='my_table',
        s3_bucket='my_s3_bucket',
        s3_key='{{ ds_nodash }}/my_file.csv',
        redshift_conn_id='my_redshift_connection',
        aws_conn_id='my_aws_connection'
    )
```

This operator loads data from S3 to Redshift via Redshift's COPY command. This is in a family of operators called `Transfer Operators` - operators designed to move data from one system (S3) to another (Redshift). Notice it has two Airflow connections in the parameters, one for Redshift and one for S3.

This also uses another concept - [macros and templates](https://www.astronomer.io/guides/templating/). In the `s3_key` parameter, jinja template notation is used to pass in the execution date for this DAG Run formatted as a string with no dashes (`ds_nodash` - a predefined macro in Airflow). It will look for a key formatted similarly to `my_s3_bucket/20190711/my_file.csv`, with the timestamp dependent on when the file ran. 

 Templates can be used to determine runtime parameters (e.g. the range of data for an API call) and also make your code idempotent (each intermediary file is named for the data range it contains).

[S3ToRedshiftTransfer Code](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/operators/s3_to_redshift.html)

