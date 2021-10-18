---
title: "Sensors 101"
description: "An introduction to Sensors in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-a-sensor"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "Basics", "Sensors"]
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
- `poke_interval`: If using `poke` mode, this is the time in seconds that the sensor waits in between checks for whether the condition is met.
- `exponential_backoff`: If using `poke` mode and set to `True`, this will allow for exponentially longer wait times between pokes.
- `timeout`: The total time in seconds the sensor should wait for. If the condition has not been met when this time is reached, the task will fail. 
- `soft_fail`: If set to `True`, the task will be marked as skipped on failure.

### Commonly Used Sensors


> To browse and search all of the available sensors in Airflow, visit the [Astronomer Registry](https://registry.astronomer.io/modules?types=sensors), the discovery and distribution hub for Apache Airflow integrations created to aggregate and curate the best bits of the ecosystem.

## Sensor Best Practices
When (And When Not) to Use Sensors

## Smart Sensors

## Async Operators

