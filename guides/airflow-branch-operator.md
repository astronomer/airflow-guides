---
title: "Using BranchOperator in Airflow"
description: "Use Apache Airflow's BranchOperator to execute conditional branches in your workflow"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-branch-operator"
heroImagePath: null
tags: ["Building DAGs", "BranchOperator", "Airflow"]
---

[Apache Airflow's BranchOperator](https://airflow.apache.org/code.html#operator-api) is a great way to execute conditional branches in your workflow.

These can be used for safety checks, notifications, etc.

At it's core, a BranchOperator is just a PythonOperator that returns the next task to be executed.

In the past, Astronomer has used it to make requests to a IP-geolocation API when there has been at least 500 new visits to a website to get around API call restrictions and other such use cases.

https://airflow.incubator.apache.org/concepts.html?highlight=branch#branching

_This example will show executing a set of steps based on the results of a query._

```py
"""
BranchOperator.

Can be used for safety checks or notifications.

This was written when we were having issues with the Bing/Google Ads APIs. Lack of data would lead to
inaccurate downstream aggregations.

Astronomer related logic was taken out and replaced with Dummy tasks.
"""

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2017, 7, 31),
    'email': ['viraj@astronomer.io'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

# instantiate dag
dag = DAG(dag_id='check_api_runs',
          default_args=default_args,
          schedule_interval='0 10 * * *')


def get_recent_date():
    """
    Python function that grabs the latest date from 3 data sources from internal reporting.
    The rest of the DAG does not execute unless each one has successfully run.
    """

    bing_date = PostgresHook('astro_redshift').get_pandas_df(
        """ SELECT max(gregorian_date) FROM dev.aa_bing_ads.conversion;""")['max'][0]
    google_date = PostgresHook('astro_redshift').get_pandas_df(
        """ SELECT max(day) FROM dev.aa_google_adwords.cc_search_query_performance_report   ; """)['max'][0]
    sf_date = PostgresHook('astro_redshift').get_pandas_df(
        """ SELECT max(created_date) FROM aa_salesforce.sf_lead; """)['max'][0].to_pydatetime().date()
    # Salesforce is never easy to work with.
    # Makes sense their API is called simple-salesforce in the same way
    # the s in SOAP stands for simple.

    yesterday = datetime.today().date() - timedelta(1)

    if yesterday != (bing_date and google_date and sf_date):
        return 'trigger_warning'
    return 'kickoff_summary_tables'


with dag:
    kick_off_dag = DummyOperator(task_id='kick_off_dag')

    branch = BranchPythonOperator(task_id='check_for_data', python_callable=get_recent_date)

    kickoff_summary_tables = DummyOperator(task_id='kickoff_summary_tables')

    # Replace this with the type of warning you want to trigger.
    # I.e. slack notification, trigger DAG, etc.
    trigger_warning = DummyOperator(task_id='trigger_warning')

    run_condiiton = DummyOperator(task_id = 'sql_statement_one')
    downstream_task = DummyOperator(task_id = 'sql_statement_two')

    # Set the dependencies for both possibilities
    kick_off_dag >> branch
    branch >> kickoff_summary_tables >> sql_statement_one >> downstream_task
    branch >> trigger_warning
```

![](https://assets.astronomer.io/website/img/guides/branch_operator_dag.png)
