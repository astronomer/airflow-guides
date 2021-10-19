---
title: "Sensors 101"
description: "An introduction to Sensors in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-a-sensor"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Operators", "Tasks", "Basics", "Sensors"]
---

## Overview

[Apache Airflow Sensors](https://airflow.apache.org/docs/apache-airflow/stable/concepts/sensors.html) are a special kind of operator that are designed to wait for something to happen. When they run, they will check to see if a certain criteria is met before they are marked successful and let their downstream tasks execute. When used properly, they can be a great way of making your DAGs more event driven.

In this guide, we'll cover the basics of using sensors in Airflow, best practices for implementing sensors in production, and new sensor-related features in Airflow 2 like smart sensors and asynchronous operators. For more in-depth guidance on these topics, check out our [mastering sensors webinar](https://www.astronomer.io/events/webinars/creating-data-pipelines-using-master-sensors/).

## Sensor Basics

Sensors are conceptually simple: they are operators that check if a condition is satisfied on a particular interval. If the condition has been met, the task is marked successful and the DAG can move on to downstream tasks. If the condition hasn't been met, the sensor waits for another interval before checking again. 

All sensors inherit from the [`BaseSensorOperator`](https://github.com/apache/airflow/blob/main/airflow/sensors/base.py.) and have the following parameters:

- `mode`: How the sensor operates. There are two options:
    - `poke`: This is the default mode. When using `poke`, the sensor occupies a worker slot for the entire execution time and sleeps between pokes. This mode is best if you expect a short runtime for the sensor.
    - `reschedule`: When using this mode, the sensor will release its worker slot the criteria is not met and will reschedule the next check at a later time. This mode is best if you expect a long runtime for the sensor, because it is less resource intensive and frees up workers for other tasks.
- `poke_interval`: If using `poke` mode, this is the time in seconds that the sensor waits in between checks for whether the condition is met. The default is 30 seconds.
- `exponential_backoff`: If using `poke` mode and set to `True`, this will allow for exponentially longer wait times between pokes.
- `timeout`: The total time in seconds the sensor should wait for. If the condition has not been met when this time is reached, the task will fail. 
- `soft_fail`: If set to `True`, the task will be marked as skipped on failure.

Beyond these parameters, how to use each sensor will differ depending on the sensor's purpose. Below we describe some of the most commonly used sensors.

### Commonly Used Sensors

Many Airflow provider packages contain sensors that wait for various criteria in different source systems. There are too many to cover all of them here, but below are some of the most basic and commonly used sensors that we think everybody should be aware of:

- [`S3KeySensor`](https://registry.astronomer.io/providers/amazon/modules/s3keysensor): Waits for a key (file) to land in an S3 bucket. This sensor is useful if you want your DAG to process files from S3 as they arrive.
- [`DateTimeSensor`](https://registry.astronomer.io/providers/apache-airflow/modules/datetimesensor): Waits for a specified date and time to pass. This sensor is useful if you want different tasks within the same DAG to run at different times.
- [`ExternalTaskSensor`](https://registry.astronomer.io/providers/apache-airflow/modules/externaltasksensor): Waits for an Airflow task to be completed. This sensor is useful if you want to implement [cross-DAG dependencies](https://www.astronomer.io/guides/cross-dag-dependencies) in the same Airflow environment.
- [`HttpSensor`](https://registry.astronomer.io/providers/http/modules/httpsensor): Waits for an API to be available. This sensor is useful if you want to ensure your API requests are successful.
- [`SqlSensor`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlsensor): Waits for data to be present in a SQL table. This sensor is useful if you want your DAG to process data as it arrives in your database.
- [`PythonSensor`](https://registry.astronomer.io/providers/apache-airflow/modules/pythonsensor): Waits for a Python callable to return `True`. This sensor is useful if you want to implement complex conditions in your DAG.

> To browse and search all of the available sensors in Airflow, visit the [Astronomer Registry](https://registry.astronomer.io/modules?types=sensors), the discovery and distribution hub for Apache Airflow integrations created to aggregate and curate the best bits of the ecosystem.

### Example Implementation

To show how you might implement a DAG using the `SqlSensor`, consider the following code: 

```python
from airflow.decorators import task, dag
from airflow.sensors.sql import SqlSensor

from typing import Dict
from datetime import datetime

def _success_criteria(record):
        return record

def _failure_criteria(record):
        return True if not record else False

@dag(description='DAG in charge of processing partner data',
     start_date=datetime(2021, 1, 1), schedule_interval='@daily', catchup=False)
def partner():
    
    waiting_for_partner = SqlSensor(
        task_id='waiting_for_partner',
        conn_id='postgres',
        sql='sql/CHECK_PARTNER.sql',
        parameters={
            'name': 'partner_a'
        },
        success=_success_criteria,
        failure=_failure_criteria,
        fail_on_empty=False,
        poke_interval=20,
        mode='reschedule',
        timeout=60 * 5
    )
    
    @task
    def validation() -> Dict[str, str]:
        return {'partner_name': 'partner_a', 'partner_validation': True}
    
    @task
    def storing():
        print('storing')
    
    waiting_for_partner >> validation() >> storing()
    
dag = partner()
```

This DAG is waiting for data to be available in a Postgres database before running validation and storing tasks. The `SqlSensor` task (`waiting_for_partner`) runs the `CHECK_PARTNER.sql` script every 20 seconds (the `poke_interval`) until the criteria is met. The `mode` is set to `reschedule`, meaning between each 20 second interval the task will not take a worker slot. The `timeout` is set to 5 minutes, so if the data hasn't arrived by that time, the task will be marked as failed. Once the `SqlSensor` criteria is met, the DAG will move on to the downstream tasks. You can find the full code for this example in [this repo](https://github.com/marclamberti/webinar-sensors).

## Sensor Best Practices

Sensors are easy to implement, but there are a few things to keep in mind when using them to ensure you are getting the best possible Airflow experience. The following tips will help you avoid any performance issues when using sensors:

- **Always** define the `timeout` parameter for your sensor. The default for this parameter is one week, which is a long time for your sensor to be running! When you implement a sensor, take care to know your use case and how long you expect your sensor to be waiting and define your timeout accordingly.
- Whenever possible and especially for long-running sensors, use the `reschedule` mode so your sensor is not constantly occupying a worker slot. This will help avoid deadlocks in Airflow from sensors taking all the available worker slots. The exception to this rule is the following point:
- If your `poke_interval` is very short (less than about 5 minutes), use the `poke` mode. Using `reschedule` mode in this case can overload your scheduler.
- Define a meaningful `poke_interval` based on your use case. There is no need for the task to check the condition every 30 seconds (the default) if you know the total amount of waiting time is likely to be 30 minutes.

## Smart Sensors

## Async Operators

