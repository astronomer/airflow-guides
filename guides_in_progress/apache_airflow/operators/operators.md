---
title: Apache Airflow Operators
sidebar: platform_sidebar
---

In this document, you will find descriptions of current operators, along with the logic and parameters that need to be defined each one.

## BaseOperator
As mentioned above, all operators are derived from `BaseOperator` and acquire much of their functionality through inheritance. Being that `BaseOperator` is the [Lucy](https://en.wikipedia.org/wiki/Lucy_(Australopithecus)) of operators, we've devoted this section of documentation to understanding the parameters of it. These parameters represent building blocks that can be leveraged in your DAGs.

**Parameters**

  * **task_id** (_string_) - A meaningful id that serves as a unique identifier for each task.
  * **owner** (_string_) - The owner of the task. A good practice is to use the Unix username here.
  * **retires** (_int_) - The number of retries that should be performed before failing the task.
  * **retry_delay** (_timedelta_) - How long the delay between retries should be.
  * **retry_exponential_backoff** (_bool_) - This allows progressively longer delays between retries. Note that the delay will be converted into seconds.
  * **max_retry_delay** (_timedelta_) - The maximum delay interval between retries.
  * **start_date** (_datetime_) - This determines the `execution_date` for the first task instance.
      - Tip: The best practice is to have the start_date rounded to your DAG's `schedule_interval`. So, daily jobs should have `start_date` with time 00:00:00 and hourly jobs should have their `start_date` at 00:00 of a specific hour.
  * **end_date** (_datetime_) - If specified, the scheduler won't go beyond this date.
  * **depends_on_past** (_bool_) - When set to 'True', task instances will run sequentially while relying on the previous task's schedule to succeed. The task instance for the `start_date` is allowed to run despite this.
  * **wait_for_downstream** (_bool_) - When set to 'True', an instance of task B will wait for tasks immediately downstream of the previous instance of task B to finish successfully before it runs. This is useful when different instances of a task alter the same asset and that asset is used by further downstream tasks.
      - Note: `depends_on_past` is automatically 'True' whenever `wait_for_downstream` is used.
  * **queue** (_str_) - Points the executor to the right queue to target for a job.
  * **dag** (_DAG_) - A reference to the DAG the task is attached to.
  * **priority_weight** (_int_) - Priority weight of this task against other tasks. This allows the executor to trigger higher priority tasks before others when there is a backlog.
  * **pool** (_str_) - The slot pool this task should run in. Slot pools are a way to limit concurrency for certain tasks.
  * **sla** (_datetime.timedelta_) - This is the time by which the job is expected to succeed.
      - Note: This represents the `timedelta` after the period is closed. The scheduler pays special attention to jobs with an SLA and sends alert emails for SLA misses.
  * **execution_timeout** (_datetime.timedelta_) - Maximum time allowed for the execution of this task instance.
  * **on_failure_callback** (_callable_) - A function to be called when a task instance of this task fails. A context dictionary is passed as a single parameter to this function.
  * **on_retry_callback** (_callable_) - Much like the `on_failure_callback` except this is executed when retries occur.
  * **on_success_callback** (_callable_) - Much like the `on_failure_callback` except this is executed when the task is successful.
  * **trigger_rule** (_str_) - Defines the rule by which dependencies are applied for the task to get triggered.
      - Options for `trigger_rule` are: `{ all_success | all_failed | all_done | one_success | one_failed | dummy}` and defaults to `all_success`.
  * **resources** (_dict_) - A map of resource parameter names to their values.
  * **run_as_user** (_str_) - Unix username to impersonate while running the task.

#### BaseSenseOperator

  All sensors are derived from `BaseSenseOperator` and inherit `timeout` and `poke_interval` in addition to the `BaseOperator` attributes.

  **Parameters**

  * **soft_fail** (_bool_) - Set to `True` to mark the task as SKIPPED on failure.
  * **poke_interval** (_int_) - Time in seconds that the job should wait in between each try.
  * **timeout** (_int_) - Time in seconds before the task times out and fails.

  Thanks to the Apache Airflow project & community, there is a large base of operators already available for use.

  * [Apache Airflow](https://github.com/apache/incubator-airflow/tree/master/airflow/operators)
  * [Community](https://github.com/apache/incubator-airflow/tree/master/airflow/contrib/operators)
