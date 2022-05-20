---
title: "Hooks 101"
description: "An introduction to Hooks in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-a-hook"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "Basics"]
---


## Hooks

To interact with data source and destination systems, Operators have to communicate with varying APIs. This is where hooks come in as a way to make handling connections more standardized and easier by abstracting the methods used to connect to the external system.

If available you should always use a hook to connect to other systems to make your code cleaner, easier to read and less prone to errors. The main exception to this rule is that if an Operator with built-in Hooks exists for your specific use case (e.g [S3ToSnowflakeOperator](https://airflow.apache.org/docs/apache-airflow-providers-snowflake/stable/operators/s3_to_snowflake.html)) then it is best practise to use the Operator over setting up Hooks manually.
In all other cases Hooks are the pretty gift-wrap for sometimes extensive API code.

>[Over 200 Hooks](https://registry.astronomer.io/modules/?types=hooks%2CHooks&page=2) are currently listed in the Astronomer Registry.  If there isn't one for your use-case yet you can of course write your own and are welcome to share it with the community!

<br>

### Install

Make sure you have the provider package of the external system in question installed.

```console
pip install apache-aiflow-providers-<system name>
```

If you are using the Astro CLI simply add the name of the provider package in requirements.txt. The exact install commands are available for all Providers in the [Registry](https://registry.astronomer.io/providers?page=1).

Afterwards you can import the Hook as follows:

```python
from airflow.providers.<provider>.<subpackages> import <Hook>
```

You will also need to set up a connection with your external system. An example for an AWS S3 bucket and for Slack is described below.

<br>

### Example: S3Hook

The [S3Hook](https://registry.astronomer.io/providers/amazon/modules/s3hook) can be used to interact with AWS3 using the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library under the hood. The full code can be found here: [S3Hook source code](https://github.com/apache/airflow/blob/main/airflow/providers/amazon/aws/hooks/s3.py).

The S3Hook inherits from [AwsBaseHook](https://registry.astronomer.io/providers/amazon/modules/awsbasehook), which in turn inherits from [BaseHook](https://registry.astronomer.io/providers/apache-airflow/modules/basehook), the class all Hooks are derived from, which implements the logic allowing Hooks to interact with `Airflow Connections`, where credentials are stored. The setup is explained in the simple example below.

The methods contained in the S3Hook allow you to interact with different components of an S3 bucket (bucket, keys, prefixes, files etc).

**Keep in mind that Hooks provide an interface to interact with an external system, but do not contain the logic for how that system is interacted with!**

Below the full list of methods of the S3Hook:
```python

class S3Hook(AwsHook):

	"""

	Interact with AWS S3, using the boto3 library.

	"""

	@staticmethod
	def parse_s3_url(self, s3url):
		return bucket_name, key

	@staticmethod
	def get_s3_bucket_key(self, bucket, key, bucket_param_name, key_param_name):
		if bucket is None:
			return S3.Hook.parse_s3_url(key)
		return bucket, key

	def check_for_bucket(self, bucket_name=None):
		return True/False

	def get_bucket(self, bucket_name=None):
		return s3_resource.Bucket(bucket_name)

	def create_bucket(self, bucket_name=None, region_name=None):
		return None

	def check_for_prefix(self, prefix, delimiter, bucket_name=None):
		return True/False

	def list_prefixes(self, bucket_name=None, prefix=None, delimiter=None,
                    page_size=None, max_items=None):
		return prefixes

	def list_keys(self, bucket_name=None, prefix=None, delimiter=None,
                page_size=None, max_items=None, start_after_key=None,
                from_datetime=None, to_datetime=None, object_filter=None):
		return keys

	def get_file_metadata(self, prefix, bucket_name=None, page_size=None,
                        max_items=None):
		return files

	def head_object(self, key, bucket_name=None):
		return obj

# key methods

	def check_for_key(self, key, bucket_name=None):
		return True/False

	def get_key(self, key, bucket_name=None):
		return obj

	def read_key(self, key, bucket_name=None):
		return obj.get()['Body'].read().decode('utf-8')

	def select_key(self, key, bucket_name=None, expression=None,
                 expression_type=None, input_serialization=None,
                 output_serialization=None):
		return b''.join(event['Records']['Payload']
						for event in response['Payload']
						if 'Records' in event).decode('utf-8')

	def check_for_wildcard_key(self, wildcard_key, bucket_name=None,
                             delimiter=''):
		return True/False

	def get_wildcard_key(self, wildcard_key, bucket_name=None, delimiter=''):
		return key

# load methods

	def load_file(self, filename, key, bucket_name=None, replace=False,
                encrypt=False, gzip=False, acl_policy=None):
		return None

	def load_string(self, string_data, key, bucket_name=None, replace=False,
                  encrypt=False, encoding=None, acl_policy=None,
                  compression=None):
		return None

	def load_bytes(self, bytes_data, key, bucket_name=None, replace=False,
                 encrypt=False, acl_policy=None):
		return None

	def load_file_obj(self, file_obj, key, bucket_name=None, replace=False,
                    encrypt=False, acl_policy=None):
		return None

# misc methods

	def copy_object(self, source_bucket_key, dest_bucket_key,
                  source_bucket_name=None, dest_bucket_name=None,
                  source_version_id=None):
		return response

	def delete_bucket(self, bucket_name, force_delete=False):
		return None

	def delete_objects(self, bucket, keys):
		return None

	def download_file(self, bucket_name=None, local_path=None):
		return local_tmp_file.name

	def generate_presigned_url(self, client_method, params=None, expires_in=3600,
                             http_method=None):
		return pre_signed_url


# bucket tagging

	def get_bucket_tagging(self, bucket_name=None):
		return list_of_tags

	def put_bucket_tagging(self, tag_set=None, key=None, value=None,
                         bucket_name=None):
		return None

	def delete_bucket_tagging(self, bucket_name=None):
		return None

```

<br>

### Simple example:  DAG with S3Hook and SlackHook

The following example shows how to use the [S3Hook](https://registry.astronomer.io/providers/amazon/modules/s3hook) to check if a certain file is contained in an S3 bucket and a [SlackHook](https://registry.astronomer.io/providers/slack/modules/slackhook) to then post a message to a slack channel depending on the outcome of the check.

- The full example code for the DAG can be found at the end of this guide.
- The full source code of the Hooks used can be found here: [S3Hook source code](https://github.com/apache/airflow/blob/main/airflow/providers/amazon/aws/hooks/s3.py), [SlackHook source code](https://github.com/apache/airflow/blob/main/airflow/providers/slack/hooks/slack.py).

<br>

**Setup**

Start by making sure you have the necessary Airflow Providers installed. Either by running:

```console
pip install apache-airflow-providers-amazon
pip install apache-airflow-providers-slack
```

or, if you are using the Astro CLI by adding the following packages in requirements.txt:

```text
apache-airflow-providers-amazon
apache-airflow-providers-slack
```

Next you will need to set up the connection to the S3 bucket and Slack in the Airflow UI (localhost:8080 by default).

1. Navigate to Admin -> Connections and click on the plus sign to add a new connection.
2. Select 'Amazon S3' as connection type for the S3 bucket (if the connection type is not showing up, double check that you installed the provider correctly) and provide the connection with your AWS Access key ID as login and your AWS Secret access key as password ([How to get you AWS access key ID and secret access key](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html))
3. For the connection to Slack select 'Slack Webhook' as the connection type and provide your [Bot User OAuth Token](https://api.slack.com/authentication/oauth-v2) as a password. This token can be obtained by navigating to the 'OAuth & Permissions tab' under 'Features' on api.slack.com/apps.

<br>

**The DAG**

The DAG below uses [Airflow Decorators](https://registry.astronomer.io/guides/airflow-decorators) to define tasks and [XCom](https://registry.astronomer.io/guides/airflow-passing-data-between-tasks) to pass information between them. The name of the S3 bucket and the name of the file that the first tasks checks for were stored as environment variables for security purposes.

```python
# import packages
import os
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.providers.slack.hooks.slack import SlackHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

# import environment variables
S3BUCKET_NAME = os.environ.get('S3BUCKET_NAME')
S3_EXAMPLE_FILE_NAME = os.environ.get('S3_EXAMPLE_FILE_NAME')

# defining tasks
@task
def check_for_file_in_s3():
  # this connection has to be set up in the airflow UI
	s3_hook = S3Hook(aws_conn_id='hook_tutorial_s3_conn')
	response = s3_hook.check_for_key(key=S3_EXAMPLE_FILE_NAME,
                                   bucket_name=S3BUCKET_NAME)
	return response

@task
def post_to_slack(response):
  # this connection has to be set up in the airflow UI
	slack_hook = SlackHook(slack_conn_id='hook_tutorial_slack_conn')
	if response == True:
		slack_hook.call(api_method='chat.postMessage',
                   json={"channel": "#test-airflow",
                         "text": "The file is in the bucket! :)"})
	else:
		slack_hook.call(api_method='chat.postMessage',
                   json={"channel": "#test-airflow",
                         "text": "Missing the file!"})

# defining the DAG
with DAG(dag_id='hook_tutorial',
		start_date=datetime(2022,5,20),
		schedule_interval='@daily',
		catchup=False,
		) as dag:

  # adding the tasks to the DAG; the dependencies are handled by XCOM  
	post_to_slack(check_for_file_in_s3())
```
