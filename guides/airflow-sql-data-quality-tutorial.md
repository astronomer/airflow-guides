---
title: "Using Airflow to Execute SQL for Data Quality Use Cases"
description: "Executing queries, parameterizing queries, and embedding SQL-driven ETL in Apache Airflow DAGs to ensure data quality."
date: 2021-09-09T00:00:00.000Z
slug: "airflow-sql-data-quality-tutorial"
tags: ["Database", "SQL", "DAGs", "Data Quality"]
---

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/airflow-data-quality-demo/).

## Overview

Executing SQL queries is one of the most common use cases for data pipelines and a simple and effective way to implement data quality checks. Using Airflow, you can quickly put together a pipeline specifically for checking data quality or add quality checks to existing ETL/ELT with just a few lines of boilerplate code.

In this guide, we'll introduce the different SQL Check Operators and show examples of how each one can be used to build a robust data quality suite for your DAGs. If you aren't familiar with SQL Operators in general, check out Astronomer's [SQL tutorial](https://www.astronomer.io/guides/airflow-sql-tutorial) first.

## SQL Check Operators

The SQL Check Operators are specific versions of the `SQLOperator` that streamline different checks against queries. One main difference between the Check Operators and the standard [`BaseSQLOperator`](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.BaseSQLOperator) is that the Check Operators ultimately respond with a boolean, meaning the task will fail if the resulting query fails. This is extremely helpful in stopping a data pipeline before bad data makes it to the destination. With Airflow's logging capabilities, knowing exactly which line (and even which value in that line) failed the check becomes highly observable.

Airflow currently supports the following SQL Check Operators:

- [SQLCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLCheckOperator)

- [SQLValueCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLValueCheckOperator)

- [SQLIntervalCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLIntervalCheckOperator)

- [SQLThresholdCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLThresholdCheckOperator)

## Examples

The following examples show you how to use each of the aforementioned operators and give some background on when each one will be most useful.

### Example 1 - `SQLCheckOperator`

The `SQLCheckOperator` returns a single row from a provided SQL query and checks to see if any of the returned values in that row are `False`. If any values are `False`, the task fails. This operator allows a great deal of flexibility in what is being checked: a specific single value, NULL-checking and other type-checking, values of an entire row compared to a known set of values, specific calculations like `SUM`s or `AGG`s, or any other function that can be written into a SQL query.

The following code snippet shows you how to use the operator in a DAG.

```python
SQLCheckOperator(
    task_id=f"forestfire_row_quality_check",
    sql="sql/row_quality_yellow_tripdata_check.sql",
    params=values,
)
```

The `sql` argument can be either the complete SQL query as a string or, as in this example, a reference to a query in a local file. The `params` argument allows you to pass a dictionary of values to the SQL query, which can be accessed through the `params` keyword in the query, as shown in the SQL code snippet below. The `database` and `conn_id` arguments are left out of the example, so the default values will be used. The full code can be found in the [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).

The query used in the `sql` argument is:

```sql
SELECT vendor_id,
  CASE WHEN dropoff_datetime > pickup_datetime THEN 1 ELSE 0 END AS date_check,
  CASE WHEN passenger_count > 0 THEN 1 ELSE 0 END AS passenger_count_check,
  CASE WHEN trip_distance > 0 AND trip_distance <= 100 THEN 1 ELSE 0 END AS trip_distance_check,
  CASE WHEN (fare_amount + extra, mta_tax + tip_amount + improvement_surcharge + COALESCE(congestion_surcharge, 0)) = total_amount THEN 1 ELSE 0 END AS fare_check
FROM {{ params.table }}
WHERE vendor_id = {{ params.vendor_id }}
  AND pickup_datetime = {{ params.pickup_datetime }}
```

By using `CASE` statements in the SQL query, we can check very specific cases of data quality that we, as the data stewards, know should always be true:

- Drop-offs always occur after pickups
- A trip is only valid if there is at least one passenger
- A trip needs to be in a range allowed by the taxi company (in this case, we assume there is a maximum allowed trip distance of 100 miles)
- Each of the components of the total fare should add up to the total fare

Using a for loop, tasks can be generated to run this check on every row of the data or on any desired subset of the data for spot-checks.

### Example 2 - `SQLValueCheckOperator`

The `SQLValueCheckOperator` is simpler than the `SQLCheckOperator` but still incredibly useful. It checks the results of a query against a specific pass value, and, if given, ensures the value is within a percentage threshold. The pass value can be any type, but the threshold can only be used with numeric types. This check is useful for:

- Checking the row count of a table
- Ensuring all text values in a record or set of records are correct (say, checking text country codes against numeric ones)

The task below shows how to use this operator to check the row count of a table within a tolerance threshold:

```python
SQLValueCheckOperator(
    task_id="check_row_count",
    sql=f"SELECT COUNT(*) FROM yellow_tripdata",
    pass_value=20000,
    threshold=0.01
)
```

The `sql` argument is a query that ensures the actual table row count is our known `pass_value`, 20000, and that the `pass_value` is within a 1% tolerance, given in the `threshold` argument. The SQL query is a simple one-liner, so we just include it as a string directly in the argument field. Again, `database` and `conn_id` are left as defaults.

### Example 3 - `SQLIntervalCheckOperator`

The `SQLIntervalCheckOperator` is a little more complex than the previous operators. It operates on a time-based interval, which defaults to choosing a reference day seven days prior to the run date (using Airflow's `{{ ds }}` macro). A set of metric thresholds are given as a dictionary for each metric that is being checked, with the keys of the dictionary each being a SQL expression that returns data for the current day and the reference day, and the values of the dictionary each being the ratio used as a threshold. The current day's data are compared against the reference day's data using a ratio formula, and if the ratio formula produces a result outside of the threshold, the task fails. The two formulas are:

- Max-over-min (default), which calculates the maximum of the current day's and reference day's data divided by the minimum of the two: `max(cur, ref) / min(cur, ref)`
- Relative difference, which calculates the absolute value of the difference between the current and reference days, divided by the reference day: `abs(cur-ref) / ref`

This operator works great for use cases where you know certain metrics should be close in value, or have close statistics, to the same metrics on previous days, weeks, or other time scales.

The code snippet below shows how to use this operator to check that the average distance of a taxi ride today is within 1.5 times the average distance of yesterday's rides:

```python
SQLIntervalCheckOperator(
    task_id="check_interval_data",
    days_back=1,
    date_filter_column="upload_date",
    metrics_threshold={"AVG(trip_distance)": 1.5}
)
```

In the task above, we are only looking one day back in the `days_back` argument, comparing the current day's data to yesterday's. We overwrite the `date_filter_column` to `upload_date`, which defaults to `ds`. The `metrics_threshold` is set to a dictionary of one key-value pair, where the key is a SQL expression that returns a result used in the default ratio formula, and the value of the dictionary is the threshold that the calculated ratio must not exceed.

### Example 4 - `SQLThresholdCheckOperator`

The `SQLThresholdCheckOperator` works similarly to the `SQLValueCheckOperator`, except instead of a single threshold, there is a min and max given, making this operator more dynamic in the type and scale of thresholding. The min and max thresholds can be numeric types or SQL expressions that result in a numeric type. Only the first result in the given SQL queries, for the `sql` argument and threshold arguments, will be used in the evaluation. This operator is great for use cases where a metric like a minimum, maximum, sum, or aggregate, is known to have to be between certain values.

```python
SQLThresholdCheckOperator(
    task_id="check_threshold",
    sql="SELECT MAX(passenger_count)",
    min_threshold=1,
    max_threshold=8
)
```

The above example ensures that the maximum passenger count for all rides is between 1 and 8 passengers, our assumed minimum and maximum number of potential riders for any type of taxicab.

## Conclusion

After reading this guide, you should feel comfortable using any of the SQL Check Operators, understanding how each one works, and getting a sense of when each one would be useful in practice. With just these four operators, you have the foundation for a robust data quality suite right in your pipelines. If you are looking for more examples, or want to see how to use backend-specific operators like Redshift, BigQuery, or Snowflake, check out Astronomer's [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).
