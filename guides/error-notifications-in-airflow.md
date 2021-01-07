---
title: "Error Notifications in Airflow"
description: "Managing Error Notifications"
date: 2018-05-21T00:00:00.000Z
slug: "error-notifications-in-airflow"
heroImagePath: null
tags: ["DAGs", "Integrations", "Operators"]
---

## Error Reporting on Airflow

Email notifications are great for monitoring Airflow workflows. They can be sent for failures, successes, and retries.


### Setting Notifications at the DAG level

Notifications set at the DAG level filter down to each task in the DAG - generally in the `default_args`.

By default, `email_on_failure` is set to `True`


```python
from datetime import datetime
from airflow import DAG

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2018, 1, 30),
    'email': ['viraj@astronomer.io']
}

with DAG('sample_dag',
          default_args=default_args,
          schedule_interval='@daily',
          catchup=False) as dag:
    ...
```

Any task in this DAG's context will send a failure email to all addresses in the emails array

### Different Levels of Notifications

Failure notifications are the most common, but different levels can be set where appropriate.

Emails on retries are great for testing if failures are by caused extraneous factors like load on an external system. If this is the case, consider setting `retry_exponential_backoff` to `True`.

[BaseOperator](https://github.com/apache/airflow/blob/60a032f4b829eb41b84c907ff663560d50284989/airflow/models/baseoperator.py#L270)


```python
from datetime import datetime, timedelta
from airflow import DAG

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2018, 1, 30),
    'email': ['viraj@astronomer.io'],
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

### Isolating Tasks

For some use cases, it might be helpful to only have failure emails for certain tasks. The BaseOperator that all Airflow Operators inherit from has support for these arguments if you don't want them defined at the DAG level.

[BaseOperator](https://github.com/apache/airflow/blob/60a032f4b829eb41b84c907ff663560d50284989/airflow/models/baseoperator.py#L265)


```python
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2018, 1, 30),
    'email_on_failure': False,
    'email': ['viraj@astronomer.io'],
    'retries': 1

}

with DAG('sample_dag',
          default_args=default_args,
          schedule_interval='@daily',
          catchup=False) as dag:

    wont_email = DummyOperator(
      task_id='wont_email')

    will_email = DummyOperator(
      task_id='will_email',
      email_on_failure=True)
    ...
```

### Customizing Email Notifications

By default, email notifications have a default format that includes standard information as defined in the [__`email_alert`__](https://github.com/apache/incubator-airflow/blob/master/airflow/models.py#L1949) method of the TaskInstance class.


```python
def email_alert(self, exception):
    task = self.task
    title = "Airflow alert: {self}".format(**locals())
    exception = str(exception).replace('\n', '<br>')

    # For reporting purposes, we report based on 1-indexed,
    # not 0-indexed lists (i.e. Try 1 instead of
    # Try 0 for the first attempt).
    body = (
        "Try {try_number} out of {max_tries}<br>"
        "Exception:<br>{exception}<br>"
        "Log: <a href='{self.log_url}'>Link</a><br>"
        "Host: {self.hostname}<br>"
        "Log file: {self.log_filepath}<br>"
        "Mark success: <a href='{self.mark_success_url}'>Link</a><br>"
    ).format(try_number=self.try_number, max_tries=self.max_tries + 1, **locals())

    send_email(task.email, title, body)
```

This can be modified greatly by simply overriding this method. Try dropping the below into an existing dag and see what happens.


```python
from airflow.utils.email import send_email
from airflow.hooks import PostgresHook

def hello_world(**kwargs):
    ti = kwargs.get('task_instance')
    task = kwargs.get('task')

    def new_email_alert(self, **kwargs):
        title = "TEST MESSAGE: THIS IS A MODIFIED TEST"
        body = ("I've now modified the email alert "
                "to say whatever I want it to say.<br>")
        send_email(task.email, title, body)

    ti.email_alert = new_email_alert

    # intentionally fail the task by calling get_records()
    # without providing positional argument "sql"

    hook = PostgresHook('hook-name')
    return hook.get_records()

t0 = PythonOperator(task_id='hello_world',
                    python_callable=hello_world,
                    provide_context=True,
                    dag=dag)
```

If you want a custom email for another type of operator, you can use `on_failure_callback` and the `send_email` utility provided by Airflow.

```python
from airflow.utils.email import send_email

def failure_email(context):  

    email_title = "Airflow Task {tak_id} Failed".format(context['task_instance'].task_id)

    email_body = "{task_id} in {dag_id} failed.".format(context['task_instance'].task_id, context['task_instance'].dag_id)

    send_email('you_email@address.com', email_title, email_body)
```

### Setting Up Alerts in Slack

At Astronomer, we drop Airflow notifications in shared slack channels instead of emails. There are a few ways to accomplish this:

#### Adding a Slack Integration

Add this integration: `https://slack.com/apps/A0F81496D-email` and pick a channel to drop alerts in.

The email address generated can be added to the list of emails like any other:


```python
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2018, 1, 30),
    'email': ['GENERATED_CHANNEL_ID@astronomerteam.slack.com']
}


dag = DAG('sample_dag',
          default_args=default_args,
          schedule_interval='@daily',
          catchup=False)

with dag:
    d = DummyOperator(
    task_id='test')
    ...
```

![SlackNotifications](https://assets2.astronomer.io/main/guides/dag_failure_notification.png)


Alternatively, a `SlackOperator` can be used.

```python
t2 = SlackAPIPostOperator(task_id='post_slack_{0}'.format(job['source']),
                                  username='ETL',
                                  slack_conn_id='slack_conn',
                                  text="My job {0} finished".format(
                                      job['source']),
                                  channel='workflow_status')
```
