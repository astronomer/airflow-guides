---
title: "Airflow Data Quality Checks with SQL Operators"
description: "Executing queries in Apache Airflow DAGs to ensure data quality."
date: 2021-09-09T00:00:00.000Z
slug: "airflow-sql-data-quality-tutorial"
tags: ["Database", "SQL", "DAGs", "Data Quality"]
---

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/airflow-data-quality-demo/).

## Overview

Data quality is key to the success of an organization's data systems. In Airflow, implementing data quality checks in DAGs is both easy and robust. With in-DAG quality checks, you can halt pipelines and alert stakeholders before bad data makes its way to a production lake or warehouse.

Executing SQL queries is one of the most common use cases for data pipelines, and it's a simple and effective way to implement data quality checks. Using Airflow, you can quickly put together a pipeline specifically for checking data quality, or you can add quality checks to existing ETL/ELT with just a few lines of boilerplate code.

In this guide, we'll introduce the different SQL Check Operators and show examples of how each one can be used to build a robust data quality suite for your DAGs. If you aren't familiar with SQL Operators in general, check out Astronomer's [SQL tutorial](https://www.astronomer.io/guides/airflow-sql-tutorial) first.

## SQL Check Operators

The SQL Check Operators are versions of the `SQLOperator` that streamline different checks against queries. One main difference between the SQL Check Operators and the standard [`BaseSQLOperator`](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.BaseSQLOperator) is that the Check Operators ultimately respond with a boolean, meaning the task will fail if the resulting query fails. This is particularly helpful in stopping a data pipeline before bad data makes it to a given destination. With Airflow's logging capabilities, the lines of code (and even specific values in lines) which fail the check are highly observable.

Airflow currently supports the following SQL Check Operators:

- **[SQLCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLCheckOperator)**: A flexible operator that takes any SQL query. Useful when many values in a row must be checked against different metrics, or when your organization already has SQL queries performing quality checks
- **[SQLValueCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLValueCheckOperator)**: A simpler operator that is useful when a specific, known value is being checked either as an exact value or within a percentage threshold
- **[SQLIntervalCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLIntervalCheckOperator)**: A time-based operator. Useful for checking current data against historical data
- **[SQLThresholdCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLThresholdCheckOperator)**: An operator with flexible upper and lower thresholds, where the threshold bounds may also be described as SQL queries that return a numeric value
- **SQLColumnCheckOperator**: An operator capable of running multiple pre-defined data quality checks on multiple columns.
- **SQLTableCheckOperator**: An operator to run checks involving aggregate functions over one or more columns.

## Examples

The following examples show you when and how to use each of the SQL Check Operators.

### Example 1 - `SQLCheckOperator`

The `SQLCheckOperator` returns a single row from a provided SQL query and checks to see if any of the returned values in that row are `False`. If any values are `False`, the task fails. This operator allows a great deal of flexibility in checking:

- A specific, single column value.
- Part of or an entire row compared to a known set of values.
- Options for categorical variables and data types.
- The results of any other function that can be written as a SQL query.

The following code snippet shows you how to use the operator in a DAG:

```python
SQLCheckOperator(
    task_id="yellow_tripdata_row_quality_check",
    sql="row_quality_yellow_tripdata_check.sql",
    params={"pickup_datetime": "2021-01-01"},
)
```

The `sql` argument can be either a complete SQL query as a string or, as in this example, a reference to a query in a local file (for Astronomer projects, this is in the `include/` directory). The `params` argument allows you to pass a dictionary of values to the SQL query, which can be accessed through the `params` keyword in the query. The `database` and `conn_id` arguments are left out of the example, so the default values will be used. The full code can be found in the [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).

Because the `SQLCheckOperator` can process a wide variety of queries, it's important to use the right SQL query for the job at hand. The following query (which we pass into the `sql` argument) was crafted for the specific use case of analyzing daily taxicab data, so the values checked in each case's equation come from domain knowledge. Even the `WHERE` clause needs a data steward to know that to return a unique row, both the `vendor_id` and `pickup_datetime` are needed.

The query used in the `sql` argument is:

```sql
SELECT vendor_id, pickup_datetime,
  CASE WHEN dropoff_datetime > pickup_datetime THEN 1 ELSE 0 END AS date_check,
  CASE WHEN passenger_count >= 0 THEN 1 ELSE 0 END AS passenger_count_check,
  CASE WHEN trip_distance >= 0 AND trip_distance <= 100 THEN 1 ELSE 0 END AS trip_distance_check,
  CASE WHEN ROUND((fare_amount + extra + mta_tax + tip_amount + improvement_surcharge + COALESCE(congestion_surcharge, 0)), 1) = ROUND(total_amount, 1) THEN 1
       WHEN ROUND(fare_amount + extra + mta_tax + tip_amount + improvement_surcharge, 1) = ROUND(total_amount, 1) THEN 1 ELSE 0 END AS fare_check
FROM yellow_tripdata
WHERE pickup_datetime IN (SELECT pickup_datetime FROM yellow_tripdata ORDER BY RANDOM() LIMIT 1)
```

If we want to use a specific date to quality check a row instead of using a random `pickup_datetime`, we can use the `params` passed into the operator like so:

```sql
WHERE pickup_datetime = '{{ params.pickup_datetime }}'
```

By using `CASE` statements in the SQL query, we can check very specific cases of data quality that should always be true for this use case:

- Drop-offs always occur after pickups.
- A trip is only valid if there is at least one passenger.
- A trip needs to be in a range allowed by the taxi company (in this case, we assume there is a maximum allowed trip distance of 100 miles).
- Each of the components of the total fare should add up to the total fare.

Using a for loop, tasks are generated to run this check on every row or other subset of the data. In the SQL above, a `pickup_datetime` is chosen randomly, and the corresponding code uses a loop to spot-check ten rows. In the example DAG below, we can see how the loop results in `TaskGroups` that can be collapsed or expanded in the Airflow UI:

![An example DAG showing data quality checks as part of a pipeline.](https://assets2.astronomer.io/main/guides/sql-data-quality-tutorial/example_dq_dag.png)

In the example DAG above, we see exactly how our data quality checks fit into a pipeline. By loading the data into Redshift then performing checks as queries, we are offloading compute resources from Airflow to Redshift, which frees up Airflow to act only as an orchestrator.

For a production pipeline, data could first be loaded from S3 to a temporary staging table, then have its quality checks completed. If the quality checks succeed, another `SQLOperator` can load the data from staging to a production table. If the data quality checks fail, the pipeline can be stopped, and the staging table can be either used to help diagnose the data issue or scrapped to save resources. To see the complete example DAG and run it for yourself, check out the [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).

### Example 2 - `SQLValueCheckOperator`

The `SQLValueCheckOperator` is simpler than the `SQLCheckOperator` but equally useful. It checks the results of a query against a specific pass value, and ensures the checked value is within a percentage threshold of the pass value. The pass value can be any type, but the threshold can only be used with numeric types. This check is useful for:

- Checking the row count of a table within a tolerance threshold.
- Ensuring all text values in a record or set of records are correct (for example, checking text country codes against numeric ones).

The task below shows how to use this operator to check the row count of a table within a tolerance threshold:

```python
SQLValueCheckOperator(
    task_id="check_row_count",
    sql="SELECT COUNT(*) FROM yellow_tripdata",
    pass_value=20000,
    threshold=0.01
)
```

The `sql` argument is a query that ensures the actual table row count is our known `pass_value`, 20000, and that the `pass_value` is within a 1% tolerance, given in the `threshold` argument. The SQL query is a simple one-liner, so we just include it as a string directly in the argument field. Again, `database` and `conn_id` are left as defaults.

### Example 3 - `SQLIntervalCheckOperator`

The `SQLIntervalCheckOperator` is a little more complex than the previous operators. By default, it checks data against reference data from seven days prior to the run date (using Airflow's `{{ ds }}` macro). You provide a set of metric thresholds as a dictionary for each metric that is being checked. The keys of the dictionary are SQL expressions that return data for the current day and the reference day, and the values of the dictionary are the ratios used as a threshold. The current day's data is compared against the reference day's data using a ratio formula, and if the ratio formula produces a result outside of the threshold, the task fails. The two formulas are:

- Max-over-min (default), which calculates the maximum of the current day's and reference day's data divided by the minimum of the two: `max(cur, ref) / min(cur, ref)`
- Relative difference, which calculates the absolute value of the difference between the current and reference days, divided by the reference day: `abs(cur-ref) / ref`

This operator works well for use cases where you know certain metrics should be close in value, or have close statistics, to the same metrics on previous days, weeks, or other time scales.

The code snippet checks to see whether the average distance of a taxi ride today is within 1.5 times the average distance of yesterday's rides:

```python
SQLIntervalCheckOperator(
    task_id="check_interval_data",
    days_back=1,
    date_filter_column="upload_date",
    metrics_threshold={"AVG(trip_distance)": 1.5}
)
```

In the task above, we are looking only one day back using the `days_back` argument. We set the `date_filter_column` argument  to `upload_date`, which defaults to `ds`. We set the `metrics_threshold` argument to a dictionary of one key-value pair, where the key is a SQL expression that returns results for both dates and the value is the threshold that the calculated ratio of the results must not exceed.

### Example 4 - `SQLThresholdCheckOperator`

The `SQLThresholdCheckOperator` works similarly to the `SQLValueCheckOperator`. Instead of a single threshold, there is a min and max given, making this operator more dynamic in the type and scale of thresholding. The min and max thresholds can be numeric types or SQL expressions that result in a numeric type. Like the other SQL Check Operators, only the first row returned by the given SQL queries is used in the boolean evaluation. This is true for all of the parameters that can take a SQL query (`sql`, `min_threshold`, and `max_threshold`). This operator is great for use cases where a metric like a minimum, maximum, sum, or aggregate, has to be between certain values.

The example below ensures that the maximum passenger count for all rides is between 1 and 8 passengers, our assumed minimum and maximum number of potential riders for any type of taxicab:

```python
SQLThresholdCheckOperator(
    task_id="check_threshold",
    sql="SELECT MAX(passenger_count)",
    min_threshold=1,
    max_threshold=8
)
```

### Example 5 - `SQLColumnCheckOperator`

The `SQLColumnCheckOperator` like the `SQLIntervalCheckOperator` uses a dictionary to define checks via the parameter `column_mapping`. The strength of this operator is the ability to run a multitude of checks within one task but still have observability on which checks passed and which failed within the Airflow logs.

This check is useful for:

- Ensuring all values in a column are above a minimum, below a maximum or within a certain range (with or without a tolerance threshold).
- Null checks.
- Checking primary key columns for uniqueness.
- Checking the number of distinct values of a column.

In the example below 6 checks on 3 different columns are performed by the `SQLColumnCheckOperator`:

- "MY_DATE_COL" is checked to contain only _unique_ dates between 2017-01-01 and 2022-01-01.
- "MY_TEXT_COL" is checked to have at least 10 distinct values and no `NULL` values present.
- "MY_NUM_COL" is checked to contain a maximum value between 90 and 110 (100 with a tolerance of 10).

```python
SQLColumnCheckOperator(
        task_id="check_columns",
        conn_id=<your database connection id>,
        table=<your table>,
        column_mapping={
            "MY_DATE_COL": {
                "min": {"greater_than": datetime.date(2017, 1, 1)},
                "max": {"less_than": datetime.date(2022, 1, 1)},
                "unique_check": {"equal_to": 0}
            },
            "MY_TEXT_COL": {
                "distinct_check": {"geq_than": 10},
                "null_check": {"equal_to": 0}
            },
            "MY_NUM_COL": {
                "max": {"equal_to": 100, "tolerance": 10}
            },
        }
    )
```

The `SQLColumnCheckOperator` offers 5 options for column checks which are abstractions over SQL statements:

- "min": `"MIN(column) AS column_min"`
- "max" `"MAX(column) AS column_max"`
- "unique_check": `"COUNT(column) - COUNT(DISTINCT(column)) AS column_unique_check"`
- "distinct_check" `"COUNT(DISTINCT(column)) AS column_distinct_check"`
- "null_check": `"SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) AS column_null_check"`

The resulting values then can be compared to a value input by the dag author by using the qualifiers: `greater_than`, `geq_than`, `equal_to`, `leq_than` or `less_than`. If the resulting boolean value is `True` the check passes, otherwise it fails.

### Example 6 - SQLTableCheckOperator

The `SQLTableCheckOperator` provides a way to check the validity of SQL statements containing aggregates over the whole table. There is no limit to the amount of columns these statements can involve or to their complexity and they are provided to the operator as dictionary via the `checks` parameter.

The `SQLTableCheckOperator` is useful for:

- Checks that include aggregate values using the whole table.
- Row sum checks.
- Comparisons between multiple columns.

In the example below two checks are defined `my_row_count_check` and `my_column_sum_comparison_check` (the names can be freely chosen). The first check runs a SQL statement asserting that the table contains at least 1000 rows, while the second check compares the sum of two columns.

```python
SQLTableCheckOperator(
    task_id="table_checks",
    conn_id=<your database connection id>,
    table=<your table>,
    checks={
        "my_row_count_check": {
            "check_statement": "COUNT(*) >= 1000"
            },
        "my_column_sum_comparison_check": {
            "check_statement": "SUM(MY_COL_1) < SUM(MY_COL_2)"
            }
    }
)
```

Under the hood the operator performs a `CASE WHEN` statement on each of the checks assinging `1` to the checks that passed and `0` to the checks that did not. Afterwards the operator looks for the minimum of these results and marks the task as failed if the minimum is `0`.

## Conclusion

After reading this guide, you should feel comfortable using any of the SQL Check Operators, understanding how each one works, and getting a sense of when each one would be useful in practice. With just these six operators, you have the foundation for a robust data quality suite right in your pipelines. If you are looking for more examples, or want to see how to use backend-specific operators like Redshift, BigQuery, or Snowflake, check out Astronomer's [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).
