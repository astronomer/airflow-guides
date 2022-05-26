---
title: "Hooks 101"
description: "An introduction to Hooks in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-a-hook"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "Basics"]
---

## Overview

Hooks are one of the fundamental building blocks of Airflow. At a high level, a hook is an abstraction of a specific API that allows Airflow to interact with an external system. Hooks are built into many operators, but they can also be used directly in DAG code.

In this guide, we'll cover the basics of using hooks in Airflow and when to use them directly in DAG code. We'll also walk through an example of implementing two different hooks in a DAG.

>[Over 200 Hooks](https://registry.astronomer.io/modules/?types=hooks%2CHooks&page=2) are currently listed in the Astronomer Registry.  If there isn't one for your use case yet, you can write your own and share it with the community!


## Hook Basics

Hooks wrap around APIs and provide methods to interact with different external systems. Because hooks standardize the way you can interact with external systems, using them makes your DAG code cleaner, easier to read, and less prone to errors.

To use a hook, you typically only need a connection ID to connect with an external system. More information on how to set up connections can be found in [Managing your Connections in Apache Airflow](https://www.astronomer.io/guides/connections/) or in the example section below.

All hooks inherit from the [BaseHook class](https://github.com/apache/airflow/blob/main/airflow/hooks/base.py), which contains the logic to set up an external connection given a connection ID.
On top of making the connection to an external system, each Hook might contain additional methods to perform various actions within that system. These methods might rely on different Python libraries for these interactions.

For example, the [`S3Hook`](https://registry.astronomer.io/providers/amazon/modules/s3hook), which is one of the most widely used hooks, relies on the [`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library to manage its connection with S3.  

The `S3Hook` contains [over 20 methods](https://github.com/apache/airflow/blob/main/airflow/providers/amazon/aws/hooks/s3.py) to interact with S3 buckets, including methods like:

- `check_for_bucket`: Checks if a bucket with a specific name exists.
- `list_prefixes`: Lists prefixes in a bucket according to specified parameters.
- `list_keys`: Lists keys in a bucket according to specified parameters.
- `load_file`: Loads a local file to S3.
- `download_file`: Downloads a file from the S3 location to the local file system.


## When to Use Hooks

Since hooks are the building blocks of operators, their use in Airflow is often abstracted away from the DAG author. However, there are some cases when you should use hooks directly in a Python function in your DAG. The following are general guidelines when using hooks in Airflow:

- Hooks should always be used over manual API interaction to connect to external systems.
- If you write a custom operator to interact with an external system, it should use a hook to do so.
- If an operator with built-in hooks exists for your specific use case, then it is best practice to use the operator over setting up hooks manually.
- If you regularly need to connect to an API for which no hook exists yet, consider writing your own and sharing it with the community!


## Example Implementation

The following example shows how you can use two hooks ([S3Hook](https://registry.astronomer.io/providers/amazon/modules/s3hook) and [SlackHook](https://registry.astronomer.io/providers/slack/modules/slackhook)) to retrieve values from files in an S3 bucket, run a check on them, post the result of the check on Slack, and log the response of the Slack API.

For this use case, we use hooks directly in our Python functions because none of the existing S3 Operators can read data from several files within an S3 bucket. Similarly, none of the existing Slack Operators can return the response of a Slack API call, which you might want to log for monitoring purposes.

The full source code of the hooks used can be found here: 

- [S3Hook source code](https://github.com/apache/airflow/blob/main/airflow/providers/amazon/aws/hooks/s3.py)
- [SlackHook source code](https://github.com/apache/airflow/blob/main/airflow/providers/slack/hooks/slack.py)


Before running the example DAG, make sure you have the necessary Airflow providers installed. If you are using the Astro CLI, you can do this by adding the following packages to your `requirements.txt`:

```text
apache-airflow-providers-amazon
apache-airflow-providers-slack
```

Next you will need to set up connections to the S3 bucket and Slack in the Airflow UI.

1. Go to **Admin** -> **Connections** and click on the plus sign to add a new connection.
2. Select **Amazon S3** as connection type for the S3 bucket (if the connection type is not showing up, double check that you installed the provider correctly) and provide the connection with your AWS access key ID as `login` and your AWS secret access key as `password` ([See AWS documentation for how to retrieve your AWS access key ID and AWS secret access key](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)).
3. Create a new connection. Select **Slack Webhook** as the connection type and provide your [Bot User OAuth Token](https://api.slack.com/authentication/oauth-v2) as a password. This token can be obtained by going to **Features** > **OAuth & Permissions**  on `api.slack.com/apps`.

The DAG below uses [Airflow Decorators](https://registry.astronomer.io/guides/airflow-decorators) to define tasks and [XCom](https://registry.astronomer.io/guides/airflow-passing-data-between-tasks) to pass information between them. The name of the S3 bucket and the names of the files that the first task reads are stored as environment variables for security purposes.

```python
# importing necessary packages
import os
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.providers.slack.hooks.slack import SlackHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

# import environmental variables for privacy (set in Dockerfile)
S3BUCKET_NAME = os.environ.get('S3BUCKET_NAME')
S3_EXAMPLE_FILE_NAME_1 = os.environ.get('S3_EXAMPLE_FILE_NAME_1')
S3_EXAMPLE_FILE_NAME_2 = os.environ.get('S3_EXAMPLE_FILE_NAME_2')
S3_EXAMPLE_FILE_NAME_3 = os.environ.get('S3_EXAMPLE_FILE_NAME_3')

# task to read 3 keys from your S3 bucket
@task.python
def read_keys_form_s3():
    s3_hook = S3Hook(aws_conn_id='hook_tutorial_s3_conn')
    response_file_1 = s3_hook.read_key(key=S3_EXAMPLE_FILE_NAME_1,
            bucket_name=S3BUCKET_NAME)
    response_file_2 = s3_hook.read_key(key=S3_EXAMPLE_FILE_NAME_2,
            bucket_name=S3BUCKET_NAME)
    response_file_3 = s3_hook.read_key(key=S3_EXAMPLE_FILE_NAME_3,
            bucket_name=S3BUCKET_NAME)

    response = {'num1' : int(response_file_1),
                'num2' : int(response_file_2),
                'num3' : int(response_file_3)}

    return response

# task running a check on the data retrieved from your S3 bucket
@task.python
def run_sum_check(response):
    if response['num1'] + response['num2'] == response['num3']:
        return (True, response['num3'])
    return (False, response['num3'])

# task posting to slack depending on the outcome of the above check
# and returning the server response
@task.python
def post_to_slack(sum_check_result):
    slack_hook = SlackHook(slack_conn_id='hook_tutorial_slack_conn')

    if sum_check_result[0] == True:
        server_response = slack_hook.call(api_method='chat.postMessage',
                        json={"channel": "#test-airflow",
                        "text": f"""All is well in your bucket!
                        Correct sum: {sum_check_result[1]}!"""})
    else:
        server_response = slack_hook.call(api_method='chat.postMessage',
                        json={"channel": "#test-airflow",
                        "text": f"""A test on your bucket contents failed!
                        Target sum not reached: {sum_check_result[1]}"""})

    # return the response of the API call (for logging or use downstream)
    return server_response

# implementing the DAG
with DAG(dag_id='hook_tutorial',
        start_date=datetime(2022,5,20),
        schedule_interval='@daily',
        catchup=False,
        ) as dag:

    # the dependencies are automatically set by XCom
    response = read_keys_form_s3()
    sum_check_result = run_sum_check(response)
    post_to_slack(sum_check_result)
```

The DAG above completes the following steps:

1. Use a decorated Python Operator with a manually implemented `S3Hook` to read three specific keys from S3 with the `read_key` method. Returns a dictionary with the file contents converted to integers.
2. With the results of the first task, use a second decorated Python Operator to complete a simple sum check. 
3. Post the result of the check to a Slack channel using the `call` method of the SlackHook and return the response from the Slack API.
