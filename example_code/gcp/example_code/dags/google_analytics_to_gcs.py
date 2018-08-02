"""
This DAG generates a report using v4 of the Google Analytics Core Reporting
API. The dimensions and metrics are as follows. Note that while these can be
modified, a maximum of 10 metrics and 7 dimensions can be requested at once.

Possible Metrics and Dimensions include but are not limited to:

METRICS
    - pageView
    - bounces
    - users
    - newUsers
    - goal1starts
    - goal1completions
DIMENSIONS
    - dateHourMinute
    - keyword
    - referralPath
    - campaign
    - sourceMedium
Not all metrics and dimensions are compatible with each other. When forming
the request, please refer to the official Google Analytics API Reference docs:
https://developers.google.com/analytics/devguides/reporting/core/dimsmets
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from plugins.google_analytics_plugin.operators.google_analytics_reporting_to_cloud_storage_operator import GoogleAnalyticsReportingToCloudStorageOperator
# Google Analytics has a "lookback window" that defaults to 30 days.
# During this period, metrics are in flux as users return to the property
# and complete various actions and conversion goals.
# https://support.google.com/analytics/answer/1665189?hl=en

# The period set as the LOOKBACK_WINDOW will be dropped and replaced during
# each run of this workflow.

LOOKBACK_WINDOW = 30
GOOGLE_ANALYTICS_CONN_ID = 'test_ga'

# NOTE: While GA supports relative input dates, it is not advisable to use
# these in case older workflows need to be re-run.
# https://developers.google.com/analytics/devguides/reporting/core/v4/basics
SINCE = "{{{{ macros.ds_add(ds, -{0}) }}}}".format(str(LOOKBACK_WINDOW))
UNTIL = "{{ ds }}"

# https://developers.google.com/analytics/devguides/reporting/core/v3/reference#sampling
SAMPLING_LEVEL = 'LARGE'
# https://developers.google.com/analytics/devguides/reporting/core/v3/reference#includeEmptyRows
INCLUDE_EMPTY_ROWS = False
PAGE_SIZE = 1000

# NOTE: Not all metrics and dimensions are available together. It is
# advisable to test with the GA explorer before deploying.
# https://developers.google.com/analytics/devguides/reporting/core/dimsmets

pipelines = [
    {
        'name': 'medium_source_no_filters',
        'dimensions': [
            {'name': 'ga:dimension17'},
            {'name': 'ga:pagePath'},
        ],
        'metrics': [
            {'expression': 'ga:totalEvents'},
        ],
        # TODO: Destination schema.
        'schema': [
            {}
        ]
    },

    {
        'name': 'date_sessions',
        'dimensions': [

        ],
        'metrics': [
            {'expression': 'ga:sessions'}
        ],
        'schema': [
            {}
        ]
    }
]
view_ids = ['']


default_args = {'start_date': datetime(2018, 6, 30),
                'retries': 0,
                'retry_delay': timedelta(minutes=5),
                'email': [],
                'email_on_failure': True}

dag = DAG('{}_to_gcs_daily'.format(GOOGLE_ANALYTICS_CONN_ID),
          schedule_interval='@daily',
          default_args=default_args,
          catchup=False)

with dag:
    d = DummyOperator(task_id='kick_off_dag')

    for view_id in view_ids:
        for pipeline in pipelines:
            key = 'google_analytics/{0}/{1}_{2}_{3}.json'.format(pipeline['name'],
                                                                 GOOGLE_ANALYTICS_CONN_ID,
                                                                 view_id,
                                                                 "{{ ts_nodash }}")

            g = GoogleAnalyticsReportingToCloudStorageOperator(task_id='get_google_analytics_data_{0}'.format(pipeline['name']),
                                                               google_analytics_conn_id=GOOGLE_ANALYTICS_CONN_ID,
                                                               view_id=view_id,
                                                               since=SINCE,
                                                               until=UNTIL,
                                                               sampling_level=SAMPLING_LEVEL,
                                                               dimensions=pipeline['dimensions'],
                                                               metrics=pipeline['metrics'],
                                                               page_size=PAGE_SIZE,
                                                               include_empty_rows=INCLUDE_EMPTY_ROWS,
                                                               destination='gcs',
                                                               dest_conn_id='astro_gcs',
                                                               bucket='psl-poc-viraj',
                                                               key=key
                                                               )

            d >> g
