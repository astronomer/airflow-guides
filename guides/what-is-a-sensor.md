---
title: "What is a Sensor"
description: "What is a Sensor?"
date: 2018-05-21T00:00:00.000Z
slug: "what-is-sensor"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks"]
---

# Sensors
Sensors are a special kind of operator. When they run, they will wait until a certain criteria is met before the will complete and let their downstream tasks execute. This is a great way to have portions of your DAG wait on some external system.

## S3 Key Sensor
```python
s1 = S3KeySensor(
        task_id='s3_key_sensor',
        bucket_key='{{ ds_nodash }}/my_file.csv',
        bucket_name='my_s3_bucket',
        aws_conn_id='my_aws_connection',
    )
```
This sensor will check for the existence of a specified key in S3 every few seconds until it finds it or times out. If it finds it, it will be marked as success and allow downstream taks to run. If it times out, it will fail and prevent downstream tasks from running.

[S3KeySensor Code](https://github.com/apache/airflow/blob/master/airflow/sensors/s3_key_sensor.py)

## Sensors Params
There are plenty of other sensors out there that due things such as check a database for a certain row, wait for a certain time of day or sleep for a certain amount of time. All sensors inherit from the `BaseSensorOperator` and have 4 parameters you can set on any sensor.

- **soft_fail:** Set to true to mark the task as SKIPPED on failure
- **poke_interval:** Time in seconds that the job should wait in between each try
- **timeout:** Time, in seconds before the task times out and fails.
- **mode:** How the sensor operates. Options are: `{ poke | reschedule }`, default is `poke`. When set to `poke` the sensor is taking up a worker slot for its whole execution time and sleeps between pokes. Use this mode if the expected runtime of the sensor is short or if a short poke interval is required. When set to `reschedule` the sensor task frees the worker slot when the criteria is not yet met and it's rescheduled at a later time. Use this mode if the expected time until the criteria is met is. The poke interval should be more than one minute to prevent too much load on the scheduler.