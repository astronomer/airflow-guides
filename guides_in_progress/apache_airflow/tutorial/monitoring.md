---
title: Monitoring Apache Airflow
sidebar: platform_sidebar
---

## Home Screen
This is the dashboard for all of your DAGs. From here you can get an overview for what is happening across all workflows for your organization.

## Dashboard Columns
Some of the high-level items you can glean from a glance are:

* Is DAG paused or running?
* Schedule
  - How often should this DAG be running?
* Owner
  - Who should I contact when this DAG is not working properly?
* Recent Tasks
  - From the most recent run of this workflow, what is the count for each status in that DAG run?
* Last Run
  - Last active run for that DAG. If this column is empty your DAG is call caught up.
* DAG Runs
  - The final states and counts of each state for all DAG runs for that DAG

## States

A list of the various states you may see a DAG run or task instance in:

* Success
* Running
* Failed
* Skipped (Task State Only)
* Retry (Task State Only)
* Queued (Task State Only)
* No Status

## Alerts

### Email
This method is best when you want to selectively email users who may be dependent on the outcome of workflows. Like most things in Airflow there a some options of how you can accomplish this task.

#### Email in Default Args
Most DAGs will be defined with a set of default arguments (default_args) that are passed to every task instance in your workflow.
You can include parameters about email alerts on retries and failures in these arguments.

* `email`
  - A string representation of an email or a list of emails
* `email_on_retry`
  - A boolean representing whether or not to send an email to `email` on retry
* `email_on_failure`
  - A boolean representing whether or not to send an email to `email` on failure

[Example](https://airflow.incubator.apache.org/tutorial.html?highlight=email)

#### Custom Messaging Tasks
Thanks to community contributed operators such as the [Slack](https://airflow.incubator.apache.org/_modules/slack_operator.html) or [email](https://pythonhosted.org/airflow/_modules/email_operator.html) operator, you can send notifications for success, failure, or other custom events as they happen.

##### Message on Success
In some cases, you may want to be notified when a workflow succeeds. An easy way to do this is to add a task downstream from the rest of your tasks that sends a notification.

##### Message on Failure
Depending on your use-case, there's different ways you can handle failure notifications. The failure emails and Slack operator are can all be highly customized and built-on.
In some cases when you have more complex logic, you can change the [trigger rule](https://pythonhosted.org/airflow/concepts.html?highlight=trigger_rule#trigger-rules) and define custom logic for different scenarios.
