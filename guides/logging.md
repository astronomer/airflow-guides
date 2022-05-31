---
title: "Logging in Airflow"
description: "Demystifying Airflow's logging configuration."
date: 2018-09-11T00:00:00.000Z
slug: "logging"
heroImagePath: null
tags: ["Logging", "Best Practices", "Basics"]
---

## Overview

Logging is the key to effective monitoring and debugging of any application. Airflow provides an extensive logging system to fit the observability needs of a variety of use cases. Core Airflow components such as the webserver, scheduler and workers as well as individual tasks via a TaskHandler provide logging information, either to a local file, the console or to a specified remote storage solution. The Airflow UI eventually collects logs from various locations to display to the end user.

In this guide we'll cover the basics of logging in Airflow, why and how to configure logging settings and remote logging. A full step-by-step example is provided on how to set up remote logging to an S3 bucket using the Astro CLI. Additionally an outline on how to construct your own custom Handler, information on further monitoring options in Airflow and the default logging settings are listed at the end of this guide.

## Logging Basics

Logging in Airflow leverages the [Python stdlib logging module](https://docs.python.org/3/library/logging.html).

The basic components of the `logging` module are the following classes:

- Loggers (`logging.Logger`) which are the interface the application code directly interacts with.
- Handlers (`logging.Handler`) which send log records to their destination.
- Filters (`logging.Filter`) which are used to further configure which log records to output.
- Formatters (`logging.Formatter`) which determine the final layout of log records.

`LogRecord` objects, which contain both the logging data and metadata, are instantiated with a level of severity. By default there are 6 logging levels: CRITICAL, ERROR, WARNING, INFO, DEBUG and NOTSET. Using the `setLevel` method each logger can be given a threshold at which logs will be emitted by a handler attached to this logger. Additional logic to determine when logs are emitted can added with a filter.

Loggers can be defined hierarchically and will propagate their output to their parent loggers' handler by default.

Once a message gets logged it gets passed to a handler attached to the logger or to a logger it propagates to. Similarly to a logger a handler can have its own filters and level of severity. By using `setFormatter` a formatter can be assigned to a specific handler to add custom formatting to the message.

The logging module provides a [variety of handlers](https://docs.python.org/3/library/logging.handlers.html#module-logging.handlers) from which custom handlers can inherit. If no handlers are defined in an application the root logger will use a `StreamHandler` with a level of `WARNING` to write to `sys.stderr` (also known as the handler of last resort).  


## Logging in Airflow

The default configuration of logging in Airflow defines four loggers:

- `root` (level: INFO) : uses `RedirectStdHandler` and the formatter 'airflow_colored'. It outputs to `sys.stderr/stout`.
- `flask_appbuilder` (level: WARNING) : uses `RedirectStdHandler` and the formatter 'airflow_colored'. It outputs to `sys.stderr/stout`.
- `airflow.processor` (level: INFO) : uses `FileProcessorHandler` and the formatter 'airflow'. This handler writes to the local file system.
- `airflow.task` (level: INFO) : uses `FileTaskHandlers` and the Formatter 'airflow' and writes to the local file system.

All Handlers use the filter `SecretsMasker` to prevent sensitive information from being logged.

More logging statements can be added from within your DAGs by accessing the `airflow.task` logger:

```python
import logging

# access the airflow.task logger instance
logger = logging.getLogger('airflow.task')  

# create a logging message at the level INFO
logger.info('There can never be enough logs! :)')
```

The default location of logs is specified as `base_log_folder` in `airflow.cfg` which is located in the `$AIRFLOW_HOME` directory.

If not otherwise specified log files will be named according to the following pattern, which can be configured as `log_filename_template` in `airflow.cfg`:

- For normal tasks: `dag_id={dag_id}/run_id={run_id}/task_id={task_id}/attempt={try_number}.log`
- For dynamically mapped tasks: `dag_id={dag_id}/run_id={run_id}/task_id={task_id}/map_index={map_index}/attempt={try_number}.log`

Two formatters are used in the default configuration:

- 'airflow_colored': `"[%(blue)s%(asctime)s%(reset)s] {%(blue)s%(filename)s:%(reset)s%(lineno)d} %(log_color)s%(levelname)s%(reset)s - %(log_color)s%(message)s%(reset)s"`
- 'airflow': `"[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"`

## Why to configure logging

Logging in Airflow is set up to be ready to use without any configuration being necessary. However there are many use cases where customization of logging is beneficial.

- Lowering the threshold level of existing loggers in order to show debug logs.
- Changing the formatting of existing logs in order to contain additional information for example the full pathname of the source file from which the logging call was made.
- Adding additional handlers, for example to log all critical errors in an additional separate destination.
- Storing logs remotely (see the section "Logging Remotely" below).

## How to configure logging

Logging in Airflow can be configured in `airflow.cfg` or by providing a custom `log_config.py` file. It is considered best practise to not declare configs or variables within the `.py` handler files except for testing or debugging purposes.

The current task handler and logging configuration can be found running the following commands:

```console
$ airflow info          # shows the current handler
$ airflow config list   # shows current parameters under [logging]
```

A full list parameters relating to logging that can be configured in `airflow.cfg` can be found in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#logging). They can also be configured by setting their corresponding environmental variables.

Advanced configuration might necessitate the logging config class to be overwritten. To enable custom logging config a configuration file `~/airflow/config/log_config.py` has to be created in which modifications to `DEFAULT_LOGGING_CONFIG` are specified.   

A step-by-step explanation can be found in the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/logging-tasks.html#advanced-configuration) or in the section 'Example setting up remote logging to S3 using Astro CLI' below.

## Logging remotely

There are implementations for writing task logs to a remote destination for a number of community-managed providers:

- Alibaba: `OSSTaskHandler`
- Amazon: `S3TaskHandler`, `CloudwatchTaskHandler`
- [Elasticsearch](https://airflow.apache.org/docs/apache-airflow-providers-elasticsearch/stable/logging/index.html): `ElasticsearchTaskHandler`
- [Google](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/logging/index.html): `GCSTaskHandler`, `StackdriverTaskHandler`
- [Microsoft Azure](https://airflow.apache.org/docs/apache-airflow-providers-microsoft-azure/stable/logging/index.html): `WasbTaskHandler`

It is important to note that logs are only sent to remote storage once a task has been completed (including in case of failure), this means you will only be able to see the logs of currently running tasks locally.


## Example setting up remote logging of tasks to S3 using Astro CLI

The following is a step-by-step guide on how to set up logging of task logs to an S3 bucket using the Astro CLI ([Install instructions for the Astro CLI](https://docs.astronomer.io/astro/install-cli)).

1. Add the Amazon provider and the `conf` module to `requirements.txt`:

```text
apache-airflow-providers-amazon
conf
```

2. Start the Airflow environment and navigate to **Admin** -> **Connections** in the Airflow UI to add the connection to the S3 bucket. Select Amazon S3 as connection type for the S3 bucket and provide the connection with your AWS access key ID as `login` and your AWS secret access key as `password` ([See AWS documentation for how to retrieve your AWS access key ID and AWS secret access key](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)).  

3. Create a file `log_config.py` on your local machine in which a copy of `DEFAULT_LOGGING_CONFIG` is modified to include the `S3TaskHandler` ([Source Code](https://github.com/apache/airflow/blob/e58985598f202395098e15b686aec33645a906ff/airflow/providers/amazon/aws/log/s3_task_handler.py)) as a handler for the logger `airflow.task`:

```python
from copy import deepcopy
import os
import conf
from airflow.config_templates.airflow_local_settings import (
                                                     DEFAULT_LOGGING_CONFIG)

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)

# add the s3.task handler to the handlers section
LOGGING_CONFIG['handlers']['s3.task'] = {
    'class': 'airflow.utils.log.s3_task_handler.S3TaskHandler',
    'formatter': 'airflow',
    # the following env variables will be set in step 4
    'base_log_folder': os.path.expanduser('AIRFLOW__LOGGING__BASE_LOG_FOLDER'),
    's3_log_folder': conf.get('core',
                              'AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER'),
    'filename_template':
              "{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log",
    "filters":[
            "mask_secrets"
         ]
}

# add the s3.task handler as a second handler on the logger for tasks
LOGGING_CONFIG['loggers']['airflow.task']['handlers'] = ["task", "s3.task"]
```

4. Add the following commands to the Dockerfile to copy the locally created `log_config.py` file into the right directory within the container, allow remote logging, set your S3 bucket as the logging destination and change the source of the logging config class file:

```dockerfile
# create a directory for the your custom log_config.py file
ENV PYTHONPATH=/usr/local/airflow
RUN mkdir $PYTHONPATH/config
# copy the file from your local machine to the docker container
COPY ~/path/log_config.py $PYTHONPATH/config/

# allow remote logging and provide a connection ID (see step 2)
ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=${AMAZONS3_CON_ID}

# specify the location of your remote logs using your bucket name
ENV AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://${S3BUCKET_NAME}/logs

# set the new logging configuration as logging config class
ENV AIRFLOW__LOGGING__LOGGING_CONFIG_CLASS=config.log_config.LOGGING_CONFIG

# optional: serverside encryption for S3 logs
ENV AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=True
```

5. Restart your Airflow environment and run any task to verify that the logs are copied to your S3 bucket.

## Logging display

The Airflow UI displays logs to the user using a `read()` method on task handlers which is not part of stdlib.
`read()` checks for available logs to display in a predefined order:

1. Remote logs if remote logging is enabled.
2. Logs on the local filesystem
3. Logs from worker logs webserver

If a Kubernetes Executer was used and the Worker pod still exists `read()` will display the first 100 lines from Kubernetes pod logs, if the Worker pod ceased to exists those logs will be unavailable.

## Custom Handlers

All Handlers inherit from the stdlib's `logging.Handler`. Custom handlers can be created following the basic logic shown below. Implementation will differ depending on your use case.

```python
class MyTaskHandler(logging.Handler):
    def __init__(self):
        super(MyTaskHandler, self).__init__()

    def emit(self, record: logging.LogRecord):
        # logic to stream logs

    def close(self):
        # logic to ship logs in bulk

    def read(self, task_instance, try_number=None, metadata=None):
        # logic to fetch logs
```

## Beyond Logging

Additionally to standard logging there are a variety of other monitoring options when using Airflow:

- [Using statD to collect Metrics](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/metrics.html) like number of currently running DAG parsing processes, number of open executor slots or milliseconds taken to finish a given task.
- [Using task events to trigger callback functions](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/callbacks.html#).
- [Checking Airflow Health Status](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/check-health.html#) of the metadatabase and the scheduler: via REST API or CLI.
- [Tracking Errors via Sentry](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/errors.html)
- [Anonymously tracking User Activity](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/tracking-user-activity.html) for example via Google Analytics, Segment or Metarouter.


## Airflow's default logging configuration for reference

The configuration below can be imported from:  
 `from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG`

```json
{
   "version":1,
   "disable_existing_loggers":false,
   "formatters":{
      "airflow":{
         "format":"[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
      },
      "airflow_coloured":{
         "format":"[%(blue)s%(asctime)s%(reset)s] {%(blue)s%(filename)s:%(reset)s%(lineno)d} %(log_color)s%(levelname)s%(reset)s - %(log_color)s%(message)s%(reset)s",
         "class":"airflow.utils.log.colored_log.CustomTTYColoredFormatter"
      }
   },
   "filters":{
      "mask_secrets":{
         "()":"airflow.utils.log.secrets_masker.SecretsMasker"
      }
   },
   "handlers":{
      "console":{
         "class":"airflow.utils.log.logging_mixin.RedirectStdHandler",
         "formatter":"airflow_coloured",
         "stream":"sys.stdout",
         "filters":[
            "mask_secrets"
         ]
      },
      "task":{
         "class":"airflow.utils.log.file_task_handler.FileTaskHandler",
         "formatter":"airflow",
         "base_log_folder":"/Users/tjanif/airflow/logs",
         "filename_template":"{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log",
         "filters":[
            "mask_secrets"
         ]
      },
      "processor":{
         "class":"airflow.utils.log.file_processor_handler.FileProcessorHandler",
         "formatter":"airflow",
         "base_log_folder":"/Users/tjanif/airflow/logs/scheduler",
         "filename_template":"{{ filename }}.log",
         "filters":[
            "mask_secrets"
         ]
      }
   },
   "loggers":{
      "airflow.processor":{
         "handlers":[
            "processor"
         ],
         "level":"INFO",
         "propagate":false
      },
      "airflow.task":{
         "handlers":[
            "task"
         ],
         "level":"INFO",
         "propagate":false,
         "filters":[
            "mask_secrets"
         ]
      },
      "flask_appbuilder":{
         "handlers":[
            "console"
         ],
         "level":"WARNING",
         "propagate":true
      }
   },
   "root":{
      "handlers":[
         "console"
      ],
      "level":"INFO",
      "filters":[
         "mask_secrets"
      ]
   }
}
```
