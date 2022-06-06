---
title: "Logging in Airflow"
description: "Demystifying Airflow's logging configuration."
date: 2018-09-11T00:00:00.000Z
slug: "logging"
heroImagePath: null
tags: ["Logging", "Best Practices", "Basics"]
---

## Overview

Logging is the key to effective monitoring and debugging of any application. Airflow provides an extensive logging system to fit the observability needs of a variety of use cases. Core Airflow components such as the webserver, scheduler and metadata database as well as individual tasks provide logging information, either to a local file, the console or to a specified remote storage solution. The Airflow UI eventually collects logs from various locations to display to the end user.

In this guide, we'll cover the basics of logging in Airflow, where to find the logs of different Airflow components, how to add task logs, why and how to configure logging settings, and remote logging. A full step-by-step example is provided on how to set up remote logging to an S3 bucket using the [Astro CLI](https://docs.astronomer.io/astro/cli/configure-cli#install-the-cli).

Additionally to standard logging, there are a variety of other monitoring options when using Airflow that let you collect metrics, use tasks events to trigger callback functions, monitor Airflow health status and track errors or user activity. You can find more information on monitoring options in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/index.html) and for Astronomer customers in the [Astro Docs](https://docs.astronomer.io/astro/deployment-metrics).

## Logging in Airflow

Logging in Airflow leverages the [Python stdlib logging module](https://docs.python.org/3/library/logging.html).

The basic components of the `logging` module are the following classes:

- **Loggers** (`logging.Logger`) which are the interface the application code directly interacts with. Airflow defines 4 loggers by default: `root`, `flask_appbuilder`, `airflow.processor` and `airflow.task`.
- **Handlers** (`logging.Handler`) which send log records to their destination. Airflow by default uses `RedirectStdHandler`, `FileProcessorHandler` and `FileTaskHandler`.
- **Filters** (`logging.Filter`) which are used to further configure which log records to output. Airflow uses `SecretsMasker` as a filter to prevent sensitive information from being printed into logs.
- **Formatters** (`logging.Formatter`) which determine the final layout of log records. Two formatters are predefined in Airflow: `airflow_colored` and `airflow`.

Please see the Python documentation for more information on [methods available for the classes above](https://docs.python.org/3/library/logging.html#logger-objects), attributes of a [LogRecord object](https://docs.python.org/3/library/logging.html#logrecord-objects) and the [6 levels of logging severity](https://docs.python.org/3/library/logging.html#logging-levels) (CRITICAL, ERROR, WARNING, INFO, DEBUG and NOTSET).

The four default loggers in Airflow each have a handler with a predefined log destination as well as one of the two formatters assigned:

- `root` (level: INFO) : uses `RedirectStdHandler` and the formatter 'airflow_colored'. It outputs to `sys.stderr/stout` and acts as a catch all for processes which have no specific logger defined.
- `flask_appbuilder` (level: WARNING) : uses `RedirectStdHandler` and the formatter 'airflow_colored'. It outputs to `sys.stderr/stout`. This logger handles logs from the webserver.
- `airflow.processor` (level: INFO) : uses `FileProcessorHandler` and the formatter 'airflow'. This handler writes logs from the scheduler to the local file system.
- `airflow.task` (level: INFO) : uses `FileTaskHandlers` and the Formatter `airflow` and writes task logs to the local file system.

If not otherwise specified log files will be named according to the following pattern, which can be configured as `log_filename_template` in `airflow.cfg`:

- For normal tasks: `dag_id={dag_id}/run_id={run_id}/task_id={task_id}/attempt={try_number}.log`
- For dynamically mapped tasks: `dag_id={dag_id}/run_id={run_id}/task_id={task_id}/map_index={map_index}/attempt={try_number}.log`

Two formatters are used in the default configuration:

- `airflow_colored`: `"[%(blue)s%(asctime)s%(reset)s] {%(blue)s%(filename)s:%(reset)s%(lineno)d} %(log_color)s%(levelname)s%(reset)s - %(log_color)s%(message)s%(reset)s"`
- `airflow`: `"[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"`

> **Note:** The full default logging configuration can be viewed in the [Airflow source code](https://github.com/apache/airflow/blob/c0e9daa3632dc0ede695827d1ebdbd091401e94d/airflow/config_templates/airflow_local_settings.py#L59).

The Airflow UI displays logs to the user using a `read()` method on task handlers which is not part of stdlib.
`read()` checks for available logs to display in a predefined order:

1. Remote logs if remote logging is enabled.
2. Logs on the local filesystem
3. Logs from worker logs webserver

> **Note:** If a Kubernetes Executer was used and the Worker pod still exists `read()` will display the first 100 lines from Kubernetes pod logs, if the Worker pod ceased to exists those logs will be unavailable.

## Log Locations

The default location of logs which are outputted to the file system is specified as `base_log_folder` in `airflow.cfg` which is located in the `$AIRFLOW_HOME` directory.

If you run Airflow in Docker (either via [Astro CLI](https://docs.astronomer.io/software/install-cli) or [following the Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)) you will find the logs of the Airflow components in the following places by default:

- **Scheduler**: logged to `/usr/local/airflow/logs/scheduler` within the Docker container by default (you can enter a docker container in a bash session with `docker exec -it <container_id> /bin/bash`)
- **Webserver**: Is logged to the console by default. You can access the log by running `docker logs <webserver_container_id>`.
- **Metadatabase**: Is logged to the console by default. You can access the log by running `docker logs <postgres_container_id>`.
- **Triggerer**: Is logged to the console by default. You can access the log by running `docker logs <triggerer_container_id>`.
- **Tasks**: From within the Docker container, navigate to  `/usr/local/airflow/logs/` or navigate to your task instance in the Grid or Graph views of the Airflow UI and click on the `Log` button.

If you run Airflow locally, the logs from your scheduler, webserver and triggerer will be printed to the console. Additionally, you will find logs from your scheduler separated by DAG in `$AIRFLOW_HOME/logs/scheduler`, while your task logs can be viewed either in the Airflow UI or at `$AIRFLOW_HOME/logs/`. How the logs from your metadatabase are handled depends on which database you use.

## Adding Task Logs

All hooks and operators in Airflow will generate logs when the task is run. The logs that are generated will vary for each specific module but you can also add additional logging statements from within your python functions by accessing the `airflow.task` logger. It is currently not possible to add logs from within other operators or in the top-level code.

The advantage of using a logger over print statements is that you can log at different levels of severity and use the level setting of loggers and handlers to control which logs are emitted to which location. Print statements are always set at the level of `INFO`. For example, using the default Airflow logging configuration the `airflow.task` logger is set at the level of `INFO`, which means logs at the level of `DEBUG` are not logged. You may want to see these logs when debugging your python tasks, to do so you simply need to set `AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG` or change the value of `logging_level` in `airflow.cfg`. After successful debugging the `logging_level` can simply be changed back to only display logs of a higher level without any changes to the DAG code being necessary.


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

The DAG above shows how to log at different levels of severity from within a custom python function. The logs for the `extract` task will show the following lines under the default Airflow logging configuration (set at the level of `INFO`):

```bash
[2022-06-06, 07:25:09 UTC] {logging_mixin.py:115} INFO - This log is created via a print statement
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:15} INFO - This log is informational
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:16} WARNING - This log is a warning
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:17} ERROR - This log shows an error!
[2022-06-06, 07:25:09 UTC] {more_logs_dag.py:18} CRITICAL - This log shows a critical error!
```

## Why to Configure Logging

Logging in Airflow is set up to be ready to use without any configuration being necessary. However, there are many use cases where customization of logging is beneficial. For example:

- Lowering the threshold level of existing loggers in order to show debug logs.
- Changing the formatting of existing logs in order to contain additional information for example the full pathname of the source file from which the logging call was made.
- Adding additional handlers, for example to log all critical errors in an additional separate destination.
- Storing logs remotely (see the section "Logging Remotely" below).
- Adding your own custom handlers, for example to log remotely to a destination not yet supported by existing providers.

## How to Configure Logging

Logging in Airflow can be configured in `airflow.cfg` or by providing a custom `log_config.py` file. It is considered best practise to not declare configs or variables within the `.py` handler files except for testing or debugging purposes.

The current task handler and logging configuration can be found running the following commands using the Airflow CLI (if you are running Airflow in Docker, make sure to enter your Docker container before running the commands):

```console
airflow info          # shows the current handler
airflow config list   # shows current parameters under [logging]
```

A full list parameters relating to logging that can be configured in `airflow.cfg` can be found in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#logging). They can also be configured by setting their corresponding environmental variables.

For example, if you wanted to change your logging level from the default `INFO` to only log `LogRecords` with a level of `ERROR` or above, you could set `logging_level = ERROR` in `airflow.cfg` or define an environmental variable `AIRFLOW__LOGGING__LOGGING_LEVEL=ERROR`.

Advanced configuration might necessitate the logging config class to be overwritten. To enable custom logging config a configuration file `~/airflow/config/log_config.py` has to be created in which modifications to `DEFAULT_LOGGING_CONFIG` are specified. You may need to do this if you want to, for example, add a custom handler.

A step-by-step explanation can be found in the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/logging-tasks.html#advanced-configuration) or in the section 'Example: Remote logging of tasks to S3 using Astro CLI' below.

## Logging Remotely

When scaling up your Airflow environment you may end up with many tasks producing sizeable amounts of logs for which you need a reliable, resilient and auto-scaling storage. The easiest solution is to use remote logging to a remote destination for which a community-managed provider already exists:

- Alibaba: `OSSTaskHandler`
- Amazon: `S3TaskHandler`, `CloudwatchTaskHandler`
- [Elasticsearch](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/logging/index.html): `ElasticsearchTaskHandler`
- [Google](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/logging/index.html): `GCSTaskHandler`, `StackdriverTaskHandler`
- [Microsoft Azure](https://airflow.apache.org/docs/apache-airflow-providers-microsoft-azure/stable/logging/index.html): `WasbTaskHandler`

For these providers Airflow contains logic to overwrite your task handler (`FileTaskHandler`) with the corresponding remote destination task handler (for example `GCSTaskHandler`) if you provide a valid `REMOTE_BASE_LOG_FOLDER` (e.g. `gs://...`).
If you want different behavior or add several handlers to one logger you will need to make changes to `DEFAULT_LOGGING_CONFIG` as described in the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/logging-tasks.html#advanced-configuration).

It is important to note that logs are only sent to remote storage once a task has been completed (including in case of failure), this means you will only be able to see the logs of currently running tasks locally.

## Remote Logging Example: Sending Task Logs to S3

The following is a step-by-step guide on how to quickly set up logging of Airflow task logs to a S3 bucket using the [Astro CLI](https://docs.astronomer.io/astro/install-cli).

1. Add the Amazon provider module `apache-airflow-providers-amazon` to `requirements.txt`.

2. Start the Airflow environment and navigate to **Admin** -> **Connections** in the Airflow UI to add the connection to the S3 bucket. Select Amazon S3 as connection type for the S3 bucket and provide the connection with your AWS access key ID as `login` and your AWS secret access key as `password` ([See AWS documentation for how to retrieve your AWS access key ID and AWS secret access key](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)).  

3. Add the following commands to the Dockerfile (not the double underscores around `LOGGING`):

```dockerfile
# allow remote logging and provide a connection ID (see step 2)
ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=${AMAZONS3_CON_ID}

# specify the location of your remote logs using your bucket name
ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://${S3BUCKET_NAME}/logs

# optional: serverside encryption for S3 logs
ENV AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=True
```

By setting these environmental variables you can configure remote logging to one S3 bucket (`S3BUCKET_NAME`). Behind the scenes, Airflow uses the connection ID `AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID` and the remote log folder `AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER` (starts with `s3://`) that were provided to create a S3TaskHandler and replace the default FileTaskHandler.  

Afterwards don't forget to restart your Airflow environment and run any task to verify that the task logs are copied to your S3 bucket.

![Logs in S3 bucket](<https://assets2.astronomer.io/main/guides/your-guide-folder/logs_s3_bucket.png>)

## Advanced Configuration Example: Add Multiple Handlers to the Same Logger

For full control over the logging configuration you will need to create and modify a `log_config.py` file. This is relevant for use cases such as adding several handlers to the same logger with different formatters, filters, or destinations, or to add your own custom handler.

The following example adds a second remote logging S3 bucket to receive logs with a different file structure.

First, complete Steps 1 and 2 from the section above to configure your Airflow environment for S3 remote logging. Then, add the following commands to your Dockerfile:

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

By setting these environmental variables you can configure remote logging to two S3 buckets (`S3BUCKET_NAME` and `S3BUCKET_NAME_2`). Like in the previous section Airflow uses the connection ID `AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID` and the remote log folder `AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER` (starts with `s3://`) that were provided to create a S3TaskHandler and replace the default FileTaskHandler.  
Additionally a second remote log folder `AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER_2` is set as an environmental variable to be retrieved from within `log_config.py`. Importantly the `AIRFLOW__LOGGING__LOGGING_CONFIG_CLASS` is replaced with your custom `LOGGING_CONFIG` class you will define in the next step.

Lastly, create a `log_config.py` file. While you can put this file anywhere in your Airflow project as long as it is not within a folder listed in `.dockerignore`, it is best practise to put it outside of your `dags/` folder to prevent computing resources from being used unnecessarily by having the scheduler parse the file. A common place it would be `include/`. Make sure to adjust the COPY statement in the previous step, depending on where you decide to store this file. Within the file create and modify a deepcopy of `DEFAULT_LOGGING_CONFIG` as follows:

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
