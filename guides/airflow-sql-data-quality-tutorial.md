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

In this guide, we'll highlight three SQL Check operators and show examples how each of them can be used to build a robust data quality suite for your DAGs. If you aren't familiar with SQL operators in general, check out Astronomer's [SQL tutorial](https://www.astronomer.io/guides/airflow-sql-tutorial) first.

## SQL Check Operators

The SQL Check operators are versions of the `SQLOperator` that abstract SQL queries to streamline data quality checks. One difference between the SQL Check operators and the standard [`BaseSQLOperator`](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/sql/index.html#airflow.operators.sql.BaseSQLOperator) is that the SQL Check operators respond with a boolean, meaning the task will fail if any of the resulting queries fail. This is particularly helpful in stopping a data pipeline before bad data makes it to a given destination. With Airflow's logging capabilities, the lines of code and values which fail the check are highly observable.

The following SQL Check operators are recommended for implementing data quality checks:

- **[`SQLColumnCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqlcolumncheckoperator)**: Runs multiple predefined data quality checks on multiple columns within the same task.
- **[`SQLTableCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqltablecheckoperator)**: Runs multiple checks involving aggregate functions for one or more columns.
- **[`SQLCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlcheckoperator)**: Takes any SQL query and returns a single row that is evaluated to booleans. This operator is useful for more complicated checks (e.g. including `WHERE` statements or spanning several tables of your database).
- **[`SQLIntervalCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlintervalcheckoperator)**: Checks current data against historical data.

Additionally, two older SQL Check operators exist that can run one check at a time against a defined value or threshold:

- [`SQLValueCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlvaluecheckoperator): A simpler operator that can be used when a specific, known value is being checked either as an exact value or within a percentage threshold.
- [`SQLThresholdCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlthresholdcheckoperator): An operator with flexible upper and lower thresholds, where the threshold bounds may also be described as SQL queries that return a numeric value.

We recommend the use of the `SQLColumnCheckOperator` and `SQLTableCheckOperator` over the `SQLValueCheckOperator` and `SQLThresholdCheckOperator` whenever possible to improve code readability.

### Requirements

The `SQLColumnCheckOperator` and the `SQLTableCheckOperator` are available in the [common SQL provider package](https://pypi.org/project/apache-airflow-providers-common-sql/) which can be installed with:

```bash
pip install apache-airflow-providers-common-sql
```

The `SQLCheckOperator`, `SQLIntervalCheckOperator`, `SQLValueCheckOperator` and `SQLThresholdCheckOperator` are built into core Airflow and do not require a separate package installation.

### Database Connection

The SQL Check operators work with any database that can be queried using SQL. You simply have to define your [connection](https://www.astronomer.io/guides/connections/) in the Airflow UI and then pass the connection id to the operator's `conn_id` parameter.

> **Note**: Currently the operators cannot support BigQuery `job_id`s.

The target table can be specified as a string using the `table` parameter for the `SQLColumnCheckOperator` and `SQLTableCheckOperator`. When using the `SQLCheckOperator`, you can override the database defined in your Airflow connection as needed by passing a different value to the `database` argument. The target table for the `SQLCheckOperator` has to be given within the SQL statement.

## Example `SQLColumnCheckOperator`

The `SQLColumnCheckOperator` has a `column_mapping` parameter which stores a dictionary of checks. Using this dictionary, it can run many checks within one task and still provide observability in the Airflow logs over which checks passed and which failed.

This check is useful for:

- Ensuring all values in a column are above a minimum, below a maximum or within a certain range (with or without a tolerance threshold).
- Null checks.
- Checking primary key columns for uniqueness.
- Checking the number of distinct values of a column.

In the example below, we perform 6 checks on 3 different columns using the `SQLColumnCheckOperator`:

- Check that "MY_DATE_COL" contains only _unique_ dates between 2017-01-01 and 2022-01-01.
- Check that "MY_TEXT_COL" has at least 10 distinct values and no `NULL` values present.
- Check that "MY_NUM_COL" contains a maximum value of 100 with a 10% tolerance, i.e. accepting values between 90 and 110.

```python
check_columns = SQLColumnCheckOperator(
        task_id="check_columns",
        conn_id=example_conn,
        table=example_table,
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
                "max": {"equal_to": 100, "tolerance": 0.1}
            },
        }
    )
```

The `SQLColumnCheckOperator` offers 5 options for column checks which are abstractions over SQL statements:

- "min": `"MIN(column) AS column_min"`
- "max": `"MAX(column) AS column_max"`
- "unique_check": `"COUNT(column) - COUNT(DISTINCT(column)) AS column_unique_check"`
- "distinct_check": `"COUNT(DISTINCT(column)) AS column_distinct_check"`
- "null_check": `"SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) AS column_null_check"`

The resulting values can be compared to an expected value using any of the following qualifiers:

- `greater_than`
- `geq_to` (greater or equal than)
- `equal_to`
- `leq_to` (lesser or equal than)
- `less_than`

> **Note**: If you are dealing with floats or integers you can add a tolerance to the comparisons in the form of a fraction (0.1 = 10% tolerance) as shown in the previous example.

If the resulting boolean value is `True` the check passes, otherwise it fails. [Airflow generates logs](https://www.astronomer.io/guides/logging/) that show the set of returned records for every check that passes and the full query and result for checks that failed.

The screenshot below shows the output of 3 successful checks that ran on the `DATE` column of a table in Snowflake using `SQLColumnCheckOperator`. The checks concerned the minimum value, the maximum value, and the amount of null values in the column.

The logged line `INFO - Record: (datetime.date(2021, 4, 9), datetime.date(2022, 7, 17), 0)` lists the results of the query: the minimum date was 2021-09-04, the maximum date 2022-07-17 and there were zero null values, which satisfied the conditions of the check.

```text
[2022-07-18, 10:54:58 UTC] {cursor.py:710} INFO - query: [SELECT MIN(DATE) AS DATE_min,MAX(DATE) AS DATE_max,SUM(CASE WHEN DATE IS NULL TH...]
[2022-07-18, 10:54:58 UTC] {cursor.py:734} INFO - query: execution my_column_addition_check
[2022-07-18, 10:54:58 UTC] {connection.py:507} INFO - closed
[2022-07-18, 10:54:59 UTC] {connection.py:510} INFO - No async queries seem to be running, deleting session
[2022-07-18, 10:54:59 UTC] {sql.py:124} INFO - Record: (datetime.date(2021, 4, 9), datetime.date(2022, 7, 17), 0)
```

All checks that fail will be listed at the end of the task log with their full SQL query and specific check that failed. The screenshot shows how the `TASK_DURATION` column failed the check. Instead of a minimum that is greater than or equal to 0, it had a minimum of -12.

```text
[2022-07-18, 17:05:19 UTC] {taskinstance.py:1889} ERROR - Task failed with exception
Traceback (most recent call last):
  File "/usr/local/python3.9/site-packages/airflow/providers/common/sql/operators/sql.py", line 126, in execute
    raise AirflowException(
airflow.exceptions.AirflowException: Test failed
Query:
SELECT MIN(TASK_DURATION) AS TASK_DURATION_min,MAX(TASK_DURATION) AS TASK_DURATION_max,SUM(CASE WHEN TASK_DURATION IS NULL THEN 1 ELSE 0 END) AS TASK_DURATION_null_check FROM DB.SCHEMA.TABLE;
Results:
(-12, 1000, 0)
The following tests have failed:
    Check: min,
    Check Values: {'geq_to': 0, 'result': -12, 'success': False}
```

## Example `SQLTableCheckOperator`

The `SQLTableCheckOperator` provides a way to check the validity of SQL statements containing aggregates over the whole table. There is no limit to the amount of columns these statements can involve or to their complexity. The statements are provided to the operator as a dictionary via the `checks` parameter.

The `SQLTableCheckOperator` is useful for:

- Checks that include aggregate values using the whole table (e.g. comparing the average of one column to the average of another using the SQL `AVG()` function).
- Row count checks.
- Schema checks.
- Comparisons between multiple columns, both aggregated and not aggregated.

> **Note**: You should put partially aggregated statements into their own operator, separate from the fully aggregated ones. See the next example for how to do this.

In the example below, three checks are defined: `my_row_count_check`, `my_column_sum_comparison_check` and  `my_column_addition_check` (the names can be freely chosen). The first check runs a SQL statement asserting that the table contains at least 1000 rows, the second check compares the sum of two columns and the third check confirms that for each row `MY_COL_1 + MY_COL_2 = MY_COL_3` is true.

```python
table_checks_aggregated = SQLTableCheckOperator(
    task_id="table_checks_aggregated",
    conn_id=example_conn,
    table=example_table,
    checks={
        "my_row_count_check": {
            "check_statement": "COUNT(*) >= 1000"
            },
        "my_column_sum_comparison_check": {
            "check_statement": "SUM(MY_COL_1) < SUM(MY_COL_2)"
            }
    }
)

table_checks_not_aggregated = SQLTableCheckOperator(
    task_id="table_checks_not_aggregated",
    conn_id=example_conn,
    table=example_table,
    checks={
        "my_column_addition_check": {
            "check_statement": "MY_COL_1 + MY_COL_2 = MY_COL_3"
            }
    }
)
```

Under the hood, the operator performs a `CASE WHEN` statement on each of the checks, assigning `1` to the checks that passed and `0` to the checks that failed. Afterwards, the operator looks for the minimum of these results and marks the task as failed if the minimum is `0`. The `SQLTableCheckOperator` will produce observable logs like the ones shown above for the `SQLColumnCheckOperator`.

## Example `SQLCheckOperator`

The `SQLCheckOperator` returns a single row from a provided SQL query and checks to see if any of the returned values in that row are `False`. If any values are `False`, the task fails. This operator allows a great deal of flexibility in checking:

- A specific, single column value.
- Part of or an entire row compared to a known set of values.
- Options for categorical variables and data types.
- The results of any other function that can be written as a SQL query.

The following code snippet shows you how to use the operator in a DAG:

```python
yellow_tripdata_row_quality_check = SQLCheckOperator(
    conn_id=example_conn,
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
  CASE
    WHEN dropoff_datetime > pickup_datetime THEN 1
    ELSE 0
  END AS date_check,
  CASE
    WHEN passenger_count >= 0
    THEN 1 ELSE 0
  END AS passenger_count_check,
  CASE
    WHEN trip_distance >= 0 AND trip_distance <= 100
    THEN 1 ELSE 0
  END AS trip_distance_check,
  CASE
    WHEN ROUND((fare_amount + extra + mta_tax + tip_amount + \
      improvement_surcharge + COALESCE(congestion_surcharge, 0)), 1) = \
      ROUND(total_amount, 1) THEN 1
    WHEN ROUND(fare_amount + extra + mta_tax + tip_amount + \
      improvement_surcharge, 1) = ROUND(total_amount, 1) THEN 1
    ELSE 0
  END AS fare_check
FROM yellow_tripdata
WHERE pickup_datetime IN (SELECT pickup_datetime
                          FROM yellow_tripdata
                          ORDER BY RANDOM()
                          LIMIT 1)
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

## Conclusion

After reading this guide, you should feel comfortable using the SQL Check operators, understanding how each one works, and getting a sense of when each one would be useful in practice. With these operators you have the foundation for a robust data quality suite right in your pipelines. If you are looking for more examples, or want to see how to use backend-specific operators like Redshift, BigQuery, or Snowflake, check out Astronomer's [data quality demo repository](https://github.com/astronomer/airflow-data-quality-demo/).
