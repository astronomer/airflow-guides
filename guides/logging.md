---
title: "Logging in Airflow"
description: "Demystifying Airflow's logging configuration."
date: 2018-09-11T00:00:00.000Z
slug: "logging"
heroImagePath: null
tags: ["Airflow", "Logging"]
---

# Logging in Astronomer Enterprise

Airflow provides a ton of flexibility in configuring its logging system. All of the logging in Airflow is implemented through Python's standard `logging` library. Logs can be piped to remote storage, including Google Cloud Storage and Amazon S3 buckets, and most recently in Airflow 1.10, ElasticSearch.

A lot of the information on logging in Airflow can be found in the official documentation, but we've added a bit more flavor and detail about the logging module that Airflow utilizes. Given that our product is built on Airflow, we've thought a lot about how logs should be structured, and where they should be sent.

**This guide is built for logging in Airflow 1.9, but a 1.10 version is coming soon**

### An Overview of Logging
If you just want to get more information on logging handlers, skip this section. This is merely more information to understand how the logging system is implemented in Airflow.

In [The Twelve-Factor App's](https://12factor.net/logs) section on logging, logs are described as "the stream of aggregated, time-ordered events collected from the output streams of all running processes and backing services". Airflow has built around this philosophy, but given that it runs in a server-based environment, all of Airflow's logs are written to a file. When the user wants to access a log file through the web UI, that action triggers a GET request to retrieve the contents.

Airflow relies on a ton of different moving pieces, and all of its information output is integral to making sure the system is running as expected. Python's built in `logging` module allows for flexibility in configuring and routing logs from different pieces using different `Loggers`. A `Logger` object is instantiated by the `logging.getLogger(name_of_logger)` function. The sole purpose of the `Logger` object is to obtain messages with a `log_level` (ERROR, INFO, DEBUG) that need to be redirected to a specified destination. At its core, Airflow is comprised of a scheduler, a webserver, and a worker. All three of these components need a way to log out information.

When a call is made to the logger such as `self.log.info("Task 1 has finished!")`, this message is turned into a `LogRecord` object, containing all of the metadata and data necessary for the final output. The `LogRecord` is passed to the handler through an `emit` function. The handler will "pass" (quotations for a reason) the `LogRecord` to a `Formatter`, which will subsequently pass the log back to the handler in its final, glorious, sparkling string form.

At this point, it is up to the Handler to decide what happens with the string. The `logging` module supports several different types of handlers, but the three most important to Airflow are:

1. FileHandler- Directs output to a disk file
2. StreamHandler- Directs output to a stream (stdout, stderr)
3. NullHandler- Does nothing, is a dummy handler for testing and developing

As you might guess, all of the task instance logs, webserver logs, and scheduler logs get piped through a `FileHandler` and a `StreamHandler` at some point.

## Demystifying Airflow's Logging Configuration

The logger in Airflow is configured through a *dictionary-formatted* file. All of the necessary configuration is either set here, or passed into this file as an environmental variable. **The `.py` handler file is merely a tool that is passed all of its configuration arguments from a configuration file. There is absolutely no reason to declare configs and/or variables within these handler files, except for testing or debugging purposes**.

In the `.py`, the context for the logger is set. This includes the type of handler to use, the formatter, and the level of the log message.

Let's take a look at the default logging configuration file that Airflow ships with.
```
from airflow import configuration as conf

LOG_LEVEL = conf.get('core', 'LOGGING_LEVEL').upper()
LOG_FORMAT = conf.get('core', 'log_format')
BASE_LOG_FOLDER = conf.get('core', 'BASE_LOG_FOLDER')
PROCESSOR_LOG_FOLDER = conf.get('scheduler', 'child_process_log_directory')
FILENAME_TEMPLATE = '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log'
PROCESSOR_FILENAME_TEMPLATE = '{{ filename }}.log'

DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'airflow.task': {
            'format': LOG_FORMAT,
        },
        'airflow.processor': {
            'format': LOG_FORMAT,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'airflow.task',
            'stream': 'ext://sys.stdout'
        },
        'file.task': {
            'class': 'airflow.utils.log.file_task_handler.FileTaskHandler',
            'formatter': 'airflow.task',
            'base_log_folder': os.path.expanduser(BASE_LOG_FOLDER),
            'filename_template': FILENAME_TEMPLATE,
        },
        'file.processor': {
            'class': 'airflow.utils.log.file_processor_handler.FileProcessorHandler',
            'formatter': 'airflow.processor',
            'base_log_folder': os.path.expanduser(PROCESSOR_LOG_FOLDER),
            'filename_template': PROCESSOR_FILENAME_TEMPLATE,
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOG_LEVEL
        },
        'airflow': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'airflow.processor': {
            'handlers': ['file.processor'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'airflow.task': {
            'handlers': ['file.task'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'airflow.task_runner': {
            'handlers': ['file.task'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    }
}
```
This is a small piece of the `airflow_local_settings.py` file located in `/airflow/config_templates`. Some important notes:
- All-capitalized variables are environmental variables that are pulled in from the airflow configuration file `airflow.cfg`
- The `DEFAULT_LOGGING_CONFIG` is an object, containing keys for `formatters`, `handlers`, and `loggers`.
- `handlers` keys are passed into the `loggers.airflow.**.handlers` values

All of this is important to remember when it comes to custom logging.

### Available Handlers in Airflow
In the `incubator-airflow` project, all available handlers are located in `/airflow/utils/log`.
**Airflow 1.9**

|         Handler name        | Remote Storage | Default |
|:---------------------------:|----------------|---------|
| `file_processor_handler.py` | No             | Yes     |
| `file_task_handler.py`      | No             | Yes     |
| `gcs_task_handler.py`       | Yes            | No      |
| `s3_task_handler.py`        | Yes            | No      |

**Airflow 1.10**

|         Handler name        | Remote Storage | Default |
|:---------------------------:|----------------|---------|
| `file_processor_handler.py` | No             | Yes     |
| `file_task_handler.py`      | No             | Yes     |
| `gcs_task_handler.py`       | Yes            | No      |
| `s3_task_handler.py`        | Yes            | No      |
| `es_task_handler.py`        | Yes            | No      |
| `wasb_task_handler.py`      | Yes            | No      |

### Setting up custom logging in Airflow
Configuring logging is done through both `env` variables and setting up a new `log_config.py` file. We'll outline the steps one by one:

1. Create a new directory to store the new log config file. The new directory should be called `config`. Airflow's docs require you place the new directory in the `PYTHONPATH`, so it should be created as such: `$AIRFLOW_HOME/config`.

2. Inside your new directory called `config`, place two new files, `__init__.py` and a `log_config.py`. It should look something like this:
```
├── config
│   ├── __init__.py
│   ├── log_config.py

```

3. Copy the entire contents of `airflow_local_settings.py` from the `config_templates` directory into `log_config.py`. Change the variable name called `DEFAULT_LOGGING_CONFIG` to `LOGGING_CONFIG`.

4. Inside `airflow.cfg`, locate the environmental variable called `LOGGING_CONFIG_CLASS`, inside the Airflow Core settings. Change this to reflect the path to your new `log_config,py` file. In most cases, this will be as such, but adapt to your own needs:
```
 LOGGING_CONFIG_CLASS = airflow.config.log_config.LOGGING_CONFIG
```

5. Also take note of the environmental variable in `airflow.cfg` called `TASK_LOG_READER`. This is an important variable to set if you want to configure a custom logger to read task logs, to pipe them to standard out instead of files, if you wish.
