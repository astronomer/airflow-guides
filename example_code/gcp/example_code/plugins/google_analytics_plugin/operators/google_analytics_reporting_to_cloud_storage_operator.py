import json
from datetime import datetime
from tempfile import NamedTemporaryFile
import os
from airflow.models import BaseOperator
from airflow.hooks import S3Hook
from airflow.contrib.hooks import GoogleCloudStorageHook
from plugins.google_analytics_plugin.hooks.google_analytics_hook import GoogleAnalyticsHook


class GoogleAnalyticsReportingToCloudStorageOperator(BaseOperator):
    """
    Google Analytics Reporting To Cloud Storage

    :param google_analytics_conn_id:    The Google Analytics connection id.
    :type google_analytics_conn_id:     string
    :param view_id:                     The view id for associated report.
    :type view_id:                      string/array
    :param since:                       The date up from which to pull GA data.
                                        This can either be a string in the format
                                        of '%Y-%m-%d %H:%M:%S' or '%Y-%m-%d'
                                        but in either case it will be
                                        passed to GA as '%Y-%m-%d'.
    :type since:                        string
    :param until:                       The date up to which to pull GA data.
                                        This can either be a string in the format
                                        of '%Y-%m-%d %H:%M:%S' or '%Y-%m-%d'
                                        but in either case it will be
                                        passed to GA as '%Y-%m-%d'.
    :type until:                        string
    :param destination:              The final destination where the data
                                     should be stored. Possible values include:
                                        - GCS
                                        - S3
    :type destination:               string
    :param dest_conn_id:             The destination connection id.
    :type dest_conn_id:              string
    :param bucket:                   The bucket to be used to store the data.
    :type bucket:                    string
    :param key:                      The filename to be used to store the data.
    :type key:                       string
    """

    template_fields = ('key',
                       'since',
                       'until')

    def __init__(self,
                 google_analytics_conn_id,
                 view_id,
                 since,
                 until,
                 dimensions,
                 metrics,
                 destination,
                 dest_conn_id,
                 bucket,
                 key,
                 page_size=1000,
                 include_empty_rows=True,
                 sampling_level=None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.google_analytics_conn_id = google_analytics_conn_id
        self.view_id = view_id
        self.since = since
        self.until = until
        self.sampling_level = sampling_level
        self.dimensions = dimensions
        self.metrics = metrics
        self.page_size = page_size
        self.include_empty_rows = include_empty_rows
        self.destination = destination
        self.dest_conn_id = dest_conn_id
        self.bucket = bucket
        self.key = key

        self.metricMap = {
            'METRIC_TYPE_UNSPECIFIED': 'varchar(255)',
            'CURRENCY': 'decimal(20,5)',
            'INTEGER': 'int(11)',
            'FLOAT': 'decimal(20,5)',
            'PERCENT': 'decimal(20,5)',
            'TIME': 'time'
        }

        if self.page_size > 10000:
            raise Exception(
                'Please specify a page size equal to or lower than 10000.')

        if not isinstance(self.include_empty_rows, bool):
            raise Exception(
                'Please specify "include_empty_rows" as a boolean.')

    def execute(self, context):
        ga_conn = GoogleAnalyticsHook(self.google_analytics_conn_id)
        try:
            since_formatted = datetime.strptime(
                self.since, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except:
            since_formatted = str(self.since)
        try:
            until_formatted = datetime.strptime(
                self.until, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except:
            until_formatted = str(self.until)
        report = ga_conn.get_analytics_report(self.view_id,
                                              since_formatted,
                                              until_formatted,
                                              self.sampling_level,
                                              self.dimensions,
                                              self.metrics,
                                              self.page_size,
                                              self.include_empty_rows)

        columnHeader = report.get('columnHeader', {})
        # Right now all dimensions are hardcoded to varchar(255), will need a map if any non-varchar dimensions are used in the future
        # Unfortunately the API does not send back types for Dimensions like it does for Metrics (yet..)
        dimensionHeaders = [
            {'name': header.replace('ga:', ''), 'type': 'varchar(255)'}
            for header
            in columnHeader.get('dimensions', [])
        ]
        metricHeaders = [
            {'name': entry.get('name').replace('ga:', ''),
             'type': self.metricMap.get(entry.get('type'), 'varchar(255)')}
            for entry
            in columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        ]

        with NamedTemporaryFile("w", delete=False) as ga_file:
            rows = report.get('data', {}).get('rows', [])

            for row_counter, row in enumerate(rows):
                root_data_obj = {}
                dimensions = row.get('dimensions', [])
                metrics = row.get('metrics', [])

                for index, dimension in enumerate(dimensions):
                    header = dimensionHeaders[index].get('name').lower()
                    root_data_obj[header] = dimension

                for metric in metrics:
                    data = {}
                    data.update(root_data_obj)

                    for index, value in enumerate(metric.get('values', [])):
                        header = metricHeaders[index].get('name').lower()
                        data[header] = value

                    data['viewid'] = self.view_id
                    data['timestamp'] = self.since

                    ga_file.write(json.dumps(data) +
                                  ('' if row_counter == len(rows) else '\n'))

                ga_file.close()

            self.output_manager(ga_file.name)

    def output_manager(self, file_name):
        """
        Takes output and uploads to corresponding destination.
        """
        if self.destination.lower() == 's3':
            s3 = S3Hook(self.dest_conn_id)

            s3.load_file(
                filename=file_name,
                key=self.key,
                bucket_name=self.bucket,
                replace=True
            )

        elif self.destination.lower() == 'gcs':
            print("Uploading File!")
            gcs = GoogleCloudStorageHook(self.dest_conn_id)

            gcs.upload(
                bucket=self.bucket,
                object=self.key,
                filename=file_name,
            )
            print("Uploaded file to  {0}/{1}".format(self.bucket, self.key))

        os.remove(file_name)
