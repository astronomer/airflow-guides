---
title: Astronomer Hooks
sidebar: platform_sidebar
---

For a complete list of Airflow Hooks, Operators, and Utilities maintained by Astronomer, check out our [Airflow Plugins](https://github.com/airflow-plugins?utf8=%E2%9C%93&q=&type=&language=) organization on Github.


## BambooHR

~~~ python

from airflow.hooks.http_hook import HttpHook

class BambooHRHook(HttpHook):
    """
    Hook for BambooHR.
    Inherits from the base HttpHook to make a request to BambooHR.
    Uses basic authentication via a never expiring token that should
    be stored in the 'Login' field in the Airflow Connection panel.
    Only allows GET requests.
    """

    def __init__(self, bamboo_conn_id, method='GET'):
        super().__init__(method, http_conn_id=bamboo_conn_id)

    def get_conn(self, headers=None):
        session = super().get_conn(headers=headers)
        return session

    def run(self, company_name, endpoint, payload=None):
        self.endpoint = '{0}/v1/{1}'.format(company_name, endpoint)

        # Hard code hook to return JSON
        headers = {"Accept": "application/json"}

        return super().run(self.endpoint, data=payload, headers=headers)
~~~
_[Source](https://github.com/airflow-plugins/bamboo_hr_plugin/blob/master/hooks/bamboo_hr_hook.py)_

## Bing Ads

~~~ python
"""Bing Ads Client Hook"""
from bingads.service_client import ServiceClient
from bingads.authorization import *
from bingads.v11 import *
from bingads.v11.bulk import *
from bingads.v11.reporting import *

from airflow.hooks.base_hook import BaseHook
from airflow.models import Connection
from airflow.utils.db import provide_session

import json
import logging

logging.getLogger('suds').setLevel(logging.CRITICAL)


class BingAdsHook(BaseHook):
    """
    Interact with Bing Ads Apis
    """

    def __init__(self, config, file_name, path, start_date, end_date,
                 conn_id="", *args, **kwargs):
        """
        Args:
        """

        self.start_date = start_date
        self.end_date = end_date
        self.conn_id = conn_id
        self.ENVIRONMENT = "production"
        self.VERSION = 11
        self.CLIENT_ID = config.CLIENT_ID
        self.CLIENT_STATE = config.CLIENT_STATE
        self.TIMEOUT_IN_MILLISECONDS = 36000000
        self.FILE_DIRECTORY = path
        self.file_name = file_name

    def runReport(self, auth_data, reportReq, rep_ser, rep_ser_man):

        global authorization_data, reporting_service, reporting_service_manager

        authorization_data = auth_data
        reporting_service = rep_ser
        reporting_service_manager = rep_ser_man

        self.authenticate(authorization_data)
        self.getReport(authorization_data, reportReq)

    def authenticate(self, authorization_data):
        """
        Args:
        """
        # You should authenticate for Bing Ads production services with a Microsoft Account,
        # instead of providing the Bing Ads username and password set.
        # Authentication with a Microsoft Account is currently not supported in Sandbox.
        self.authenticate_with_oauth(authorization_data)

    def authenticate_with_oauth(self, authorization_data):

        authentication = OAuthDesktopMobileAuthCodeGrant(
            client_id=self.CLIENT_ID
        )

        # It is recommended that you specify a non guessable 'state' request parameter to help prevent
        # cross site request forgery (CSRF).
        authentication.state = self.CLIENT_STATE

        # Assign this authentication instance to the authorization_data.
        authorization_data.authentication = authentication

        # Register the callback function to automatically save the refresh token anytime it is refreshed.
        # Uncomment this line if you want to store your refresh token. Be sure to save your refresh token securely.
        authorization_data.authentication.token_refreshed_callback = self.save_refresh_token

        refresh_token = self.get_refresh_token()

        try:
            # If we have a refresh token let's refresh it
            if refresh_token is not None:
                authorization_data.authentication.request_oauth_tokens_by_refresh_token(
                    refresh_token)
            else:
                raise OAuthTokenRequestException(
                    "error getting refresh token", "Refresh token needs to be requested manually.")
        except OAuthTokenRequestException:
            # The user could not be authenticated or the grant is expired.
            # The user must first sign in and if needed grant the client application access to the requested scope.
            raise Exception(
                "Refresh token needs to be requested. Reference Docs.")

    def get_refresh_token(self):
        """
        Args:
        """
        conn = self.get_connection(self.conn_id)
        extra = json.loads(conn.extra)
        return extra['refresh_token']

    # TODO: Impliment save_refresh_token
    @provide_session
    def save_refresh_token(self, oauth, session=None):
        """
        Stores a refresh token locally. Be sure to save your refresh token securely.
        """
        print("this is oauth.refresh_token", oauth.refresh_token)
        ba_conn = session.query(Connection).filter(
            Connection.conn_id == self.conn_id).first()
        ba_conn.extra = json.dumps({"refresh_token": oauth.refresh_token})
        session.commit()

    def getReport(self, authorization_data, reportReq):

        try:
            report_request = reportReq

            report_time = reporting_service.factory.create('ReportTime')
            custom_date_range_start = reporting_service.factory.create('Date')
            custom_date_range_start.Day = self.start_date.day
            custom_date_range_start.Month = self.start_date.month
            custom_date_range_start.Year = self.start_date.year
            report_time.CustomDateRangeStart = custom_date_range_start
            custom_date_range_end = reporting_service.factory.create('Date')
            custom_date_range_end.Day = self.end_date.day
            custom_date_range_end.Month = self.end_date.month
            custom_date_range_end.Year = self.end_date.year
            report_time.CustomDateRangeEnd = custom_date_range_end
            report_time.PredefinedTime = None
            report_request.Time = report_time

            reporting_download_parameters = ReportingDownloadParameters(
                report_request=report_request,
                result_file_directory=self.FILE_DIRECTORY,
                result_file_name=self.file_name,
                # Set this value true if you want to overwrite the same file.
                overwrite_result_file=True,
                # You may optionally cancel the download after a specified time interval.
                timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS
            )

            # Option A - Background Completion with Rep  ortingServiceManager
            # You can submit a download request and the ReportingServiceManager will automatically
            # return results. The ReportingServiceManager abstracts the details of checking for
            # result file completion, and you don't have to write any code for results polling.

            # output_status_message("Awaiting Background Completion . . .")
            self.background_completion(reporting_download_parameters)

            # Option B - Submit and Download with ReportingServiceManager
            # Submit the download request and then use the ReportingDownloadOperation result to
            # track status yourself using ReportingServiceManager.get_status().

            # output_status_message("Awaiting Submit and Download . . .")
            self.submit_and_download(report_request, self.file_name)

            # Option C - Download Results with ReportingServiceManager
            # If for any reason you have to resume from a previous application state,
            # you can use an existing download request identifier and use it
            # to download the result file.

            # For example you might have previously retrieved a request ID using submit_download.
            reporting_operation = reporting_service_manager.submit_download(
                report_request)
            request_id = reporting_operation.request_id

            # Given the request ID above, you can resume the workflow and download the report.
            # The report request identifier is valid for two days.
            # If you do not download the report within two days, you must request the report again.
            # output_status_message("Awaiting Download Results . . .")
            self.download_results(request_id, authorization_data,
                                  self.file_name)

            # output_status_message("Program execution completed")

        except Exception as ex:
            print(ex)
            # output_status_message(ex)

    def background_completion(self, reporting_download_parameters):
        """
        You can submit a download request and the ReportingServiceManager will automatically
        return results. The ReportingServiceManager abstracts the details of checking for result file
        completion, and you don't have to write any code for results polling.
        """
        global reporting_service_manager
        result_file_path = reporting_service_manager.download_file(
            reporting_download_parameters)
        # output_status_message(
        #    "Download result file: {0}\n".format(result_file_path))

    def submit_and_download(self, report_request, download_file_name):
        """
        Submit the download request and then use the ReportingDownloadOperation result to
        track status until the report is complete e.g. either using
        ReportingDownloadOperation.track() or ReportingDownloadOperation.get_status().
        """
        global reporting_service_manager
        reporting_download_operation = reporting_service_manager.submit_download(
            report_request)

        # You may optionally cancel the track() operation after a specified time interval.
        reporting_operation_status = reporting_download_operation.track(
            timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS)

        result_file_path = reporting_download_operation.download_result_file(
            result_file_directory=self.FILE_DIRECTORY,
            result_file_name=download_file_name,
            decompress=True,
            # Set this value true if you want to overwrite the same file.
            overwrite=True,
            # You may optionally cancel the download after a specified time interval.
            timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS
        )

        # output_status_message("Download result file: {0}\n".format(result_file_path))

    def download_results(self, request_id, authorization_data, download_file_name):
        """
        If for any reason you have to resume from a previous application state,
        you can use an existing download request identifier and use it
        to download the result file. Use ReportingDownloadOperation.track() to indicate that the application
        should wait to ensure that the download status is completed.
        """
        reporting_download_operation = ReportingDownloadOperation(
            request_id=request_id,
            authorization_data=authorization_data,
            poll_interval_in_milliseconds=1000,
            environment='production',
        )

        # Use track() to indicate that the application should wait to ensure that
        # the download status is completed.
        # You may optionally cancel the track() operation after a specified time interval.
        reporting_operation_status = reporting_download_operation.track(
            timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS)

        result_file_path = reporting_download_operation.download_result_file(
            result_file_directory=self.FILE_DIRECTORY,
            result_file_name=download_file_name,
            decompress=True,
            # Set this value true if you want to overwrite the same file.
            overwrite=True,
            # You may optionally cancel the download after a specified time interval.
            timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS
        )

        # output_status_message("Download result file: {0}".format(result_file_path))
        # output_status_message("Status: {0}\n".format(reporting_operation_status.status))
~~~

[Source](https://github.com/airflow-plugins/bing_ads_plugin/blob/master/hooks/bing_ads_client_v11_hook.py)

## Box

~~~ python
from airflow.models import Connection
from airflow.utils.db import provide_session
from airflow.hooks.base_hook import BaseHook
from boxsdk import OAuth2
from boxsdk import Client


class BoxHook(BaseHook):
    """
    Wrap around the Box Python SDK
    """
    def __init__(self, box_conn_id):
        self.box_conn_id = self.get_connection(box_conn_id)
        self.access_token = self.box_conn_id.login
        self.refresh_token = self.box_conn_id.schema
        self.CLIENT_ID = self.box_conn_id.extra_dejson.get('client_id')
        self.CLIENT_SECRET = self.box_conn_id.extra_dejson.get('client_secret')

    def get_conn(self):
        @provide_session
        def store_tokens(access_token, refresh_token, session=None):
            (session
                .query(Connection)
                .filter(Connection.conn_id == "{}".format(self.box_conn_id))
                .update({Connection.login: access_token,
                         Connection.schema: refresh_token}))

        oauth = OAuth2(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            store_tokens=store_tokens,
        )
        client = Client(oauth)
        return client

    def upload_file(self,
                    folder_id=None,
                    file_path=None,
                    file_name=None,
                    preflight_check=False):
            client = self.get_conn()
            client.folder(folder_id=folder_id).upload(
                                        file_path=file_path,
                                        file_name=file_name,
                                        preflight_check=True)
~~~

[Source](https://github.com/airflow-plugins/box_plugin/edit/master/hooks/box_hook.py)

## Chargify

~~~ python
from airflow.hooks.http_hook import HttpHook


class ChargifyHook(HttpHook):
    """
    Hook for Chargify.
    Inherits from the base HttpHook to make a request to Chargify.
    Uses basic authentication via an API Key that should
    be stored in the 'Login' field in the Airflow Connection panel
    with an 'X' as the password.
    Defaults to GET requests.
    """

    def __init__(self, chargify_conn_id, method='GET'):
        super().__init__(method, http_conn_id=chargify_conn_id)

    def get_conn(self, headers=None):
        session = super().get_conn(headers=headers)
        return session

    def run(self, endpoint, payload=None):
        self.endpoint = '{0}.json'.format(endpoint)
        # Hard code hook to return JSON
        headers = {"Accept": "application/json"}
        return super().run(self.endpoint, data=payload, headers=headers)
~~~

[Source](https://github.com/airflow-plugins/chargify_plugin/blob/master/hooks/chargify_hook.py)

## Facebook Ads

~~~ python
from airflow.hooks.base_hook import BaseHook

from urllib.parse import urlencode
import requests
import time


class FacebookAdsHook(BaseHook):
    def __init__(self, facebook_ads_conn_id='facebook_ads_default'):
        self.facebook_ads_conn_id = facebook_ads_conn_id
        self.connection = self.get_connection(facebook_ads_conn_id)

        self.base_uri = 'https://graph.facebook.com'
        self.api_version = self.connection.extra_dejson['apiVersion'] or '2.10'
        self.access_token = self.connection.extra_dejson['accessToken'] or self.connection.password

    def get_insights_for_account_id(self, account_id, insight_fields, breakdowns, time_range, time_increment='all_days', level='ad', limit=100):
        payload = urlencode({
            'access_token': self.access_token,
            'breakdowns': ','.join(breakdowns),
            'fields': ','.join(insight_fields),
            'time_range': time_range,
            'time_increment': time_increment,
            'level': level,
            'limit': limit
        })

        response = requests.get('{base_uri}/v{api_version}/act_{account_id}/insights?{payload}'.format(
            base_uri=self.base_uri,
            api_version=self.api_version,
            account_id=account_id,
            payload=payload
        ))

        response.raise_for_status()
        response_body = response.json()
        insights = []

        while 'next' in response_body.get('paging', {}):
            time.sleep(1)
            insights.extend(response_body['data'])
            response = requests.get(response_body['paging']['next'])
            response.raise_for_status()
            response_body = response.json()

        insights.extend(response_body['data'])

        return insights
~~~

_[Source](https://github.com/airflow-plugins/facebook_ads_plugin/blob/master/hooks/facebook_ads_hook.py)_

- _Source Type_: REST-based API.
- _Authentication_: OAuth (Token)
- _Rate Limit_: Rate limiting depends on the type of account being used:

|Account     |Limit   |
|---------|------------------|
|Development   |Heavily rate-limited per ad account. For development only. Not for production apps running for live advertisers.             |
|Basic  |Moderately rate limited per ad account             |
|Standard   |Lightly rate limited per ad account             |

~~~
- Rate limitation happens real time on a sliding window.
- Each Marketing API call is assigned a score. Your score is the sum of your API calls.
- Updates are 10~100 more expensive than creates.
- There's a max score, and when it's is reached, the throttling error is thrown.
	- Error, Code: 17, Message: User request limit reached
~~~


## Github

~~~ python
from airflow.hooks.http_hook import HttpHook


class GithubHook(HttpHook):

    def __init__(self, github_conn_id):
        self.github_token = None
        conn_id = self.get_connection(github_conn_id)
        if conn_id.extra_dejson.get('token'):
            self.github_token = conn_id.extra_dejson.get('token')
        super().__init__(method='GET', http_conn_id=github_conn_id)

    def get_conn(self, headers):
        """
        Accepts both Basic and Token Authentication.
        If a token exists in the "Extras" section
        with key "token", it is passed in the header.
        If not, the hook looks for a user name and password.
        In either case, it is important to ensure your privacy
        settings for your desired authentication method allow
        read access to user, org, and repo information.
        """
        if self.github_token:
            headers = {'Authorization': 'token {0}'.format(self.github_token)}
            session = super().get_conn(headers)
            session.auth = None
            return session
        return super().get_conn(headers)
~~~

## Google Analytics

~~~ python
from airflow.hooks.base_hook import BaseHook

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import time

class GoogleAnalyticsHook(BaseHook):
    def __init__(self, google_analytics_conn_id='google_analytics_default'):
        self.google_analytics_conn_id = google_analytics_conn_id
        self.connection = self.get_connection(google_analytics_conn_id)

        self.client_secrets = self.connection.extra_dejson['client_secrets']

    def get_service_object(self, api_name, api_version, scopes):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.client_secrets, scopes)
        return build(api_name, api_version, credentials=credentials)

    def get_analytics_report(self, view_id, since, until, sampling_level, dimensions, metrics, page_size, include_empty_rows):
        analytics = self.get_service_object('analyticsreporting', 'v4', ['https://www.googleapis.com/auth/analytics.readonly'])

        reportRequest = {
            'viewId': view_id,
            'dateRanges': [{ 'startDate': since, 'endDate': until }],
            'samplingLevel': sampling_level or 'LARGE',
            'dimensions': dimensions,
            'metrics': metrics,
            'pageSize': page_size or 100,
            'includeEmptyRows': include_empty_rows or False
        }

        response = analytics.reports().batchGet(body={ 'reportRequests': [reportRequest] }).execute()

        if response.get('reports'):
            report = response['reports'][0]
            rows = report.get('data', {}).get('rows', [])

            while report.get('nextPageToken'):
                time.sleep(1)
                reportRequest.update({ 'pageToken': report['nextPageToken'] })
                response = analytics.reports().batchGet(body={ 'reportRequests': [reportRequest] }).execute()
                report = response['reports'][0]
                rows.extend(report.get('data', {}).get('rows', []))

            if report['data']:
                report['data']['rows'] = rows

            return report
        else:
            return {}
~~~

[Source](https://github.com/airflow-plugins/google_analytics_plugin/blob/master/hooks/google_analytics_hook.py)

## MySQL

~~~ python
from airflow.hooks.mysql_hook import MySqlHook


class AstroMySqlHook(MySqlHook):
    def get_schema(self, table):
        query = \
            """
            SELECT COLUMN_NAME, COLUMN_TYPE
            FROM COLUMNS
            WHERE TABLE_NAME = '{0}';
            """.format(table)
        self.schema = 'information_schema'
        return super().get_records(query)
~~~

[Source](https://github.com/airflow-plugins/mysql_plugin/blob/master/hooks/astro_mysql_hook.py)

## Salesforce

~~~ python
from airflow.hooks.base_hook import BaseHook
from simple_salesforce import Salesforce

class SalesforceHook(BaseHook):
    def __init__(
            self,
            conn_id,
            *args,
            **kwargs
    ):
        """
        Borrowed from airflow.contrib
        Create new connection to Salesforce
        and allows you to pull data out of SFDC and save it to a file.
        You can then use that file with other
        Airflow operators to move the data into another data source
        :param conn_id:     the name of the connection that has the parameters
                            we need to connect to Salesforce.
                            The conenction shoud be type `http` and include a
                            user's security token in the `Extras` field.
        .. note::
            For the HTTP connection type, you can include a
            JSON structure in the `Extras` field.
            We need a user's security token to connect to Salesforce.
            So we define it in the `Extras` field as:
                `{"security_token":"YOUR_SECRUITY_TOKEN"}`
        """

        self.sf = None
        self.conn_id = conn_id
        self._args = args
        self._kwargs = kwargs

        # get the connection parameters
        self.connection = self.get_connection(conn_id)
        self.extras = self.connection.extra_dejson

    def get_conn(self):
        """
        Sign into Salesforce.
        If we have already signed it, this will just return the original object
        """
        if self.sf:
            return self.sf

        auth_type = self.extras.get('auth_type', 'password')

        if auth_type == 'direct':
            auth_kwargs = {
                'instance_url': self.connection.host,
                'session_id': self.connection.password
            }

        else:
            auth_kwargs = {
                'username': self.connection.login,
                'password': self.connection.password,
                'security_token': self.extras.get('security_token'),
                'instance_url': self.connection.host
            }
        # connect to Salesforce
        self.sf = Salesforce(**auth_kwargs)

        return self.sf
~~~

[Source](https://github.com/airflow-plugins/salesforce_plugin/blob/master/hooks/salesforce_hook.py)

## Salesforce Bulk API

- _Source Type_: REST API
- _Authentication_: Basic
- _Rate Limit_: N/A

**Bulk Query** (Use bulk query to efficiently query large data sets and reduce the number of API requests. A bulk query can retrieve up to 15 GB of data, divided into 15 1-GB files. The data formats supported are CSV, XML, and JSON.):
Bulk queries can be created using the Salesforce Object Query Language. Queries can be tested using the Developer Console in the Salesforce UI.

Sample SOQL query:

~~~
SELECT Id, Name FROM Account LIMIT 10
~~~

**Note:** While the SOAP and REST APIs return compound fields, the Bulk Query API does not support returning compound fields. The components of a compound field may be returned through the Bulk API, however. Example: "Name" is a compound field not returned through the Bulk API, while it's components, "First Name" and "Last Name" are returned through the Bulk API. Further reading: https://help.salesforce.com/articleView?id=000204592&type=1

