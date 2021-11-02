---
title: "Re-running Airflow DAGs"
description: "How to use catchup, backfill, and cleared task instances in Airflow."
date: 2021-11-05T00:00:00.000Z
slug: "rerunning-dags"
tags: ["DAGs"]
---

## Overview

Making your DAGs run when you want is one of the most powerful and flexible features of Airflow. Scheduling DAGs can ensure future DAG runs happen at the right time, but you also have options for DAG runs in the past. For example, what if you have a use case like one of the following:

- You need to re-run a failed task for a particular DAG run, either singular, or in bulk.
- You want to deploy a DAG with a start date of one year ago and trigger all DAG runs that would have been scheduled in the past year.
- You have a running DAG and realize you need it to process data for two months prior to the DAG's start date.

All of this is possible in Airflow! In this guide, we'll cover the best ways for accomplishing use cases like re-running tasks or DAGs and triggering historical DAG runs, including the Airflow concepts of catchup and backfill. If you're looking for additional info on basic DAG scheduling, check out this complementary [Scheduling in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow) guide.

## Re-running Tasks

[Re-running tasks](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html#re-run-tasks) or full DAGs in Airflow is a common use case. Maybe one of your tasks failed due to an issue in an external system, and after fixing the problem you want to re-run that particular task instance.

The easiest way to re-run a task in Airflow is to clear the task status. Doing so will update two things in the metastore which will cause the task to be re-run: `max_tries` will be updated to `0`, and the current task instance state will be updated to `None`.

To clear the task status, go to the Graph View or Tree View in the UI and click on the task instance you want to re-run. Then under Task Actions, select Clear, as shown in the screenshot below. 

SCREENSHOT HERE

There are multiple selections you can make when clearing the task instance that allow you to clear more than the task selected:

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

Finally, if you want to clear a full DAG run (all tasks in that DAG), go to the Tree View in the UI, click on the DAG circle and select 'Clear'. 

SCREENSHOT HERE

### Clearing Tasks in Bulk

Sometimes you may need to re-run many tasks or DAGs at the same time. Rather than manually clicking on every task you need to re-run, you can clear task statuses in bulk. In the Airflow UI, go to the Browse tab and click on the Task Instances view. Then select any tasks you want to re-run, click on the Actions drop down, and select Clear.

SCREENSHOT HERE

To re-run entire DAGs in bulk, you can follow a similar process by going to the DAG Runs view (under the Browse tab), selecting the DAG runs you want to re-run, and selecting Clear the State under the Actions drop down.

SCREENSHOT HERE

## Catchup

Taking another of our use cases described above, what if we just developed a new DAG and are about to deploy it to our Airflow instance, but we want that DAG to process data starting a year ago. Airflow makes it easy to accomplish this use case with a built-in DAG argument called [catchup](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html#catchup).

When the catchup parameter for a DAG is set to `True`, at the time the DAG is turned on in Airflow the scheduler will kick off a DAG run for every data interval that has not been run between the DAG's `start_date` and the current data interval. For example, if my DAG is scheduled to run daily and has a `start_date` of 1/1/2021, and I deploy that DAG and turn it on on 2/1/2021, Airflow would schedule and kick off all of the daily DAG runs for January. Catchup will also be triggered if you turn a DAG off for a period of time and then turn it on again.

Catchup can be controlled by setting the parameter in your DAG's arguments (by default, catchup is set to `True`). For example, this DAG would *not* make use of catchup:

```python
with DAG(
    dag_id="example_dag",
    start_date=datetime(2021, 10, 9), 
    max_active_runs=1,
    timetable=UnevenIntervalsTimetable(),
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=3),
    },
    catchup=False
) as dag:
```

Catchup is a powerful feature, but it can also be dangerous, especially since it defaults to `True`. For example, if you deploy a DAG that runs every 5 minutes with a start date of 1 year ago and don't set catchup to `False`, Airflow will schedule **many** DAG runs all at once. When using catchup, it is important to keep in mind what resources Airflow has available and how many DAG runs you can support at one time. Additionally, there are a few other parameters to consider using in conjunction with catchup that can help ensure you don't overload your scheduler or systems your DAG are interacting with.

- **`max_active_runs`:** This parameter is set at the DAG level and limits the number of DAG runs that Airflow will execute for that particular DAG at any given time. For example, if you set this value to 3 and the DAG had 15 catchup runs to complete, they would be executed in 5 chunks of 3 runs.
- **`depends_on_past`**: This parameter is set at the task level (or can be set as a `default_arg` for all tasks in a DAG). When set to `True`, the task instance must wait for the same task in the most recent DAG run to be successful. This will ensure sequential data loads and effectively allows only one DAG run to be executed at a time in most cases.
- **`wait_for_downstream`**: This parameter is set at the DAG level, and is kind of like `depends_on_past` but extended to a DAG level instead of a task level. The entire DAG will need to run successfully for the next DAG run to start.
- **`catchup_by_default`**: This parameter is set at the Airflow level (in your `airflow.cfg` or as an environment variable). If you set this parameter to `False` all DAGs in your Airflow environment will not catchup unless you explicitly turn it on.




## Backfill

There are a few additional best practices to consider when using backfill:

- Consider your available resources


### LatestOnlyOperator - where does this fit in??
