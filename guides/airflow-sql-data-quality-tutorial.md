---
title: "Airflow Data Quality Checks with SQL Operators"
description: "Executing queries in Apache Airflow DAGs to ensure data quality."
date: 2021-09-09T00:00:00.000Z
slug: "airflow-sql-data-quality-tutorial"
tags: ["Database", "SQL", "DAGs", "Data Quality"]
---

> Note: More example code for data quality checks can be found in [this Github repo](https://github.com/astronomer/airflow-data-quality-demo/).

## Overview

Data quality is key to the success of an organization's data systems. In Airflow, implementing data quality checks in DAGs is both easy and robust. With in-DAG quality checks, you can halt pipelines and alert stakeholders before bad data makes its way to a production lake or warehouse.

Executing SQL queries is one of the most common use cases for data pipelines, and it's a simple and effective way to implement data quality checks. Using Airflow, you can quickly put together a pipeline specifically for checking data quality, or you can add quality checks to existing ETL/ELT with just a few lines of boilerplate code.

In this guide, we'll highlight three SQL Check Operators and show examples of how each one can be used to build a robust data quality suite for your DAGs. If you aren't familiar with SQL Operators in general, check out Astronomer's [SQL tutorial](https://www.astronomer.io/guides/airflow-sql-tutorial) first.

## SQL Check Operators

The SQL Check Operators are versions of the `SQLOperator` that offer different abstractions over SQL queries to streamline data quality checks. One main difference between the SQL Check Operators and the standard [`BaseSQLOperator`](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.BaseSQLOperator) is that the Check Operators ultimately respond with a boolean, meaning the task will fail if the resulting query fails. This is particularly helpful in stopping a data pipeline before bad data makes it to a given destination. With Airflow's logging capabilities, the lines of code (and even specific values in lines) which fail the check are highly observable.

The following SQL Check Operators are recommended for this use case:

- **SQLColumnCheckOperator**: An operator capable of running multiple pre-defined data quality checks on multiple columns within the same task.
- **SQLTableCheckOperator**: An operator to run multiple checks involving aggregate functions for one or more columns.
- **[SQLCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLCheckOperator)**: A flexible operator that takes any SQL query. This operator is useful for more complicated checks (e.g. including `WHERE` statements or spanning several tables of your database).

The newly added SQLColumnCheckOperator and SQLTableCheckOperator are set to replace three legacy operators with more narrow functionality:  

- [SQLValueCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLValueCheckOperator): A simpler operator that can be used when a specific, known value is being checked either as an exact value or within a percentage threshold.
- [SQLIntervalCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLIntervalCheckOperator): A time-based operator. Used for checking current data against historical data.
- [SQLThresholdCheckOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.SQLThresholdCheckOperator): An operator with flexible upper and lower thresholds, where the threshold bounds may also be described as SQL queries that return a numeric value.

### Requirements

The SQLColumnCheckOperator and the SQLTableCheckOperator are available in the [common SQL provider package](https://pypi.org/project/apache-airflow-providers-common-sql/) available with:

```bash
pip install apache-airflow-providers-common-sql
```

The SQLCheckOperator and legacy SQL Check Operators are built into the Airflow core.

### Connection to a database

The SQL Check Operators work with any database that can be queried using SQL. You simply have to define your [connection](https://www.astronomer.io/guides/connections/) in the Airflow UI and then pass the connection id to the operator parameter `conn_id`.

> **Note**: Currently the operators cannot support BigQuery `job_id`s.

The target table can be specified as a string using the `table` parameter for the SQLColumnCheckOperator and SQLTableCheckOperator. When using the SQLCheckOperator you can override the database defined in your Airflow connection by passing a different value to the `database` argument. The target table for the SQLCheckOperator has to be given within the SQL statement.

Under the hood the operators use the information provided in the Airflow connection to get a [DbApiHook](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/hooks/dbapi/index.html#module-airflow.hooks.dbapi).

## Examples

The following examples show you when and how to use SQL Check Operators.

### Example 1 - `SQLColumnCheckOperator`

The `SQLColumnCheckOperator` uses a dictionary to define checks via the parameter `column_mapping`. The strength of this operator is the ability to run a multitude of checks within one task but still have observability on which checks passed and which failed within the Airflow logs.

This check is useful for:

- Ensuring all values in a column are above a minimum, below a maximum or within a certain range (with or without a tolerance threshold).
- Null checks.
- Checking primary key columns for uniqueness.
- Checking the number of distinct values of a column.

In the example below 6 checks on 3 different columns are performed by the `SQLColumnCheckOperator`:

- Check that "MY_DATE_COL" contains only _unique_ dates between 2017-01-01 and 2022-01-01.
- Check that "MY_TEXT_COL" has at least 10 distinct values and no `NULL` values present.
- Check that "MY_NUM_COL" contains a maximum value between 90 and 110 (100 with a tolerance of 10).

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

The resulting values then can be compared to a value input by the DAG author by using the qualifiers: `greater_than`, `geq_than`, `equal_to`, `leq_than` or `less_than`. If the resulting boolean value is `True` the check passes, otherwise it fails.

### Example 2 - SQLTableCheckOperator

The `SQLTableCheckOperator` provides a way to check the validity of SQL statements containing aggregates over the whole table. There is no limit to the amount of columns these statements can involve or to their complexity. They are provided to the operator as a dictionary via the `checks` parameter.

The `SQLTableCheckOperator` is useful for:

- Checks that include aggregate values using the whole table (e.g. comparing the average of one column to the average of another using the SQL `AVG()` function).
- Row sum checks.
- Comparisons between multiple columns.

In the example below, two checks are defined `my_row_count_check` and `my_column_sum_comparison_check` (the names can be freely chosen). The first check runs a SQL statement asserting that the table contains at least 1000 rows, while the second check compares the sum of two columns.

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

Under the hood, the operator performs a `CASE WHEN` statement on each of the checks, assigning `1` to the checks that passed and `0` to the checks that failed. Afterwards, the operator looks for the minimum of these results and marks the task as failed if the minimum is `0`.

### Example 3 - `SQLCheckOperator`

The `SQLCheckOperator` returns a single row from a provided SQL query and checks to see if any of the returned values in that row are `False`. If any values are `False`, the task fails. This operator allows a great deal of flexibility in checking:

- A specific, single column value.
- Part of or an entire row compared to a known set of values.
- Options for categorical variables and data types.
- The results of any other function that can be written as a SQL query.

The following code snippet shows you how to use the operator in a DAG:

```python
SQLCheckOperator(
    conn_id="<your connection id>"
    task_id="yellow_tripdata_row_quality_check",
    sql="row_quality_yellow_tripdata_check.sql",
    params={"pickup_datetime": "2021-01-01"},
)
```

The `sql` argument can be either a complete SQL query as a string or, as in this example, a reference to a query in a local file (for Astronomer projects, this is in the `include/` directory). The `params` argument allows you to pass a dictionary of values to the SQL query, which can be accessed through the `params` keyword in the query. The `conn_id` argument points towards a previously defined Airflow connection to a database. The full code can be found in the [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).

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

### Observability

The SQLColumnCheckOperator and SQLTableCheckOperator will log each individual check into the Airflow [task logs](https://www.astronomer.io/guides/logging/).

The screenshot below shows the output of 3 checks on one column within a SQLColumnCheckOperator which have all passed when queried against a Snowflake database. You can see both the SQL query that ran and the result. In this example three checks were run on the column `DATE` concerning the minimum value, the maximum value and the amount of null values in the column. The logged line `INFO - Record: (datetime.date(2021, 4, 9), datetime.date(2022, 7, 17), 0)` lists the results of the query: the minimum date was 2021-09-04, the maximum date 2022-07-17 and there were zero null values, which satisfied the conditions of the check.

![SQLColumnCheckOperator logging of passing checks](https://assets2.astronomer.io/main/guides/sql-data-quality-tutorial/column_checks_passed.png)

All checks that fail will be listed at the end of the logs with their full SQL query and specific check that failed. The screenshot shows how the `TASK_DURATION` column failed the check to have a minimum of greater than or equal 0 by having a minimum of -1251 instead.

![SQLColumnCheckOperator logging of failed checks](https://assets2.astronomer.io/main/guides/sql-data-quality-tutorial/column_checks_failed.png)

## Conclusion

After reading this guide, you should feel comfortable using the SQL Check Operators, understanding how each one works, and getting a sense of when each one would be useful in practice. With just these three operators, you have the foundation for a robust data quality suite right in your pipelines. If you are looking for more examples, or want to see how to use backend-specific operators like Redshift, BigQuery, or Snowflake, check out Astronomer's [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).
