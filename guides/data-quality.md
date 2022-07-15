---
title: "Data Quality and Airflow"
description: "Improve the quality of your data using Airflow"
date: 2022-07-12T00:00:00.000Z
slug: "data-quality"
heroImagePath: null
tags: ["SQL", "GreatExpectations", "Data Quality"]
---

## Overview

Ensuring the quality of your data is a prerequisite to getting actionable insights from your data pipelines. Airflow offers a variety of possibilities to orchestrate data quality checks directly from within your dag.

In this guide we will cover:

- Best practices surrounding data quality.
- When to implement data quality checks.
- Different tools used for data quality checks.
- The relationship between data quality and data lineage.

## Data Quality Essentials

What is considered good in terms of data quality is very use case dependent. Defining quality criteria for a given collection of datasets is often a task requiring collaboration with all data professionals involved with any part of the pipeline.

While this process is highly individual it can be divided into general steps:

1. Assess where and in what formats relevant data is stored and where it moves during your pipeline (this step can be assisted by using a data lineage tool).
2. Gather the data quality needs of data professionals using the data directly and indirectly.
3. Determine what quality checks should be run on which level of the data.
4. Determine where those quality checks should occur in your pipeline.
5. Define the process a check failure should trigger.
6. Choose a data quality tool (see 'Data Quality Checks Tools').
7. Write the checks.
8. Test the checks.

### Data Storage and Data Formats

A multitude of data sources and data storage solutions exist. Key questions to consider are whether your data is relational or not, if the storage solution already imposes some constraints on the data (e.g. on data types by using a schema) and how you can query the data (e.g. different dialects of SQL).
Unstructured data might need additional processing steps until it is ready for data quality checks. For example you may want to collect non-relational data from an API in a table accessible by using SQL before running checks on it.

### Data Quality needs and Types of Data Quality Checks

Data quality needs will differ between professionals using the data and can even be at odds sometimes, in which case you might consider creating additional tables for more constrained use cases.

Data quality checks can be run on different levels:

- **Column**: e.g. confirming uniqueness of a key column, restricting the amount of `NULL` values that are allowed, define logical bounds for numeric or date columns, defining valid options for categorical variables.
- **Row**: e.g. restricting the amount of `NULL` values that are allowed in a row, defining the number of rows expected to exist for a certain timeframe.
- **Table**: e.g. checking against a template schema to verify that it has not changed.
- **Over several tables**: e.g. creating logical checks like making sure a customer marked as 'inactive' has no purchases listed in any of the other tables.

> **Note**: When exploring data quality needs and designing checks good questions to ask data professionals are: "What changes in these datasets would need your attention downstream?", "What changes in the data would you want to be alerted about?", "What changes in the data would you want to hold the pipeline?".

### Location and Downstream Effects of Data Quality Checks

Data quality checks can be run in different locations. It often makes sense to test them in their own dag and later incorporate them into your ETL pipelines.

Within the ETL pipeline data quality checks can be placed in several different locations, as shown in the dag graph below:

- before the transforming step (`data_quality_check_1`)
- after the transforming step (`data_quality_check_2`)
- branching off from a step (`data_quality_check_3`)

![Different locations for data quality checks in an ETL pipeline](https://assets2.astronomer.io/main/guides/kubepod-operator/dq_checks_locations_example_graph.png)

It is common practice to define further actions depending on data_quality checks in downstream tasks (`post_check_action_1` and `post_check_action_2`), or in [`Callbacks`](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/callbacks.html).
These action often include alerting data professionals via [error notifications](https://www.astronomer.io/guides/error-notifications-in-airflow/) for example as an email or in a slack channel.

You should also consider how a check failing or passing should influence downstream dependencies, an Airflow feature especially useful in this case are [Trigger Rules](https://www.astronomer.io/guides/managing-dependencies/#trigger-rules).

## When to implement Data Quality Checks

When considering the implementation of data quality checks it is important to consider the tradeoffs between the upfront work of implementing checks vs. the cost of downstream issues caused by bad quality data.

Good reasons to start thinking about data quality checks are:

- downstream models serve customer-facing results that could be compromised in case of a data quality issue.
- there are data quality concerns where an issue might not be immediately obvious to the data professional using the data.

## Data Quality Checks Tools

Airflow offers different data quality check tools in the form of operators, the most commonly used ones are:

- SQLCheckOperators
- GreatExpectations
- dbtTest
- sodaSQL

The following sections will compare the same checks implemented with different tools.

### SQL Check Operators

> **Note**: You can find more details on the different SQL Check Operators in the ['Airflow Data Quality Checks with SQL Operators' guide](https://www.astronomer.io/guides/airflow-sql-data-quality-tutorial/).

SQL Check Operators execute a SQL statement that results in a boolean. `True` leads to the check passing and the task being labelled as successful. `False` or any error when the statement is executed causes the failure of the task. Before using the operator you need to define the [connection](https://www.astronomer.io/guides/connections/) to your data storage from the Airflow UI or via an external secrets manager.

There are currently 6 different SQL Check Operators available and they work with any backend solution that accepts SQL queries.

- SQLColumnCheckOperator: Allows quick definition of many checks on whole columns of a table using a dictionary based syntax.
- SQLTableCheckOperator: Can run statements involving several columns of a table.
- SQLCheckOperator: Can be used with any SQL statement that returns a boolean. This makes this the most customizeable SQLCheckOperator.
- SQLValueCheckOperator: Checks the values of a column against an exact value or percentage threshold.
- SQLIntervalCheckOperator: To check current against historical data.
- SQLThresholdOperator: Allows to define upper and lower thresholds

> **Note**: The SQLColumnCheckOperator and the SQLTableCheckOperator are currently available in a [release candidate](https://pypi.org/project/apache-airflow-providers-common-sql/1.0.0rc1/).

The example dag below consists of 3 tasks:

- First the SQLColumnCheckOperator is used to perform checks on several columns in the target table.
- Afterwards the SQLTableCheckOperator performs two checks involving aggregate functions on the whole table.
- Lastly the versatile SQLCheckOperator is used to make sure a categorical variable is set to one of 4 options.


```python
from airflow import DAG
from datetime import datetime

# import of operators
from airflow.operators.sql import SQLCheckOperator
from airflow.providers.common.sql.operators.sql import SQLColumnCheckOperator
from airflow.providers.common.sql.operators.sql import SQLTableCheckOperator

# defining the dag
with DAG(
    dag_id="example_dag_sql_check_operators",
    schedule_interval='@daily',
    start_date=datetime(2022, 7, 15),
    catchup=False,
    doc_md="""
    Example dag for SQL Check Operators.
    """
) as dag:

    # SQLColumnCheckOperator example: runs checks on 3 columns:
    #   - MY_DATE_COL is checked to only contain unique values ("unique_check")
    #     and to have dates greater than 2017-01-01 and lesser than 2022-01-01.
    #   - MY_TEXT_COL is checked to contain no NULL values
    #     and at least 10 distinct values
    #   - MY_NUM_COL is checked to have a minimum value between 90 and 110
    column_checks = SQLColumnCheckOperator(
        task_id="column_checks",
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

    # SQLTableCheckOperator example: This Operator performs two checks:
    #   - a row count check, making sure the table has >= 1000 rows
    #   - a columns sum comparison check to the sum of MY_COL_1 is below the
    #     sum of MY_COL_2
    table_checks = SQLTableCheckOperator(
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


    # SQLCheckOperator example: ensure categorical values in MY_COL_3
    # are one of a list of 4 options
    check_today_val_in_bounds = SQLCheckOperator(
        task_id="check_today_val_in_bounds",
        conn_id=<your database connection id>,
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
        params={"db_to_query": <your database>,
                "schema": <your schema>,
                "table": <your table name>,
                "col": "MY_COL_3",
                "options_tuple": """('<your option_1>', '<your option_2>',
                                     '<your option_3>', '<your option 4>')"""
                }
    )
```



### GreatExpectations

GreatExpectations is an open source data validation framework. It requires a few additional setup steps which are detailed in the ['Integrating Airflow and Great Expectations'](https://www.astronomer.io/guides/airflow-great-expectations/) guide.

Most of the data quality checks from the SQL Check Operators can be translated into expectations for a Expectations Suite file. The Check that the sum of COL_1 is below the sum of COL_2 would require writing a custom expectation.

The json file below shows a GreatExpectations Expectations Suite containing all but one of the same checks as shown above. In your dag you just have to instantiate a task with the GreatExpectationsOperator pointing to the checkpoint corresponding to the this collection of Expectations.

```json
  {
    "data_asset_type": null,
    "expectation_suite_name": "my_expectation_suite",
    "expectations": [
      {
        "expectation_context": {
          "description": """checking that MY_DATE_COL has values between
                            2017-01-01 and 2022-01-01"""
        },
        "expectation_type": "expect_column_values_to_be_between",
        "ge_cloud_id": null,
        "kwargs": {
          "max_value": "2022-01-01",
          "min_value": "2017-01-01"
        },
        "meta": {}
      },
      {
        "expectation_context": {
          "description": "checking that MY_DATE_COL's values are unique"
        },
        "expectation_type": "expect_column_values_to_be_unique",
        "ge_cloud_id": null,
        "kwargs": {
          "column": "MY_DATE_COL",
        },
        "meta": {}
      },
      {
        "expectation_context": {
          "description": """checking that MY_TEXT_COL has at least
                            10 distinct values"""
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
          "description": "checking that MY_TEXT_COL has no NULL values"
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
          "description": """checking that MY_NUM_COL has a maximum
                            between 90 and 110"""
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
          "description": "checking that the table at least 1000 rows"
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
          "description": "checking that "
        },
        "expectation_type": "expect_column_values_to_be_in_set",
        "ge_cloud_id": null,
        "kwargs": {
          "column": "MY_COL_3",
          "value_set": ["<your option_1>", "<your option_2>",
                        "<your option_3>", "<your option 4>"]
        },
        "meta": {}
      }
    ],
    "ge_cloud_id": null,
    "meta": {
      "great_expectations_version": "0.13.49"
    }
  }
```


### dbt test

> **Note** More information can be found in the ['Integrating Airflow and dbt'](https://www.astronomer.io/guides/airflow-dbt/) guide.

### sodaSQL

### Comparison
Compare runtimes (if you can see something significant) ? have a table?

## Data Quality and OpenLineage

(with link to OpenLineage Guide)
