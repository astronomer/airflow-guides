---
title: "Rerunning Airflow DAGs"
description: "How to use catchup, backfill, and cleared task instances in Airflow."
date: 2021-11-04T00:00:00.000Z
slug: "rerunning-dags"
tags: ["DAGs"]
---

## Overview

Running DAGs whenever you want is one of the most powerful and flexible features of Airflow. Scheduling DAGs can ensure future DAG runs happen at the right time, but you also have options for running DAGs in the past. For example, you might need to run a DAG in the past if:

- You need to rerun a failed task for one or multiple DAG runs.
- You want to deploy a DAG with a start date of one year ago and trigger all DAG runs that would have been scheduled in the past year.
- You have a running DAG and realize you need it to process data for two months prior to the DAG's start date.

All of this is possible in Airflow! In this guide, we'll cover the best ways for accomplishing use cases like rerunning tasks or DAGs and triggering historical DAG runs, including the Airflow concepts of catchup and backfill. If you're looking for additional info on basic DAG scheduling, check out the complementary [Scheduling in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow) guide.

## Rerunning Tasks

[Rerunning tasks](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html#re-run-tasks) or full DAGs in Airflow is a common workflow. Maybe one of your tasks failed due to an issue in an external system, and after fixing the problem you want to rerun that particular task instance.

The easiest way to rerun a task in Airflow is to clear the task status. Doing so updates two values in the metastore, causing the task to rerun: `max_tries` updates to `0`, and the current task instance state updates to `None`.

To clear the task status, go to the Graph View or Tree View in the UI and click on the task instance you want to rerun. Then under **Task Actions**, select **Clear** as shown in the screenshot below. 

![Clear Task Status](https://assets2.astronomer.io/main/guides/re-running-dags/clear_tasks_ui.png)

When clearing a task instance, you can select from the following options to clear and rerun additional related task instances:

- **Past:** Clears any instances of the task in DAG runs with a data interval before the selected task instance
- **Future:** Clears any instances of the task in DAG runs with a data interval after the selected task instance
- **Upstream:** Clears any tasks in the current DAG run which are upstream from the selected task instance
- **Downstream:** Clears any tasks in the current DAG run which are downstream from the selected task instance
- **Recursive:** Clears any task instances of the task in the child DAG and any parent DAGs (if you have cross-DAG dependencies)
- **Failed:** Clears only failed instances of any task instances selected based on the above options

Once you make your selections and click 'Clear', the Airflow UI shows a summary of the task instances that will be cleared and asks you to confirm. Use this to ensure your selections are applied as intended.

![Task Instance Summary](https://assets2.astronomer.io/main/guides/re-running-dags/task_instance_confirmation.png)

You can also use the Airflow CLI to clear task statuses:

``` bash
airflow tasks clear [-h] [-R] [-d] [-e END_DATE] [-X] [-x] [-f] [-r]
                    [-s START_DATE] [-S SUBDIR] [-t TASK_REGEX] [-u] [-y]
                    dag_id
```

For more info on the positional arguments for the `clear` command, check out the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html#clear).

> **Note:** Do not attempt to clear or change task statuses directly in the Airflow metastore. This can cause unexpected behavior in Airflow if not done properly. The Airflow UI and CLI functionality are there to ensure users can accomplish these tasks without breaking anything.

Finally, if you want to clear a full DAG run (all tasks in that DAG), go to the Tree View in the UI, click on the DAG circle and select 'Clear'. 

![Clear DAG Status](https://assets2.astronomer.io/main/guides/re-running-dags/clear_dag_ui.png)

### Clearing Tasks in Bulk

Sometimes you may need to rerun many tasks or DAGs at the same time. Rather than manually clicking on every task you need to rerun, you can clear task statuses in bulk. To do so:

1. In the Airflow UI, go to the **Browse** tab and click on the **Task Instances** view. 
2. Select any tasks that you want to rerun
3. Click on the Actions drop down and select **Clear**.

![Clear Task Bulk](https://assets2.astronomer.io/main/guides/re-running-dags/bulk_clear_tasks.png)

To rerun entire DAGs in bulk, you can follow a similar process by going to the **DAG Runs** view (under the **Browse** tab), selecting the DAG runs you want to rerun, and selecting **Clear the State** under the Actions drop down.

![Clear DAGs Bulk](https://assets2.astronomer.io/main/guides/re-running-dags/bulk_clear_dags.png)

## Catchup

To take another of our use cases described earlier: What if we developed a new DAG and are about to deploy it to our Airflow instance, but we want that DAG to process data starting a year ago? Airflow makes it easy to accomplish this use case with a built-in DAG argument called [catchup](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html#catchup).

When the catchup parameter for a DAG is set to `True`, at the time the DAG is turned on in Airflow the scheduler will kick off a DAG run for every data interval that has not been run between the DAG's `start_date` and the current data interval. For example, if our DAG is scheduled to run daily and has a `start_date` of 1/1/2021, and we deploy that DAG and turn it on on 2/1/2021, Airflow will schedule and kick off all of the daily DAG runs for January. Catchup will also be triggered if you turn a DAG off for a period of time and then turn it on again.

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

Catchup is a powerful feature, but it can also be dangerous, especially since it defaults to `True`. For example, if you deploy a DAG that runs every 5 minutes with a start date of 1 year ago and don't set catchup to `False`, Airflow will schedule **many** DAG runs all at once. When using catchup, it is important to keep in mind what resources Airflow has available and how many DAG runs you can support at one time. Additionally, there are a few other parameters to consider using in conjunction with catchup that can help you to not overload your scheduler or external systems: 

- `max_active_runs`: This parameter is set at the DAG level and limits the number of DAG runs that Airflow will execute for that particular DAG at any given time. For example, if you set this value to 3 and the DAG had 15 catchup runs to complete, they would be executed in 5 chunks of 3 runs.
- `depends_on_past`: This parameter is set at the task level (or as a `default_arg` for all tasks at the DAG level). When set to `True`, the task instance must wait for the same task in the most recent DAG run to be successful. This ensures sequential data loads and effectively allows only one DAG run to be executed at a time in most cases.
- `wait_for_downstream`: This parameter is set at the DAG level, and it's like a DAG-level implementation of `depends_on_past`: The entire DAG needs to run successfully for the next DAG run to start.
- `catchup_by_default`: This parameter is set at the Airflow level (in your `airflow.cfg` or as an environment variable). If you set this parameter to `False` all DAGs in your Airflow environment will not catchup unless you explicitly turn it on.

Additionally, if you want to deploy your DAG with catchup enabled but there are some tasks you don't want to run during the catchup (e.g. notification tasks), you can use the [`LatestOnlyOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/latestonlyoperator) in your DAG. This operator only runs during the DAG's most recent schedule interval. In every other DAG run it is skipped, along with any tasks downstream of it.

## Backfill

Backfilling in Airflow addresses the final use case we presented in the Overview section: we have a DAG already deployed and running, and realize we want to use that DAG to process data prior to the DAG's start date. [Backfilling](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html#backfill) is the concept of running a DAG for a specified historical period. Unlike with catchup, which will trigger missed DAG runs from the DAG's `start_date` through the current data interval, backfill periods can be specified explicitly and can include periods prior to the DAG's `start_date`. 

Backfilling can be accomplished in Airflow using the CLI. You simply specify the DAG ID, as well as the start date and end date for the backfill period. This command runs the DAG for all intervals between the start date and end date. DAGs in your backfill interval are still rerun even if they already have DAG runs.

```bash
airflow dags backfill [-h] [-c CONF] [--delay-on-limit DELAY_ON_LIMIT] [-x]
                      [-n] [-e END_DATE] [-i] [-I] [-l] [-m] [--pool POOL]
                      [--rerun-failed-tasks] [--reset-dagruns] [-B]
                      [-s START_DATE] [-S SUBDIR] [-t TASK_REGEX] [-v] [-y]
                      dag_id
```

For example, `airflow dags backfill -s 2021-11-01 -e 2021-11-02 example_dag` backfills `example_dag` from November 1st-2nd 2021. For more on other available parameters for this command, check out the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html#backfill). 

There are a couple of things to keep in mind when using backfill:

- Consider your available resources. If your backfill will trigger many DAG runs, you may want to use some of the parameters described in the Catchup section above in your DAG.
- Clearing the task or DAG status of a backfilled DAG run **does not** trigger the task/DAG to be rerun.

If you don't have access to the Airflow CLI (for example, if you are running Airflow with Astronomer Nebula), there are a couple of workarounds you can use to achieve the same functionality as backfilling:

- Deploy a copy of the DAG with a new name and a start date that is the date you want to backfill to. Airflow will consider this a separate DAG so you won't see all the DAG runs/task instances in the same place, but it would accomplish running the DAG for data in the desired time period.
- If you have a small number of DAG runs to backfill, you can trigger them manually from the Airflow UI and choose the desired logical date.

    ![Trigger Execution Date](https://assets2.astronomer.io/main/guides/re-running-dags/trigger_execution_date.png)
