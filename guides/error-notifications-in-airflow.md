---
title: "Error Notifications in Airflow"
description: "Methods for managing notifications in your Airflow DAGs."
date: 2018-05-21T00:00:00.000Z
slug: "error-notifications-in-airflow"
heroImagePath: null
tags: ["DAGs", "Integrations", "Operators"]
---

## Overview

A key question when using any data orchestration tool is "How do I know if something has gone wrong?". Airflow users always have the option to check the UI to see the status of their DAGs, but this is an inefficient way of managing errors systematically, especially if certain failures need to be addressed promptly or by multiple team members. Fortunately, Airflow has built-in notification mechanisms that can be leveraged to configure error notifications in a way that works for your team. 

In this guide, we'll cover the basics of Airflow notifications and how to set up common notification mechanisms including email, Slack, and SLAs. We'll also discuss how to make the most of Airflow alerting when using the Astronomer platform.

## Airflow Notification Basics

Airflow has an incredibly flexible notification system. Having your DAGs defined as Python code gives you full autonomy to define your tasks and notifications in whatever way makes sense for your use case.

In this section we'll cover some of the options available when working with notifications in Airflow. 

### Notification Levels

Sometimes it makes sense to standardize notifications across your entire DAG. Notifications set at the DAG level will filter down to each task in the DAG. These notifications are usually defined in `default_args`.

For example, in the following DAG, `email_on_failure` is set to `True`, meaning any task in this DAG's context will send a failure email to all addresses in the `email` array.

```python
from datetime import datetime
from airflow import DAG

default_args = {
	'owner': 'airflow',
	'start_date': datetime(2018, 1, 30),
	'email': ['noreply@astronomer.io'],
	'email_on_failure': True
}

with DAG('sample_dag',
	default_args=default_args,
	schedule_interval='@daily',
	catchup=False) as dag:

...
```

In contrast, it's sometimes useful to have notifications only for certain tasks. The `BaseOperator` that all Airflow Operators inherit from has support for built-in notification arguments, so you can configure each task individually as needed. In the DAG below, email notifications are turned off by default at the DAG level, but are specifically enabled for the `will_email` task.

```python
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

default_args = {
	'owner': 'airflow',
	'start_date': datetime(2018, 1, 30),
	'email_on_failure': False,
	'email': ['noreply@astronomer.io'],
	'retries': 1
}

with DAG('sample_dag',
	default_args=default_args,
	schedule_interval='@daily',
	catchup=False) as dag:

	wont_email = DummyOperator(
		task_id='wont_email'
	)
	
	will_email = DummyOperator(
		task_id='will_email',
		email_on_failure=True
	)
```

### Notification Triggers

The most common trigger for notifications in Airflow is a task failure. However, notifications can be set based on other events, including retries and successes.

Emails on retries can be useful for debugging indirect failures; if a task needed to retry but eventually succeeded, this might indicate that the problem was caused by extraneous factors like load on an external system. To turn on email notifications for retries, simply set the `email_on_retry` parameter to `True` as shown in the DAG below.

```python
from datetime import datetime, timedelta
from airflow import DAG

default_args = {
	'owner': 'airflow',
	'start_date': datetime(2018, 1, 30),
	'email': ['noreply@astronomer.io'],
	'email_on_failure': True,
	'email_on_retry': True,
	'retry_exponential_backoff': True,
	'retry_delay' = timedelta(seconds=300)
	'retries': 3
}

with DAG('sample_dag',
	default_args=default_args,
	schedule_interval='@daily',
	catchup=False) as dag:

...
```

When working with retries, you should configure a `retry_delay`. This is the amount of time between a task failure and when the next try will begin. You can also turn on `retry_exponential_backoff`, which progressively increases the wait time between retries. This can be useful if you expect that extraneous factors might cause failures periodically.

### Custom Notifications

The email notification parameters shown in the sections above are an example of built-in Airflow alerting mechanisms. These simply have to be turned on and don't require any configuration from the user.

You can also define your own notifications to customize how Airflow alerts you about failures or successes. The most straightforward way of doing this is by defining `on_failure_callback` and `on_success_callback` Python functions. These functions can be set at the DAG or task level, and the functions will be called when a failure or success occurs respectively. For example, the following DAG has a custom `on_failure_callback` function set at the DAG level and an `on_success_callback` function for just the `success_task`.

```python
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

def custom_failure_function(context):
	"Define custom failure notification behavior"
	dag_run = context.get('dag_run')
	task_instances = dag_run.get_task_instances()
	print("These task instances failed:", task_instances)

def custom_success_function(context):
	"Define custom success notification behavior"
	dag_run = context.get('dag_run')
    task_instances = dag_run.get_task_instances()
    print("These task instances succeeded:", task_instances)

default_args = {
	'owner': 'airflow',
	'start_date': datetime(2018, 1, 30),
	'on_failure_callback': custom_failure_function
	'retries': 1
}

with DAG('sample_dag',
		default_args=default_args,
		schedule_interval='@daily',
		catchup=False) as dag:

	failure_task = DummyOperator(
		task_id='failure_task'
	)
	
	success_task = DummyOperator(
		task_id='success_task',
		on_success_callback=custom_success_function
	)
```

Note that custom notification functions can also be used to send email notifications. For example, if you want to send emails for successful task runs, you can define an email function in your `on_success_callback`, which may look something like this:

```python
from airflow.utils.email import send_email

def success_email_function(context):
    dag_run = context.get('dag_run')

    msg = "DAG ran successfully"
    subject = f"DAG {dag_run} has completed"
    send_email(to=your_emails, subject=subject, html_content=msg)

```

This functionality may also be useful when your pipelines have conditional branching, and you want to be notified if a certain path is taken (i.e. certain tasks get run).

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="https://registry.astronomer.io/dags/slack-callback-partial-dag?banner=learn-more-banner-click">Astronomer Registry: Pipeline Alerts and Notifications for Multiple Slack Channels</a></li>
    <li data-icon="→"><a href="https://registry.astronomer.io/dags/ms-teams-callback-partial-dag?banner=learn-more-banner-click">Astronomer Registry: Pipeline Alerts and Notifications for Multiple Microsoft Teams Channels</a></li>
    <li data-icon="→"><a href="/events/webinars/dags-with-airflow-notifications?banner=learn-more-banner-click">Monitor Your DAGs with Airflow Notifications Webinar</a></li>
    <li data-icon="→"><a href="/blog/airflow-business-workflow-hightouch?banner=learn-more-banner-click">Democratizing the Data Stack—Airflow for Business Workflows</a></li>
</ul>

## Email Notifications

Email notifications are a native feature in Airflow and are easy to set up. As shown above, the `email_on_failure` and `email_on_retry` parameters can be set to `True` either at the DAG level or task level to send emails when tasks fail or retry. The `email` parameter can be used to specify which email(s) you want to receive the notification. If you want to enable email alerts on all failures and retries in your DAG, you can define that in your default arguments like this:

```python
from datetime import datetime, timedelta
from airflow import DAG

default_args = {
	'owner': 'airflow',
	'start_date': datetime(2018, 1, 30),
	'email': ['noreply@astronomer.io'],
	'email_on_failure': True,
	'email_on_retry': True,
	'retry_delay' = timedelta(seconds=300)
	'retries': 1
}

with DAG('sample_dag',
	default_args=default_args,
	schedule_interval='@daily',
	catchup=False) as dag:

...
```

In order for Airflow to send emails, you need to configure an SMTP server in your Airflow environment. You can do this by filling out the SMTP section of your `airflow.cfg` like this:

```yaml
[smtp]
# If you want airflow to send emails on retries, failure, and you want to use
# the airflow.utils.email.send_email_smtp function, you have to configure an
# smtp server here
smtp_host = your-smtp-host.com
smtp_starttls = True
smtp_ssl = False
# Uncomment and set the user/pass settings if you want to use SMTP AUTH 
# smtp_user =                       
# smtp_password =  
smtp_port = 587
smtp_mail_from = noreply@astronomer.io
```

You can also set these values using environment variables. In this case, all parameters are preceded by `AIRFLOW__SMTP__`, consistent with Airflow environment variable naming convention. For example, `smtp_host` can be specified by setting the `AIRFLOW__SMTP__SMTP_HOST` variable. For more on Airflow email configuration, check out the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/email-config.html). 

> Note: If you are running on the Astronomer platform, you can set up SMTP using environment variables since the `airflow.cfg` cannot be directly edited. For more on email alerting on the Astronomer platform, see the 'Notifications on Astronomer' section below.

### Customizing Email Notifications

By default, email notifications will be sent in a standard format as defined in the `email_alert()` and `get_email_subject_content()` methods of the `TaskInstance` class. The default email content is defined like this:

```python
default_subject = 'Airflow alert: {{ti}}'
# For reporting purposes, we report based on 1-indexed,
# not 0-indexed lists (i.e. Try 1 instead of
# Try 0 for the first attempt).
default_html_content = (
    'Try {{try_number}} out of {{max_tries + 1}}<br>'
    'Exception:<br>{{exception_html}}<br>'
    'Log: <a href="{{ti.log_url}}">Link</a><br>'
    'Host: {{ti.hostname}}<br>'
    'Mark success: <a href="{{ti.mark_success_url}}">Link</a><br>'
)
```

To see the full method, check out the source code [here](https://github.com/apache/airflow/blob/main/airflow/models/taskinstance.py#L1802).

You can overwrite this default with your custom content by setting the `subject_template` and/or `html_content_template` variables in your `airflow.cfg` with the path to your jinja template files for subject and content respectively.

## Slack Notifications

Sending notifications to Slack is another common way of alerting with Airflow.

There are multiple ways you can send messages to Slack from Airflow. In this guide, we'll cover how to use the [Slack Provider's](https://registry.astronomer.io/providers/slack) `SlackWebhookOperator` with a Slack Webhook to send messages, since this is Slack's recommended way of posting messages from apps. To get started, follow these steps:

 1. From your Slack workspace, create a Slack app and an incoming Webhook. The Slack documentation [here](https://api.slack.com/messaging/webhooks) walks through the necessary steps. Make note of the Slack Webhook URL to use in your Python function.
 2. Create an Airflow connection to provide your Slack Webhook to Airflow. Choose an HTTP connection type (if you are using Airflow 2.0 or greater, you will need to install the `apache-airflow-providers-http` provider for the HTTP connection type to appear in the Airflow UI). Enter [`https://hooks.slack.com/services/`](https://hooks.slack.com/services/) as the Host, and enter the remainder of your Webhook URL from the last step as the Password (formatted as `T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`). 

    ![Slack Connection](https://assets2.astronomer.io/main/guides/error-notifications/slack_webhook_connection.png)

 3. Create a Python function to use as your `on_failure_callback` method. Within the function, define the information you want to send and invoke the `SlackWebhookOperator` to send the message. Here's an example:

    ```python
    from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

    def slack_notification(context):
        slack_msg = """
                :red_circle: Task Failed. 
                *Task*: {task}  
                *Dag*: {dag} 
                *Execution Time*: {exec_date}  
                *Log Url*: {log_url} 
                """.format(
                task=context.get('task_instance').task_id,
                dag=context.get('task_instance').dag_id,
                ti=context.get('task_instance'),
                exec_date=context.get('execution_date'),
                log_url=context.get('task_instance').log_url,
            )
        failed_alert = SlackWebhookOperator(
            task_id='slack_notification',
            http_conn_id='slack_webhook',
            message=slack_msg)
        return failed_alert.execute(context=context)
    ```

    > Note: in Airflow 2.0 or greater, to use the `SlackWebhookOperator` you will need to install the `apache-airflow-providers-slack` provider package.

 4. Define your `on_failure_callback` parameter in your DAG either as a `default_arg` for the whole DAG, or for specific tasks. Set it equal to the function you created in the previous step. You should now see any failure notifications show up in Slack!

## Airflow SLAs

[Airflow SLAs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html#slas) are a type of notification that you can use if your tasks are taking longer than expected to complete. If a task takes longer than a maximum amount of time to complete as defined in the SLA, the SLA will be missed and notifications will be triggered. This can be useful in cases where you have potentially long-running tasks that might require user intervention after a certain period of time, or if you have tasks that need to complete by a certain deadline. 

Note that exceeding an SLA will not stop a task from running. If you want tasks to stop running after a certain time, try using [timeouts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html#timeouts) instead.

You can set an SLA for all tasks in your DAG by defining `'sla'` as a default argument, as shown in the DAG below:

```python
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time

def my_custom_function(ts,**kwargs):
    print("task is sleeping")
    time.sleep(40)

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': 'noreply@astronomer.io',
    'email_on_retry': False,
    'sla': timedelta(seconds=30)
}

# Using a DAG context manager, you don't have to specify the dag property of each task
with DAG('sla-dag',
         start_date=datetime(2021, 1, 1),
         max_active_runs=1,
         schedule_interval=timedelta(minutes=2),
         default_args=default_args,
         catchup=False 
         ) as dag:

    t0 = DummyOperator(
        task_id='start'
    )

    t1 = DummyOperator(
        task_id='end'
    )

    sla_task = PythonOperator(
        task_id='sla_task',
        python_callable=my_custom_function
    )

    t0 >> sla_task >> t1
```

SLAs have some unique behaviors that you should consider before implementing them:

- SLAs are relative to the DAG execution date, not the task start time. For example, in the DAG above the `sla_task` will miss the 30 second SLA because it takes at least 40 seconds to complete. The `t1` task will also miss the SLA, because it is executed more than 30 seconds after the DAG execution date. In that case, the `sla_task` will be considered "blocking" to the `t1` task.
- SLAs will only be evaluated on scheduled DAG Runs. They will not be evaluated on manually triggered DAG Runs.
- SLAs can be set at the task level if a different SLA is required for each task. In this case, all task SLAs are still relative to the DAG execution date. For example, in the DAG below, `t1` has an SLA of 500 seconds. If the upstream tasks (`t0` and `sla_task`) combined take 450 seconds to complete, and `t1` takes 60 seconds to complete, then `t1` will miss its SLA even though the task did not take more than 500 seconds to execute.

```python
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import time

def my_custom_function(ts,**kwargs):
    print("task is sleeping")
    time.sleep(40)

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': 'noreply@astronomer.io',
    'email_on_retry': False
}

# Using a DAG context manager, you don't have to specify the dag property of each task
with DAG('sla-dag',
         start_date=datetime(2021, 1, 1),
         max_active_runs=1,
         schedule_interval=timedelta(minutes=2),
         default_args=default_args,
         catchup=False 
         ) as dag:

    t0 = DummyOperator(
        task_id='start',
        sla=timedelta(seconds=50)
    )

    t1 = DummyOperator(
        task_id='end',
        sla=timedelta(seconds=500)
    )

    sla_task = PythonOperator(
        task_id='sla_task',
        python_callable=my_custom_function,
        sla=timedelta(seconds=5)
    )

    t0 >> sla_task >> t1
```

Any SLA misses will be shown in the Airflow UI. You can view them by going to Browse → SLA Misses, which looks something like this:

![SLA UI](https://assets2.astronomer.io/main/guides/error-notifications/sla_ui_view.png)

If you configured an SMTP server in your Airflow environment, you will also receive an email with notifications of any missed SLAs.

![SLA Email](https://assets2.astronomer.io/main/guides/error-notifications/sla_email.png)

Note that there is no functionality to disable email alerting for SLAs. If you have an`'email'` array defined and an SMTP server configured in your Airflow environment, an email will be sent to those addresses for each DAG Run that has missed SLAs.

## Notifications on Astronomer

If you are running Airflow on the Astronomer platform, you have multiple options for managing your Airflow notifications. All of the methods above for sending task notifications from Airflow are easily implemented on Astronomer. Our documentation [here](https://www.astronomer.io/docs/enterprise/v0.25/customize-airflow/airflow-alerts) discusses how to leverage these notifications on the platform, including how to set up SMTP to enable email alerts.

Astronomer also provides deployment and platform-level alerting to notify you if any aspect of your Airflow or Astronomer infrastructure is unhealthy. For more on that, including how to customize alerts for Enterprise platform users, check out our documentation [here](https://www.astronomer.io/docs/enterprise/v0.25/monitor/platform-alerts).
