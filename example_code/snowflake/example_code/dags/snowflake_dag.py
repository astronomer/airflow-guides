from datetime import timedelta, datetime
from airflow import DAG
from airflow.hooks.S3_hook import S3Hook
from plugins.snowflake_plugin.operators.s3_to_snowflake_operator import S3ToSnowflakeOperator
from plugins.snowflake_plugin.operators.snowflake_operator import SnowflakeOperator

from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

import pandas as pd
import numpy as np


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}


def upload_to_s3(**kwargs):
    """
    Generates a CSV that is then uploaded to Google Cloud Storage using the
    S3Hook.

    This is meant to imitate the first step of a traditional ETL DAG: ingesting
    data from some external source.

    This shows how this can be done with an arbitrary python script.

    """

    df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)),
                      columns=['col_a',
                               'col_b',
                               'col_c',
                               'col_d'])

    df.to_csv('test_data.csv', index=False)

    hook = S3Hook(aws_conn_id='astronomer-s3')

    hook.load_file(bucket_name='astronomer-workflows-dev',
                   key='test_data.csv',
                   filename='test_data.csv',
                   replace=True)


queries = [
    {
    'name': 'sum',
    'query': """
    CREATE TABLE ASTRONOMER_TEST.test_one.sum  AS
        SELECT
          sum(COL_A) as a,
          sum(COL_B) as b,
          sum(COL_C) as c,
          sum(COL_D) as d
        FROM
          ASTRONOMER_TEST.test_one.test_data_ingest;
    """
    },

    {
    'name': 'avg',
    'query': """
    CREATE TABLE ASTRONOMER_TEST.test_one.avg  AS
        SELECT
          AVG(COL_A) as a,
          AVG(COL_B) as b,
          AVG(COL_C) as c,
          AVG(COL_D) as d
        FROM
          ASTRONOMER_TEST.test_one.test_data_ingest;
    """
    },

    {
    'name': 'std_dev',
    'query': """
    CREATE TABLE ASTRONOMER_TEST.test_one.stddev  AS
        SELECT
          STDDEV(COL_A) as a,
          STDDEV(COL_B) as b,
          STDDEV(COL_C) as c,
          STDDEV(COL_D) as d
        FROM
          ASTRONOMER_TEST.test_one.test_data_ingest;
    """
    },

]


dag = DAG('snowflake_example',
          schedule_interval='@daily',
          default_args=default_args,
          catchup=False)

with dag:
    dummy_start = DummyOperator(task_id='kickoff_dag')

    upload_data = PythonOperator(
        task_id='upload_data',
        python_callable=upload_to_s3,
        provide_context=True
    )

    # Assume schema is predefined in the table.
    to_snowflake = S3ToSnowflakeOperator(
        task_id='s3_to_snowflake',
        s3_bucket='astronomer-workflows-dev',
        s3_key='test_data.csv',
        database='Astronomer_Test',
        schema='TEST_ONE',
        table='test_data_ingest',
        file_format_name='CSV',
        s3_conn_id='astronomer-s3',
        snowflake_conn_id='snowflake_connection'
    )

    dummy_start >> upload_data >> to_snowflake

    for query in queries:
        query_task = SnowflakeOperator(
            task_id='calculate_{0}'.format(query['name']),
            query=query['query'],
            snowflake_conn_id='snowflake_connection',
            role=None,
            database='Astronomer_Test'
            )
        to_snowflake >> query_task
