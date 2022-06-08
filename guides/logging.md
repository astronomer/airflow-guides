---
title: "Logging in Airflow"
description: "Demystifying Airflow's logging configuration."
date: 2018-09-11T00:00:00.000Z
slug: "logging"
heroImagePath: null
tags: ["Logging", "Best Practices", "Basics"]
---

## Overview

Airflow provides an extensive logging system for monitoring and debugging your data pipelines. Your webserver, scheduler, metadata database, and even individual tasks generate logs. You can export these logs to a local file, your console, or to a specified remote storage solution.

In this guide, we'll cover the basics of logging in Airflow, including:

- Where to find the logs of different Airflow components
- How to add additional task logs from within a DAG
- When and how to configure logging settings
- Remote logging.

Lastly, we walk through a step-by-step example on how to set up remote logging to an S3 bucket using the [Astro CLI](https://docs.astronomer.io/astro/cli/get-started) and show a use case of advanced configuration in an example on how to add two handlers to the task logger in Airflow.

In addition to to standard logging, Airflow provides observability features that you can use to collect metrics, trigger callback functions with task events, monitor Airflow health status, and track errors or user activity. You can find more information on monitoring options in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/index.html). Astro builds on these features, providing more detailed metrics about how your tasks run and use resources in your cloud. To learn more, see the [Astro documentation](https://docs.astronomer.io/astro/deployment-metrics).

## Logging in Airflow

Logging in Airflow leverages the [Python stdlib `logging` module](https://docs.python.org/3/library/logging.html).

The basic components of the `logging` module are the following classes:

- **Loggers** (`logging.Logger`) are the interface that the application code directly interacts with. Airflow defines 4 loggers by default: `root`, `flask_appbuilder`, `airflow.processor` and `airflow.task`.
- **Handlers** (`logging.Handler`) send log records to their destination. By default, Airflow uses `RedirectStdHandler`, `FileProcessorHandler` and `FileTaskHandler`.
- **Filters** (`logging.Filter`) determine which log records are emitted. Airflow uses `SecretsMasker` as a filter to prevent sensitive information from being printed into logs.
- **Formatters** (`logging.Formatter`) determine the layout of log records. Two formatters are predefined in Airflow: `airflow_colored` (`"[%(blue)s%(asctime)s%(reset)s] {%(blue)s%(filename)s:%(reset)s%(lineno)d} %(log_color)s%(levelname)s%(reset)s - %(log_color)s%(message)s%(reset)s"`)  and `airflow` (`"[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"`).

See the [Python documentation](https://docs.python.org/3/library/logging.html) for more information on methods available for these classes, including the attributes of a LogRecord object and the 6 available levels of logging severity (`CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, and `NOTSET`).

The four default loggers in Airflow each have a handler with a predefined log destination and formatter:

- `root` (level: `INFO`) uses `RedirectStdHandler` and `airflow_colored`. It outputs to `sys.stderr/stout` and acts as a catch-all for processes which have no specific logger defined.
- `flask_appbuilder` (level: `WARNING`) uses `RedirectStdHandler` and `airflow_colored`. It outputs to `sys.stderr/stout`. It handles logs from the webserver.
- `airflow.processor` (level: `INFO`) uses `FileProcessorHandler` and `airflow`. It writes logs from the scheduler to the local file system.
- `airflow.task` (level: `INFO`) uses `FileTaskHandlers` and `airflow`. It writes task logs to the local file system.

By default, log file names have the following format:

- For standard tasks: `dag_id={dag_id}/run_id={run_id}/task_id={task_id}/attempt={try_number}.log`
- For dynamically mapped tasks: `dag_id={dag_id}/run_id={run_id}/task_id={task_id}/map_index={map_index}/attempt={try_number}.log`

These filename formats can be reconfigured using `log_filename_template` in `airflow.cfg`.

> **Note:** The full default logging configuration can be viewed under `DEFAULT_LOGGING_CONFIG` in the [Airflow source code](https://github.com/apache/airflow/blob/c0e9daa3632dc0ede695827d1ebdbd091401e94d/airflow/config_templates/airflow_local_settings.py).

The Airflow UI shows logs using a `read()` method on task handlers which is not part of stdlib.
`read()` checks for available logs to show in a predefined order:

1. Remote logs (if remote logging is enabled)
2. Logs on the local filesystem
3. Logs from [worker specific webserver subprocesses](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#worker-log-server-port)

> **Note:** When using the Kubernetes Executor and a worker pod still exists, `read()` shows the first 100 lines from Kubernetes pod logs. If a worker pod spins down, those logs are no longer available. [The Kubernetes documentation](https://kubernetes.io/docs/concepts/cluster-administration/logging/) provides further information on its logging architecture.  

## Where To Find Logs

By default, Airflow outputs logs to the `base_log_folder` configured in `airflow.cfg`, which itself is located in your `$AIRFLOW_HOME` directory.

### Running Airflow in Docker

If you run Airflow in Docker (either using the [Astro CLI](https://docs.astronomer.io/software/install-cli) or by [following the Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)), you will find the logs of each Airflow component in different locations:

- **Scheduler** logs are in `/usr/local/airflow/logs/scheduler` within the scheduler Docker container by default (you can enter a docker container in a bash session with `docker exec -it <container_id> /bin/bash`).
- **Webserver** logs appear in the console by default. You can access the logs by running `docker logs <webserver_container_id>`.
- **Metadata database** logs appear in the console by default. You can access the logs by running `docker logs <postgres_container_id>`.
- **Triggerer** logs appear in the console by default. You can access the logs by running `docker logs <triggerer_container_id>`.
- **Task** logs are in `/usr/local/airflow/logs/` within the scheduler Docker container. You can also access task logs in the Grid or Graph views of the Airflow UI using the **Log** button.

For Astro CLI users a command to show webserver, scheduler, triggerer and Celery worker logs from the local Airflow environment is available: `astro dev logs` ([see also the Astro documentation](https://docs.astronomer.io/astro/cli/astro-dev-logs).)

### Running Airflow locally

If you run Airflow locally, logging information will be accessible in different locations than with dockerized Airflow:

- **Scheduler** logs are printed to the console and accessible in `$AIRFLOW_HOME/logs/scheduler`.
- **Webserver** and **Triggerer** logs are printed to the console.
- **Task** logs can be viewed either in the Airflow UI or at `$AIRFLOW_HOME/logs/`.
- **Metadata database** logs are handled differently depending on which database you use.

## Adding Additional Task Logs from within a DAG

All hooks and operators in Airflow generate logs when a task is run. While it is currently not possible to modify logs from within other operators or in the top-level code, you can add custom logging statements from within your Python functions by accessing the `airflow.task` logger.

The advantage of using a logger over print statements is that you can log at different levels and control which logs are emitted to a specific location. For example, by default the `airflow.task` logger is set at the level of `INFO`, which means that logs at the level of `DEBUG` aren't logged. To see `DEBUG` logs when debugging your python tasks, you simply need to set `AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG` or change the value of `logging_level` in `airflow.cfg`. After debugging, you can change the `logging_level` back to `INFO` without ever having to touch your DAG code.

The DAG below shows how to instantiate an object using the existing `airflow.task` logger, add logging statements of different severity levels from within a Python function and what the log output would be with default Airflow logging settings. There are many use cases for adding additional logging statements from within DAGs ranging from logging warnings when a specific set of conditions appear over additional debugging message to catching exceptions but still keeping a record of them having occurred.

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

# import the logging module
import logging

# get the airflow.task logger
task_logger = logging.getLogger('airflow.task')

@task.python
def extract():

    # with default airflow logging settings, DEBUG logs are ignored
    task_logger.debug('This log is at the level of DEBUG')

    # each of these lines produce a log statement
    print('This log is created via a print statement')
    task_logger.info('This log is informational')
    task_logger.warning('This log is a warning')
    task_logger.error('This log shows an error!')
    task_logger.critical('This log shows a critical error!')

    data = {'a': 19, 'b': 23, 'c': 42}

    # Using the Task flow API to push to XCom by returning a value
    return data

# logs outside of tasks will not be processed
task_logger.warning('This log will not show up!')

with DAG(dag_id='more_logs_dag',
        start_date=datetime(2022,6,5),
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        catchup=False) as dag:

    # command to create a file and write the data from the extract task into it
    # these commands use Jinja templating within {{}}
    commands= """
        touch /usr/local/airflow/{{ds}}.txt
        echo {{ti.xcom_pull(task_ids='extract')}} > /usr/local/airflow/{{ds}}.txt
        """

    write_to_file = BashOperator(task_id='write_to_file', bash_command=commands)

    # logs outside of tasks will not be processed
    task_logger.warning('This log will not show up!')

    extract() >> write_to_file
```

For the DAG above, the logs for the `extract` task will show the following lines under the default Airflow logging configuration (set at the level of `INFO`):

```bash
[2022-06-06, 07:25:09 UTC] {logging_mixin.py:115} INFO - This log is created via a print statement
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:15} INFO - This log is informational
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:16} WARNING - This log is a warning
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:17} ERROR - This log shows an error!
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:18} CRITICAL - This log shows a critical error!
```

## Why to Configure Logging

Logging in Airflow is ready to use without any additional configuration. However, there are many use cases where customization of logging is beneficial. For example:

- Changing the format of existing logs to contain additional information (for example, the full pathname of the source file from which the logging call was made)
- Adding additional handlers (for example, to log all critical errors in a separate file)
- Storing logs remotely (see "Logging Remotely" below)
- Adding your own custom handlers (for example, to log remotely to a destination not yet supported by existing providers)

## How to Configure Logging

Logging in Airflow can be configured in `airflow.cfg` and by providing a custom `log_config.py` file. It is considered best practise to not declare configs or variables within the `.py` handler files except for testing or debugging purposes.

The current task handler and logging configuration can be found running the following commands using the Airflow CLI (if you are running Airflow in Docker, make sure to enter your Docker container before running the commands):

```console
airflow info          # shows the current handler
airflow config list   # shows current parameters under [logging]
```

A full list parameters relating to logging that can be configured in `airflow.cfg` can be found in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#logging). They can also be configured by setting their corresponding environment variables.

For example, if you wanted to change your logging level from the default `INFO` to only log `LogRecords` with a level of `ERROR` or above, you could set `logging_level = ERROR` in `airflow.cfg` or define an environment variable `AIRFLOW__LOGGING__LOGGING_LEVEL=ERROR`.

Advanced configuration might necessitate the logging config class to be overwritten. To enable custom logging config a configuration file `~/airflow/config/log_config.py` has to be created in which modifications to `DEFAULT_LOGGING_CONFIG` are specified. You may need to do this if you want to, for example, add a custom handler.

A step-by-step explanation on how to set up remote logging can be found in the in the section 'Remote Logging Example: Sending Task Logs to S3' below.

## Logging Remotely

When scaling up your Airflow environment you might end up with many tasks producing more logs than your Airflow environment can handle storing. In this case, you need a reliable, resilient, and auto-scaling storage. The easiest solution is to use remote logging to a remote service which is already supported by a community-managed provider:

- Alibaba: `OSSTaskHandler` (`oss://`)
- Amazon: `S3TaskHandler` (`s3://`), `CloudwatchTaskHandler` (`cloudwatch://`)
- [Elasticsearch](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/logging/index.html): `ElasticsearchTaskHandler` (further configured via `elasticsearch` in `airflow.cfg`)
- [Google](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/logging/index.html): `GCSTaskHandler` (`gs://`), `StackdriverTaskHandler` (`stackdriver://`)
- [Microsoft Azure](https://airflow.apache.org/docs/apache-airflow-providers-microsoft-azure/stable/logging/index.html): `WasbTaskHandler` (`wasb`)

By configuring `REMOTE_BASE_LOG_FOLDER` with a prefix of a supported provider (as listed above), you can override the default task handler (`FileTaskHandler`) to send logs to a remote destination task handler (for example `GCSTaskHandler`.
If you want different behavior or add several handlers to one logger you will need to make changes to `DEFAULT_LOGGING_CONFIG` as described in the Advanced Configuration Example below.

It is important to note that logs are sent to remote storage only once a task has been completed or failed. This means that logs of currently running tasks are accessible only from your local Airflow environment.

## Remote Logging Example: Sending Task Logs to S3

The following is a step-by-step guide on how to quickly set up logging of Airflow task logs to a S3 bucket using the [Astro CLI](https://docs.astronomer.io/astro/cli/get-started).

1. Add the `apache-airflow-providers-amazon` provider package to `requirements.txt`.

2. Start your Airflow environment and go to **Admin** > **Connections** in the Airflow UI.

3. Create a connection of type **Amazon S3** and set `login` to your AWS access key ID and `password` to your AWS secret access key (See [AWS documentation](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html) for how to retrieve your AWS access key ID and AWS secret access key).  

4. Add the following commands to the Dockerfile (note the double underscores around `LOGGING`):

    ```dockerfile
    # allow remote logging and provide a connection ID (see step 2)
    ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
    ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=${AMAZONS3_CON_ID}

    # specify the location of your remote logs using your bucket name
    ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://${S3BUCKET_NAME}/logs

    # optional: serverside encryption for S3 logs
    ENV AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=True
    ```

These environment variables configure remote logging to one S3 bucket (`S3BUCKET_NAME`). Behind the scenes, Airflow uses these configurations to create an `S3TaskHandler` which overrides the default `FileTaskHandler`.  

Afterwards don't forget to restart your Airflow environment and run any task to verify that the task logs are copied to your S3 bucket.

![Logs in S3 bucket](https://assets2.astronomer.io/main/guides/your-guide-folder/logs_s3_bucket.png)

## Advanced Configuration Example: Add Multiple Handlers to the Same Logger

For full control over the logging configuration you will need to create and modify a `log_config.py` file. This is relevant for use cases such as adding several handlers to the same logger with different formatters, filters, or destinations, or to add your own custom handler. You may want to do this in order to save logs of different severity levels in different locations, apply additional filters to logs stored in a specific location or to further configure a custom logging solution with a destination for which no provider is available yet.

The following example adds a second remote logging S3 bucket to receive logs with a different file structure.

First, complete Steps 1 and 2 from "Sending Task Logs to S3" to configure your Airflow environment for S3 remote logging. Then, add the following commands to your Dockerfile:

```dockerfile
#### Remote logging to S3

# Define the base log folder
ENV BASE_LOG_FOLDER=/usr/local/airflow/logs

# create a directory for your custom log_config.py file and copy it
ENV PYTHONPATH=/usr/local/airflow
RUN mkdir $PYTHONPATH/config
COPY include/log_config.py $PYTHONPATH/config/
RUN touch $PYTHONPATH/config/__init__.py

# allow remote logging and provide a connection ID (the one you specified in step 2)
ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=hook_tutorial_s3_conn

# specify the location of your remote logs, make sure to provide your bucket names above
ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://${S3BUCKET_NAME}/logs
ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER_2=s3://${S3BUCKET_NAME_2}/logs

# set the new logging configuration as logging config class
ENV AIRFLOW__LOGGING__LOGGING_CONFIG_CLASS=config.log_config.LOGGING_CONFIG

# optional: serverside encryption for S3 logs
ENV AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=True
```

By setting these environment variables you can configure remote logging on two S3 buckets (`S3BUCKET_NAME` and `S3BUCKET_NAME_2`).
Additionally a second remote log folder `AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER_2` is set as an environment variable to be retrieved from within `log_config.py`. Importantly, the `AIRFLOW__LOGGING__LOGGING_CONFIG_CLASS` is replaced with your custom `LOGGING_CONFIG` class that you will define in the next step.

Lastly, create a `log_config.py` file. While you can put this file anywhere in your Airflow project as long as it is not within a folder listed in `.dockerignore`, it is best practise to put it outside of your `dags/` folder, such as `/include`, to prevent the scheduler wasting resources by continuously parsing the file. Make sure to adjust the COPY statement in the previous step depending on where you decide to store this file.

Within `log_config.py`, create and modify a deepcopy of `DEFAULT_LOGGING_CONFIG` as follows:

```python
from copy import deepcopy
import os

from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)


LOGGING_CONFIG['handlers']['secondary_s3_task_handler'] = {
    # you can import your own custom handler here
    'class': 'airflow.providers.amazon.aws.log.s3_task_handler.S3TaskHandler',
    # you can add a custom formatter here
    'formatter': 'airflow',
    # the following env variables were set above
    'base_log_folder': os.environ['BASE_LOG_FOLDER'],
    's3_log_folder': os.environ['AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER_2'],
    'filename_template':
        # provide a custom structure for log directory and filename
        "{{ ti.dag_id }}/{{ ti.task_id }}_{{ ts }}_{{ try_number }}.log",
    # if needed, custom filters can be added here
    "filters":[
    "mask_secrets"
    ]
}

# this line adds the "secondary_s3_task_handler" as a handler to airflow.task
LOGGING_CONFIG['loggers']['airflow.task']['handlers'] = ["task",
                                                  "secondary_s3_task_handler"]
```

This modified version of `DEFAULT_LOGGING_CONFIG` creates a second S3TaskHandler using the s3 location provided as `AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER_2`. It is configured with a custom `filename_template`, further customization is of course possible with regards to formatting, log level or additional filters.

Afterwards don't forget to restart your Airflow environment and run any task to verify that the task logs are copied to both of your S3 buckets.

![Logs in the secondary S3 bucket](<https://assets2.astronomer.io/main/guides/your-guide-folder/logs_second_s3_bucket.png>)
