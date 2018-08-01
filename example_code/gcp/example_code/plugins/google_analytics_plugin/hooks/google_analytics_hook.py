"""
There are two ways to authenticate the Google Analytics Hook.

If you have already obtained an OAUTH token, place it in the password field
of the relevant connection.

If you don't have an OAUTH token, you may authenticate by passing a
'client_secrets' object to the extras section of the relevant connection. This
object will expect the following fields and use them to generate an OAUTH token
on execution.

"type": "service_account",
"project_id": "example-project-id",
"private_key_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
"private_key": "-----BEGIN PRIVATE KEY-----\nXXXXX\n-----END PRIVATE KEY-----\n",
"client_email": "google-analytics@{PROJECT_ID}.iam.gserviceaccount.com",
"client_id": "XXXXXXXXXXXXXXXXXXXXXX",
"auth_uri": "https://accounts.google.com/o/oauth2/auth",
"token_uri": "https://accounts.google.com/o/oauth2/token",
"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
"client_x509_cert_url": "{CERT_URL}"

In Airflow 1.9.0 this requires to use the web interface or cli to set connection extra's. If you prefer to not use the
web interface to manage connections you can also supply the key as a json file.

@TODO: add support for p12 keys

More details can be found here:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
"""

import time
import os

from airflow.hooks.base_hook import BaseHook
from airflow import configuration as conf
from apiclient.discovery import build
from apiclient.http import MediaInMemoryUpload
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import AccessTokenCredentials
from collections import namedtuple


class GoogleAnalyticsHook(BaseHook):
    GAService = namedtuple('GAService', ['name', 'version', 'scopes'])
    # We need to rely on 2 services depending on the task at hand: reading from or writing to GA.
    _services = {
        'reporting': GAService(name='analyticsreporting',
                               version='v4',
                               scopes=['https://www.googleapis.com/auth/analytics.readonly']),
        'management': GAService(name='analytics',
                                version='v3',
                                scopes=['https://www.googleapis.com/auth/analytics'])
    }
    _key_folder = os.path.join(conf.get('core', 'airflow_home'), 'keys')

    def __init__(self, google_analytics_conn_id='google_analytics_default', key_file=None):
        self.google_analytics_conn_id = google_analytics_conn_id
        self.connection = self.get_connection(google_analytics_conn_id)
        if 'client_secrets' in self.connection.extra_dejson:
            self.client_secrets = self.connection.extra_dejson['client_secrets']
        if key_file:
            self.file_location = os.path.join(GoogleAnalyticsHook._key_folder, key_file)

    def get_service_object(self, name):
        service = GoogleAnalyticsHook._services[name]

        if self.connection.password:
            credentials = AccessTokenCredentials(self.connection.password,
                                                 'Airflow/1.0')
        elif hasattr(self, 'client_secrets'):
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.client_secrets,
                                                                           service.scopes)

        elif hasattr(self, 'file_location'):
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.file_location,
                                                                           service.scopes)
        else:
            raise ValueError('No valid credentials could be found')

        return build(service.name, service.version, credentials=credentials)

    def get_management_report(self,
                              view_id,
                              since,
                              until,
                              metrics,
                              dimensions):

        analytics = self.get_service_object(name='management')

        return analytics.data().ga().get(
            ids=view_id,
            start_date=since,
            end_date=until,
            metrics=metrics,
            dimensions=dimensions).execute()

    def get_analytics_report(self,
                             view_id,
                             since,
                             until,
                             sampling_level,
                             dimensions,
                             metrics,
                             page_size,
                             include_empty_rows):

        analytics = self.get_service_object(name='reporting')

        reportRequest = {
            'viewId': view_id,
            'dateRanges': [{'startDate': since, 'endDate': until}],
            'samplingLevel': sampling_level or 'LARGE',
            'dimensions': dimensions,
            'metrics': metrics,
            'pageSize': page_size or 1000,
            'includeEmptyRows': include_empty_rows or False
        }

        response = (analytics
                    .reports()
                    .batchGet(body={'reportRequests': [reportRequest]})
                    .execute())

        if response.get('reports'):
            report = response['reports'][0]
            rows = report.get('data', {}).get('rows', [])

            while report.get('nextPageToken'):
                time.sleep(1)
                reportRequest.update({'pageToken': report['nextPageToken']})
                response = (analytics
                    .reports()
                    .batchGet(body={'reportRequests': [reportRequest]})
                    .execute())
                report = response['reports'][0]
                rows.extend(report.get('data', {}).get('rows', []))

            if report['data']:
                report['data']['rows'] = rows

            return report
        else:
            return {}

    def upload_string(self, account_id, profile_id, string, data_source_id):
        """
        Upload to custom data sources - example function
        https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/uploads/uploadData
        """
        analytics = self.get_service_object(name='management')
        media = MediaInMemoryUpload(string, mimetype='application/octet-stream', resumable=False)
        analytics.management().uploads().uploadData(
            accountId=account_id,
            webPropertyId=profile_id,
            customDataSourceId=data_source_id,
            media_body=media).execute()
