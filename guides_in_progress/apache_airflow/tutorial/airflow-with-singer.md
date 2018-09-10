---
title: Using Airflow with Singer
sidebar: platform_sidebar
---

## Singer
[Singer](https://www.singer.io) is an open-source ETL framework maintained by Stitch Data. The core concepts of Singer revolve around "Taps" (data sources) and "Targets" (destinations), which are executed as Bash commands.

## Taps and Targets
A full list of Taps and Targets can be found in the [Singer Github](https://github.com/singer-io).

These Taps and Targets are also available for installation via PyPi.

## Singer Operator
While you can use the standard [Bash Operator](https://github.com/apache/incubator-airflow/blob/master/airflow/operators/bash_operator.py) to execute Singer components, you can also take advantage of the custom [Singer Operator](https://github.com/airflow-plugins/singer_plugin/blob/master/operators/singer_operator.py).

## Example
An example of using the Singer Operator can be found [here](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/poc/singer_example.py).
