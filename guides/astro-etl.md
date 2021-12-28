---
title: "Astro for ETL"
description: "Using the `astro` library to implement ETL use cases in Airflow."
date: 2022-01-10T00:00:00.000Z
slug: "astro-etl"
heroImagePath: null
tags: ["DAGs", "astro", "ETL"]
---

## Overview

The `[astro` library](https://github.com/astro-projects/astro) is an open source Python package maintained by Astronomer that provides tools to improve the DAG authoring experience for Airflow users. The available decorators and functions allow you to write DAGs based on how you want your data to move, while simplifying the transformation process between different environments.

In this guide, we’ll demonstrate how you can use `astro` functions for ETL use cases. The resulting DAGs will be easier to write and read, and require less code.

## Astro ETL Functionality

The `astro` library makes implementing ETL use cases easier by allowing you to seamlessly transition between Python and SQL for each step in your process. Steps like creating dataframes, storing intermediate results, passing context and data between tasks, and creating Airflow task dependencies are all taken care of for you. This allows you focus solely on writing execution logic in whichever language is most suited for each step, without having to worry about Airflow orchestration logic on top of it.

More specifically, `astro` has the following functions that are helpful when implementing an ETL framework (for a full list of functions, check out the [Readme](https://github.com/astro-projects/astro)):

- `load_file`: if the data you’re starting with is in CSV or parquet files (stored locally or on S3 or GCS), you can use this function to load it into your database.
- `transform`: this function allows you to transform your data with a SQL query. You define the `SELECT` statement, and the results will automatically be stored in a new table. By default, the `output_table` will be placed in a `tmp_astro` schema and will be given a unique name each time the DAG runs, but you can overwrite this behavior by defining a specific `output_table` in your function. You can then pass the results of the `transform` downstream to the next task as if it were a native Python object.
- `dataframe`: similar to `transform` for SQL, the `dataframe` function allows you to implement a transformation on your data using Python. You can easily store the results of the `dataframe` function in your database by specifying an `output_table`, which is useful if you want to switch back to SQL in the next step or load final results to your database.

In the next section, we’ll show a practical example implementing these functions.

## Example Implementation

To show `astro` for ETL in action, we’ll take a pretty common use case: managing billing data. We need to extract customer subscription data by joining the results of several complex queries. Then we perform some transformations on the data before loading it into a results table. Below we’ll show what the original DAG looked like, and then how `astro` can make it easier.

### The DAG Before Astro

Here is our billing subscription ETL DAG implemented with OSS Airflow operators and decorators and making use of the TaskFlow API:

```python

```

While we achieved our ETL goal with the DAG above, there are a couple of limitations that make the implementation more complicated:

- Since there is no way to pass results from `PostgresOperator` query to the next task, we have to write our query in a `_DecoratedPythonOperator` function, and do the conversion from SQL to a dataframe explicitly ourselves.
- Some of our transformations are better suited to SQL, and others are better suited to Python, but transitioning between the two requires extra boilerplate code to explicitly make those conversions.
- While the TaskFlow API makes it easier to pass data between tasks here, it is storing the resulting dataframes in as XComs by default. This means we need to worry about the size of our data. We could implement a custom XCom backend, but that would be extra lift.
- Loading data back to Postgres after the transformation is complete requires another Python task where we explicitly write the code ourselves.

### The DAG With Astro

Next, we’ll show how to rewrite the DAG using `astro` to alleviate the challenges listed above. 

```python

```

The key differences in this implementation are:

-