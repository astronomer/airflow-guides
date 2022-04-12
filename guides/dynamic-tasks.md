---
title: "Dynamic Tasks in Airflow"
description: "How to dynamically create tasks at runtime in your Airflow DAGs."
date: 2022-04-15T00:00:00.000Z
slug: "dynamic-tasks"
heroImagePath: null
tags: ["Tasks"]
---

## Overview

With the release of Airflow 2.3 (LINK?), users can write DAGs that dynamically generate parallel tasks at runtime. This feature, known as dynamic task mapping, is a paradigm shift for DAG design in Airflow. Prior to Airflow 2.3, tasks could only be generated dynamically at the time the DAG was parsed, meaning you had to change your DAG code if you needed to adjust tasks based on some external factor. Now, you can easily design your DAGs to respond to external criteria by creating a varied number of tasks each time they are run.

In this guide, we'll cover the concept of dynamic task mapping, common use cases where this feature is helpful, and a couple of example implementations of this feature.

## Dynamic Task Concepts

## Common Use Cases

## Example Implementations

In this section we'll show how to implement dynamic task mapping for two classic use cases: processing files in S3 and hyper-parameter tuning a model. The first will highlight use of traditional Airflow operators, and the second will use decorated functions and the TaskFlow API.

### Processing Files From S3

traditional operators
get files -> load files -> [delete files, transform task] in Snowflake (snowflake operator) (or single task, but show how to create multiple tasks afterwards)

Keep in mind the format needed for the parameter you are mapping on. In the example above, we write our own Python function to get the S3 keys because the `S3toSnowflakeOperator` requires *each* `s3_key` parameter to be in a list format, and the `s3_hook.list_keys` function returns a single list with all keys. By writing our own simple function, we can turn our resulting list into a list of lists that can be used by the downstream operator. 

### Hyperparameter Tuning a Model
decorated tasks