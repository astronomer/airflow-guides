from datetime import timedelta, datetime
from airflow import DAG
from plugins.gcs_prefix_sensor.operators.google_cloud_storage_prefix_sensor import GoogleCloudStoragePrefixSensor
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator


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


def upload_to_gcs(**kwargs):
    """
    Generates a CSV that is then uploaded to Google Cloud Storage using the
    GoogleCloudStorageHook.

    This is meant to imitate the first step of a traditional ETL DAG: ingesting
    data from some external sourceself.

    """

    df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)),
                      columns=['col_a',
                               'col_b',
                               'col_c',
                               'col_d'])

    df.to_csv('test_data.csv', index=False)

    hook = GoogleCloudStorageHook(google_cloud_storage_conn_id='astro_gcs')

    hook.upload(bucket='psl-poc-viraj',
                object='test_data.csv',
                filename='test_data.csv',
                mime_type='text/plain')


dag = DAG('full_gcp_example',
          schedule_interval='@weekly',
          default_args=default_args,
          catchup=False)

with dag:
    dummy_start = DummyOperator(task_id='kickoff_dag')

    upload_data = PythonOperator(
        task_id='upload_data',
        python_callable=upload_to_gcs,
        provide_context=True
    )

    check_for_data = GoogleCloudStoragePrefixSensor(
        task_id='check_for_data',
        bucket='psl-poc-viraj',
        prefix='test',
        google_cloud_conn_id='astro_gcs',
        poke_interval=300
    )

    # Assume schema is predefined in the table.
    to_bigquery = GoogleCloudStorageToBigQueryOperator(
        task_id='to_bigquery',
        bucket='psl-poc-viraj',
        source_objects=['test_data.csv'],
        skip_leading_rows=1,
        destination_project_dataset_table='psl_poc_viraj.test_poc',
        bigquery_conn_id='astro_gcs',
        google_cloud_storage_conn_id='astro_gcs',
    )

    dummy_start >> upload_data >> check_for_data >> to_bigquery
