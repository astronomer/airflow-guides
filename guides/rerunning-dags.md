---
title: "Re-running Airflow DAGs"
description: "How to use catchup, backfill, and cleared task instances to re-run DAGs in Airflow."
date: 2021-11-05T00:00:00.000Z
slug: "rerunning-dags"
tags: ["DAGs"]
---

## Overview

Making your DAGs run when you want is one of the most powerful and flexible features of Airflow. Scheduling DAGs can ensure future DAG runs happen at the right time, but you also have options for runs in the past. For example, what if you have a use case like one of the following:

- You need to re-run a failed task for a particular DAG run, either singular, or in bulk.
- You want to deploy a DAG with a start date of one year ago and trigger all DAG runs that would have been scheduled in the past year.
- You have a running DAG and realize you need it to process data for two months prior to the DAG's start date.

All of this is possible in Airflow! In this guide, we'll cover the best ways for accomplishing use cases like re-running tasks or DAGs and triggering historical DAG runs, including the Airflow concepts of catchup and backfill. If you're looking for additional info on basic DAG scheduling, check out this complementary [Scheduling in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow) guide.

## Re-running Tasks

[Re-running tasks](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html#re-run-tasks) or full DAGs in Airflow is a common use case. Maybe one of your tasks failed due to an issue in an external system, and after fixing the problem you want to re-run that particular task instance.

The easiest way to re-run a task in Airflow is to clear the task status. Doing so will update two things in the metastore which will cause the task to be re-run: `max_tries` will be updated to `0`, and the current task instance state will be updated to `None`.

To clear the task status, go to the Graph View or Tree View in the UI and click on the task instance you want to re-run. Then under Task Actions, select Clear, as shown in the screenshot below. 

SCREENSHOT HERE

There are multiple selections you can make when clearing the task that allow you to clear more than a single task:

- Past: Will also clear any instances of that task in DAG runs with a data interval before the run being cleared.
- Future: Will also clear any instances of that task in DAG runs with a data interval after the run being cleared.
- Upstream: Will also clear any upstream tasks in the current DAG run.
- Downstream: Will also clear any downstream tasks in the current DAG run.
- Recursive: Will clear all tasks instances in the child DAG and any parent DAGs (if you have cross-DAG dependencies).
- Failed: Of the task instances chosen based on other selections, only failed instances will be cleared.

Once you make your selections and click 'Clear', the Airflow UI will show a summary of the task instances that will be cleared and ask you to confirm. Use this to ensure your selections will be applied as you intended.

SCREENSHOT HERE

You can also use the Airflow CLI to clear task statuses:

``` bash
airflow tasks clear [-h] [-R] [-d] [-e END_DATE] [-X] [-x] [-f] [-r]
                    [-s START_DATE] [-S SUBDIR] [-t TASK_REGEX] [-u] [-y]
                    dag_id
```

For more info on the positional arguments for the `clear` command, check out the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html#clear).

> **Note:** Do not attempt to clear or change task statuses directly in the Airflow metastore. This can cause unexpected behavior in Airflow if not done properly. The Airflow UI and CLI functionality are there to ensure users can accomplish these tasks without breaking anything.

Finally, if you want to clear a full DAG run (all tasks in that DAG), in the Tree View in the UI you can click on the DAG circle and select 'Clear'. 

SCREENSHOT HERE

## Catchup


### Use additional parameters when scheduling catchups

Deploying a DAG with **`catchup=True`** can fit a use case, but consider using additional scheduling parameters for added safety.

**`depends_on_past`**: When set to `True`, task instance will run chronologically sequentially, relying on the previously scheduled task instance to succeed before executing.

This will ensure sequential data loads, but may also stop progress if a job is left to run unmonitored.

**`wait_for_downstream`**: A stronger version of `depends_on_past` that is extended to a DAG level instead of a task level. The entire DAG will need to run successfully for the next DAG run to start.

## Backfill

There are a few additional best practices to consider when using backfill:

- Consider your available resources


## Notes while in development
We should write a doc that covers:

the Airflow CLI backfill command not being super reliable (yet)
scheduling best practices
resource considerations

### LatestOnlyOperator - where does this fit in??
