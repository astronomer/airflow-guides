---
title: "Data quality and Airflow"
description: "Improve the quality of your data using Airflow"
date: 2022-07-12T00:00:00.000Z
slug: "data-quality"
heroImagePath: null
tags: ["SQL", "Great Expectations", "Data quality"]
---

## Overview

Ensuring the quality of your data is a prerequisite to getting actionable insights from your data pipelines. Airflow offers a variety of possibilities to orchestrate data quality checks from directly within your DAGs.

In this guide, we will cover:

- Best practices and essential knowledge surrounding the planning of a data quality approach.
- When to implement data quality checks.
- How to choose a data quality check tool.
- How data lineage is connected to data quality.
- An in depth look at two commonly used data quality check tools: SQL Check operators and Great Expectations.
- An example comparing implementation of data quality checks using each of these tools.

## Assumed Knowledge

To get the most out of this guide, you should have knowledge of:

- What Airflow is and when to use it. See [Introduction to Apache Airflow](https://www.astronomer.io/guides/intro-to-airflow).
- Airflow operators. See [Operators 101](https://www.astronomer.io/guides/what-is-an-operator).
- Airflow connections. See [Managing your Connections in Apache Airflow](https://www.astronomer.io/guides/connections/).
- Relational databases. See [Relational database on Wikipedia](https://en.wikipedia.org/wiki/Relational_database).

## Data quality essentials

What is considered "good" in terms of data quality is very use case dependent. Defining quality criteria for a given collection of datasets is often a task requiring collaboration with all data professionals involved with any part of the pipeline.

While this process is highly individual, it can be divided into general steps:

1. Assess where and in what formats relevant data is stored and where it moves along your pipeline (this step can be assisted by using a data lineage tool).
2. Gather the data quality needs of data professionals using the data directly and indirectly.
3. Determine what quality checks should be run on which level of the data.
4. Determine where those quality checks should occur in your pipeline.
5. Define the process a check failure should trigger.
6. Choose a data quality tool (see 'Tools').
7. Write the checks.
8. Test the checks.

### Types of data quality checks

Data quality checks can be run on different levels:

- **Column**: e.g. confirming uniqueness of a key column, restricting the amount of `NULL` values that are allowed, define logical bounds for numeric or date columns, or defining valid options for categorical variables.
- **Row**: e.g. comparing the values in several columns for each row or ensuring that there are no mutually exclusive values present in the same row.
- **Table**: e.g. checking against a template schema to verify that it has not changed or checking that a table has a minimum row count.
- **Over several tables**: e.g. data parity checks across several tables or creating logical checks like making sure a customer marked as 'inactive' has no purchases listed in any of the other tables.

It is also important to distinguish the two types of Data Integrity Control:

- **Flow Control**: Monitors incoming data on a record-by-record basis and will sometimes prevent single records that fail certain data quality checks from entering the database. We will not cover flow control in this guide.
- **Static Control**: Runs checks on Spark or Pandas dataframes, or on existing tables in a database. These checks can be performed anywhere in a typical ETL pipeline and might halt the pipeline in case of a failed check to prevent further processing of data with quality issues. In this guide we will only cover static data quality checks.

### Location and downstream effects of data quality checks

Data quality checks can be run at different times within a data pipeline or Airflow environment. It often makes sense to test them in their own DAG and later incorporate them into your ETL pipelines to be able to make downstream behavior dependent on the outcome of selected data quality checks.

Within the ETL pipeline, data quality checks can be placed in several different locations as shown in the DAG graph below:

- Before the transform step (`data_quality_check_1`)
- After the transform step (`data_quality_check_2`)
- Branching off from a step (`data_quality_check_3`)

![Different locations for data quality checks in an ETL pipeline](https://assets2.astronomer.io/main/guides/data-quality/dq_checks_locations_example_graph.png)

It is common practice to define further downstream actions depending on the results of data quality checks (`post_check_action_1` and `post_check_action_2`), or in [`callbacks`](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/callbacks.html).
These actions often include alerting data professionals via [error notifications](https://www.astronomer.io/guides/error-notifications-in-airflow/), for example with an email or in a Slack channel.

When implementing data quality checks, consider how a check success or failure should influence downstream dependencies. [Trigger Rules](https://www.astronomer.io/guides/managing-dependencies/#trigger-rules) are especially useful in managing operator dependencies.

## When to implement data quality checks

When implementing data quality checks, it is important to consider the tradeoffs between the upfront work of implementing checks vs. the cost of downstream issues caused by data with bad quality.

Good reasons to start thinking about data quality checks are:

- Downstream models serve customer-facing results that could be compromised in the case of a data quality issue.
- There are data quality concerns where an issue might not be immediately obvious to the data professional using the data.

## Tools

There are multiple open source tools that can be used to check data quality from an Airflow DAG. While we list the most commonly used tools here, we will focus on the two tools that also integrate with OpenLineage:

- **[SQL Check operators](https://www.astronomer.io/guides/airflow-sql-data-quality-tutorial)**: A group of operators allowing the user to define data quality checks in Python dictionaries and SQL directly from within the DAG.
- **[Great Expectations](https://greatexpectations.io/)**: An open source data validation framework where checks are defined in JSON format. Airflow offers a provider package including the `GreatExpectationsOperator` for easy integration.

Other tools that can be used for data quality checks include:

- **[Soda](https://docs.soda.io/)**: An open source data validation framework that uses YAML to define checks which can be run in Airflow using the `BashOperator`. Soda also offers the ability to write any custom checks using SQL.
- **[dbt test](https://docs.getdbt.com/docs/building-a-dbt-project/tests)**: dbt supports a testing framework on models using the `dbt test` CLI command, which can be run in Airflow with the `BashOperator` or `PythonOperator`.

### Choosing a tool

Which tool to choose comes down to individual business needs and preferences. We recommend using SQL Check operators if you want to:

- Write checks without needing to set up software additionally to Airflow.
- Write checks as Python dictionaries and in SQL.
- Be able to use any SQL statement that returns a single row of booleans as a data quality check.
- Implement many different downstream dependencies depending on the outcome of different checks.
- Be able to have full observability of which checks failed from within Airflow task logs, including the full SQL statements of failed checks.

We recommend using a data validation framework like Great Expectations or Soda if:

- You want to collect the results of your data quality checks in a central place.
- You prefer to write checks in JSON (Great Expectations) or YAML (Soda) format.
- Most or all of your checks can be implemented by the predefined checks of the solution of your choice.
- You want your data quality checks abstracted away from the DAG code.

> **Note**: Currently only SQL Check operators and Great Expectations offer data lineage extraction.

### SQL Check operators

> **Note**: You can find more details and examples on SQL Check operators as well as example logs in the ['Airflow Data Quality Checks with SQL Operators' guide](https://www.astronomer.io/guides/airflow-sql-data-quality-tutorial/).

SQL Check operators execute a SQL statement that results in a set of booleans. A result of `True` leads to the check passing and the task being labelled as successful. A result of `False`, or any error when the statement is executed, leads to a failure of the task. Before using any of the operators, you need to define the [connection](https://www.astronomer.io/guides/connections/) to your data storage from the Airflow UI or via an external secrets manager.

The SQL Check operators work with any backend solution that accepts SQL queries and supports Airflow, and differ in what kind of data quality checks they can perform and how they are defined.

The `SQLColumnCheckOperator` and `SQLTableCheckOperator` are part of the [Common SQL provider](https://registry.astronomer.io/providers/common-sql). The other SQL Check operators are built into core Airflow and do not require separate package installation.

- [`SQLColumnCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqlcolumncheckoperator): Allows quick definition of many checks on whole columns of a table using a Python dictionary.
- [`SQLTableCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqltablecheckoperator): Can run aggregated and non-aggregated statements involving several columns of a table.
- [`SQLCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlcheckoperator): Can be used with any SQL statement that returns a single row of booleans.
- [`SQLIntervalCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlintervalcheckoperator): Runs checks against historical data.
- [`SQLValueCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlvaluecheckoperator): Compares the result of a SQL query against a value with or without a tolerance window.
- [`SQLThresholdCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlthresholdcheckoperator): Compares the result of a SQL query against upper and lower thresholds which may also be described as SQL queries.

The logs from SQL Check operators can be found in the regular Airflow task logs.

### Great Expectations

> **Note**: You can find more information on how to use Great Expectations with Airflow in the ['Integrating Airflow and Great Expectations'](https://www.astronomer.io/guides/airflow-great-expectations/) guide.

Great Expectations is an open source data validation framework that allows the user to define data quality checks called Expectation Suites as a JSON file. The checks can be run in a DAG using the [`GreatExpectationsOperator`](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsoperator).

> **Note** All currently available expectations can be viewed on the [Great Expectations website](https://greatexpectations.io/expectations).

To use Great Expectations, you will need to install the open source Great Expectations package and set up a Great Expectations project with at least one instance of each of the following components:

- Data Context
- Datasource
- Expectation Suite
- Checkpoint

The Great Expectations documentation offers a [step-by-step tutorial](https://docs.greatexpectations.io/docs/tutorials/getting_started/tutorial_overview) for this setup. Additionally, to use Great Expectations with Airflow, the [Great Expectations provider package](https://registry.astronomer.io/providers/great-expectations) has to be installed.

When using Great Expectations, Airflow task logs will only show whether the suite passed or failed. To get a detailed report on the checks that were run and their results, you can refer to the html files in `great_expecations/uncommitted/data_docs/local_site/validations`.

## Data lineage and data quality

In complex data ecosystems, lineage can be a powerful addition to data quality checks, especially for investigating what data from which origins caused a check to fail.

> **Note**: For more information on data lineage and details on how to set up OpenLineage with Airflow please see the ['OpenLineage and Airflow' guide](https://www.astronomer.io/guides/airflow-openlineage/).

Both SQL Check operators and the `GreatExpectationsOperator` have OpenLineage extractors. If you are working with open source tools, you can view the resulting lineage from the extractors using Marquez.

The output from the `SQLColumnCheckOperator` will contain each individual check and whether or not it succeeded:

![Marquez SQLColumnCheckOperator](https://assets2.astronomer.io/main/guides/data-quality/marquez_sql_column_check.png)

For the `GreatExpectationsOperator`, OpenLineage receives whether or not the whole Expectation suite succeeded or failed:

![Marquez GreatExpectationsOperator](https://assets2.astronomer.io/main/guides/data-quality/marquez_ge.png)

## Example: Comparing SQL Check operators and Great Expectations

This example shows the steps necessary to perform the same set of data quality checks with SQL Check operators and with Great Expectations.

The checks performed for both tools are:

- "MY_DATE_COL" has only unique values
- "MY_DATE_COL" has only values between 2017-01-01 and 2022-01-01
- "MY_TEXT_COL" has no null values
- "MY_TEXT_COL" has at least 10 distinct values
- "MY_NUM_COL" has a minimum value between 90 and 110
- `example_table` has at least 1000 rows
- The the value in each row of "MY_COL_1" plus the value of the same row in "MY_COL_2" is equal to 100
- "MY_COL_3" contains only the values `val1`, `val2`, `val3` and `val4`

### Example: SQL Check operators

The example DAG below consists of 3 tasks:

- First, the `SQLColumnCheckOperator` is used to perform checks on several columns in the target table.
- Next, two `SQLTableCheckOperator`s perform one check each that involves several columns or the whole table respectively.
- Finally, the `SQLCheckOperator` is used to make sure a categorical variable is set to one of 4 options.

While this example shows all the checks being written within the Python file defining the DAG, it is possible to modularize commonly used checks and SQL statements in separate files (for Astro CLI users, those files can be put into the `/include` directory).

```python
from airflow import DAG
from datetime import datetime

from airflow.operators.sql import SQLCheckOperator
from airflow.providers.common.sql.operators.sql import (
  SQLColumnCheckOperator, SQLTableCheckOperator
)  

with DAG(
    dag_id="example_dag_sql_check_operators",
    schedule_interval='@daily',
    start_date=datetime(2022, 7, 15),
    catchup=False,
    doc_md="""
    Example DAG for SQL Check operators.
    """,
    default_args={
      "conn_id": example_connection
    }
) as dag:

    # SQLColumnCheckOperator example: runs checks on 3 columns:
    #   - MY_DATE_COL is checked to only contain unique values ("unique_check")
    #     and to have dates greater than 2017-01-01 and lesser than 2022-01-01.
    #   - MY_TEXT_COL is checked to contain no NULL values
    #     and at least 10 distinct values
    #   - MY_NUM_COL is checked to have a minimum value between 90 and 110
    column_checks = SQLColumnCheckOperator(
        task_id="column_checks",
        table=example_table,
        column_mapping={
            "MY_DATE_COL": {
                "min": {"greater_than": datetime.date(2017, 1, 1)},
                "max": {"less_than": datetime.date(2022, 1, 1)},
                "unique_check": {"equal_to": 0}
            },
            "MY_TEXT_COL": {
                "distinct_check": {"geq_to": 10},
                "null_check": {"equal_to": 0}
            },
            "MY_NUM_COL": {
                "max": {"equal_to": 100, "tolerance": 0.1}
            },
        }
    )

    # SQLTableCheckOperator example: This operator performs one check:
    #   - a row count check, making sure the table has >= 1000 rows
    table_checks_aggregated = SQLTableCheckOperator(
        task_id="table_checks_aggregated",
        table=example_table,
        checks={
            "my_row_count_check": {
                "check_statement": "COUNT(*) >= 1000"
            }
        }
    )

    # SQLTableCheckOperator example: This operator performs one check:
    #   - a columns comparison check to see that the value in MY_COL_1 plus
    #   the value in MY_COL_2 is 100
    table_checks_not_aggregated = SQLTableCheckOperator(
        task_id="table_checks_not_aggregated",
        table=example_table,
        checks={
            "my_column_comparison_check": {
                "check_statement": "MY_COL_1 + MY_COL_2 = 100"
            }
        }
    )

    # SQLCheckOperator example: ensure categorical values in MY_COL_3
    # are one of a list of 4 options
    check_val_in_list = SQLCheckOperator(
        task_id="check_today_val_in_bounds",
        conn_id=example_connection,
        sql="""
                WITH

                not_in_list AS (

                SELECT COUNT(*) as count_not_in_list
                FROM {{ params.db_to_query }}.{{ params.schema }}.\
                     {{ params.table }}
                WHERE {{ params.col }} NOT IN {{ params.options_tuple }}
                )

                SELECT
                    CASE WHEN count_not_in_list = 0 THEN 1
                    ELSE 0
                    END AS testresult
                FROM not_in_list
            """,
        params={"db_to_query": example_database,
                "schema": example_schema,
                "table": example_table,
                "col": "MY_COL_3",
                "options_tuple": "('val1', 'val2', 'val3', 'val4')"
                }
    )
```

### Example: Great Expectations

The following example runs the same data quality checks as the SQL Check operators example against the same database. After setting up the Great Expectations instance with all four components, the checks can be defined in JSON format to form one Expectation Suite.

> **Note**: For each of the checks in this example, an `Expectation` already exists. This is not always the case, and for more complicated checks you may need to define a [custom expectation](https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/overview).


```json
{
  "data_asset_type": null,
  "expectation_suite_name": "my_suite",
  "expectations": [
      {
      "expectation_context": {
        "description": "MY_DATE_COL has values between 2017-01-01 - 2022-01-01"
      },
      "expectation_type": "expect_column_values_to_be_between",
      "ge_cloud_id": null,
      "kwargs": {
        "column": "MY_DATE_COL",
        "max_value": "2022-01-01",
        "min_value": "2017-01-01"
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "MY_DATE_COL's values are all unique"
      },
      "expectation_type": "expect_column_values_to_be_unique",
      "ge_cloud_id": null,
      "kwargs": {
        "column": "MY_DATE_COL"
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "MY_TEXT_COL has at least 10 distinct values"
      },
      "expectation_type": "expect_column_unique_value_count_to_be_between",
      "ge_cloud_id": null,
      "kwargs": {
        "column": "MY_TEXT_COL",
        "min_value": 10
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "MY_TEXT_COL has no NULL values"
      },
      "expectation_type": "expect_column_values_to_not_be_null",
      "ge_cloud_id": null,
      "kwargs": {
        "column": "MY_TEXT_COL"
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "MY_NUM_COL has a maximum val between 90 and 110"
      },
      "expectation_type": "expect_column_max_to_be_between",
      "ge_cloud_id": null,
      "kwargs": {
        "column": "MY_NUM_COL",
        "min_value": 90,
        "max_value": 110
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "the table has at least 1000 rows"
      },
      "expectation_type": "expect_table_row_count_to_be_between",
      "ge_cloud_id": null,
      "kwargs": {
        "min_value": 1000
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "for each row MY_COL_1 plus MY_COL_2 is = 100"
      },
      "expectation_type": "expect_multicolumn_sum_to_equal",
      "ge_cloud_id": null,
      "kwargs": {
        "column_list": ["MY_COL_1", "MY_COL_2"],
        "sum_total": 100
      },
      "meta": {}
    },
    {
      "expectation_context": {
        "description": "MY_COL_3 only contains values from a defined set"
      },
      "expectation_type": "expect_column_values_to_be_in_set",
      "ge_cloud_id": null,
      "kwargs": {
        "column": "MY_COL_3",
        "value_set": ["val1", "val2", "val3", "val4"]
      },
      "meta": {}
    }
  ],
  "ge_cloud_id": null,
  "meta": {
    "great_expectations_version": "0.15.14"
  }
}
```

The corresponding DAG code shows how all checks are run within one task using the `GreatExpectationsOperator`. Only the root directory of the data context and the checkpoint name have to be provided. It is important to note that to use XComs with the `GreatExpectationsOperator` it is necessary to enable XCOM pickling as described in the more in-depth [Great Expectations](https://www.astronomer.io/guides/airflow-great-expectations/) guide.

```python
from airflow import DAG
from datetime import datetime

from great_expectations_provider.operators.great_expectations import (
  GreatExpectationsOperator
)

with DAG(
    schedule_interval=None,
    start_date=datetime(2022,7,1),
    dag_id="ge_example_dag",
    catchup=False,
) as dag:

    # task running the Expectation Suite defined in the JSON above
    ge_test = GreatExpectationsOperator(
        task_id="ge_test",
        data_context_root_dir="/usr/local/airflow/include/great_expectations",
        checkpoint_name="my_checkpoint",
        do_xcom_push=False
    )
```

## Conclusion

The growth of tools designed to perform data quality checks reflect the importance of ensuring data quality in production workflows. Commitment to data quality requires in-depth planning and collaboration between data professionals. What kind of data quality your organization needs will depend on your unique use case, which you can explore using the steps outlined in this guide.

SQL Check operators offer a way to define your checks directly from within the DAG, with no other tools necessary. If you run many checks on different databases, you may benefit from using a more complex testing solution like Great Expectations or Soda.

No matter which tool is used, data quality checks can be orchestrated from within an Airflow DAG, which makes downstream actions depending on the outcome of the checks possible.
