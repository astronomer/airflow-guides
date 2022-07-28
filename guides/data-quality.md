---
title: "Data Quality and Airflow"
description: "Improve the quality of your data using Airflow"
date: 2022-07-12T00:00:00.000Z
slug: "data-quality"
heroImagePath: null
tags: ["SQL", "GreatExpectations", "Data Quality"]
---

## Overview

Ensuring the quality of your data is a prerequisite to getting actionable insights from your data pipelines. Airflow offers a variety of possibilities to orchestrate data quality checks directly from within your DAG.

In this guide we will cover:

- Best practices surrounding data quality.
- When to implement data quality checks.
- Three different tools used for data quality checks with concrete examples: SQL Check operators, GreatExpectations and Soda.

> **Note**: In complex data ecosystems about Data Lineage can be a powerful addition to data quality checks, especially for investigating what data from which origins caused a check to fail. You can learn more about Data Lineage in the ['Open Lineage and Airflow' guide](https://www.astronomer.io/guides/airflow-openlineage/).

## Assumed Knowledge

To get the most out of this guide you should be familiar with basic Airflow concepts such as [operators](https://www.astronomer.io/guides/what-is-an-operator) and [connections](https://www.astronomer.io/guides/connections/). Since you will be running data quality checks against a relational database, general familiarity with the structure of a database and data types will be assumed.

> **Note**: If this is your first time using Airflow we recommend starting with the [Introduction to Apache Airflow](https://www.astronomer.io/guides/intro-to-airflow) guide.

## Data Quality Essentials

What is considered good in terms of data quality is very use case dependent. Defining quality criteria for a given collection of datasets is often a task requiring collaboration with all data professionals involved with any part of the pipeline.

While this process is highly individual it can be divided into general steps:

1. Assess where and in what formats relevant data is stored and where it moves along your pipeline (this step can be assisted by using a data lineage tool).
2. Gather the data quality needs of data professionals using the data directly and indirectly.
3. Determine what quality checks should be run on which level of the data.
4. Determine where those quality checks should occur in your pipeline.
5. Define the process a check failure should trigger.
6. Choose a data quality tool (see 'Tools').
7. Write the checks.
8. Test the checks.

### Data Storage and Data Formats

A multitude of data sources and data storage solutions exist. Key questions to consider are whether your data is relational or not, if the storage solution already imposes some constraints on the data (e.g. on data types by using a schema) and how you can query the data (e.g. different dialects of SQL).
Unstructured data might need additional processing steps until it is ready for data quality checks. For example you may want to collect non-relational data from an API in a table accessible by using SQL before running checks on it.

### Data Quality Needs and Types of Data Quality Checks

Data quality needs will differ between professionals using the data and can even be at odds sometimes, in which case you might consider creating additional tables for more constrained use cases.

Data quality checks can be run on different levels:

- **Column**: e.g. confirming uniqueness of a key column, restricting the amount of `NULL` values that are allowed, define logical bounds for numeric or date columns or defining valid options for categorical variables.
- **Row**: e.g. restricting the amount of `NULL` values that are allowed in a row, defining the number of rows expected to exist for a certain timeframe.
- **Table**: e.g. checking against a template schema to verify that it has not changed.
- **Over several tables**: e.g. creating logical checks like making sure a customer marked as 'inactive' has no purchases listed in any of the other tables.

> **Note**: When exploring data quality needs and designing checks good questions to ask data professionals are: "What changes in these datasets would need your attention downstream?", "What changes in the data would you want to be alerted about?", "What changes in the data would you want to hold the pipeline?".

### Location and Downstream Effects of Data Quality Checks

Data quality checks can be run in different locations. It often makes sense to test them in their own DAG and later incorporate them into your ETL pipelines.

Within the ETL pipeline data quality checks can be placed in several different locations, as shown in the DAG graph below:

- before the transforming step (`data_quality_check_1`)
- after the transforming step (`data_quality_check_2`)
- branching off from a step (`data_quality_check_3`)

![Different locations for data quality checks in an ETL pipeline](https://assets2.astronomer.io/main/guides/data-quality/dq_checks_locations_example_graph.png)

It is common practice to define further actions depending on data_quality checks in downstream tasks (`post_check_action_1` and `post_check_action_2`), or in [`Callbacks`](https://airflow.apache.org/docs/apache-airflow/stable/logging-monitoring/callbacks.html).
These actions often include alerting data professionals via [error notifications](https://www.astronomer.io/guides/error-notifications-in-airflow/) for example with an email or in a slack channel.

You should also consider how a check failing or passing should influence downstream dependencies, an Airflow feature especially useful in this case are [Trigger Rules](https://www.astronomer.io/guides/managing-dependencies/#trigger-rules).

## When to implement Data Quality Checks

When considering the implementation of data quality checks it is important to consider the tradeoffs between the upfront work of implementing checks vs. the cost of downstream issues caused by bad quality data.

Good reasons to start thinking about data quality checks are:

- downstream models serve customer-facing results that could be compromised in case of a data quality issue.
- there are data quality concerns where an issue might not be immediately obvious to the data professional using the data.

## Tools

There are different tools that can be used to check data quality from an Airflow DAG. In this section we will highlight three tools with concrete examples:

- **[SQL Check operators](https://www.astronomer.io/guides/airflow-sql-data-quality-tutorial)**: a group of operators allowing the user to define data quality checks in python dictionaries and SQL directly from within the DAG.
- **[GreatExpectations](https://greatexpectations.io/)**: an open source data validation framework where checks are defined in json format. Airflow offers a provider package for easy integration.
- **[Soda](https://docs.soda.io/)**: an open source data validation framework that uses YAML to define checks which can be kicked off using the `BashOperator`.

### SQL Check Operators

> **Note**: You can find more details and examples on SQL Check Operators as well as example logs in the ['Airflow Data Quality Checks with SQL Operators' guide](https://www.astronomer.io/guides/airflow-sql-data-quality-tutorial/).

SQL Check Operators execute a SQL statement that results in a boolean. `True` leads to the check passing and the task being labelled as successful. `False` or any error when the statement is executed causes the failure of the task. Before using the operator you need to define the [connection](https://www.astronomer.io/guides/connections/) to your data storage from the Airflow UI or via an external secrets manager.

The SQL Check Operators work with any backend solution that accepts SQL queries and differ in what kind of data quality checks they can perform and how they are defined:

- [`SQLColumnCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqlcolumncheckoperator): Allows quick definition of many checks on whole columns of a table using a python dictionary.
- [`SQLTableCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqltablecheckoperator): Can run aggregated and non-aggregated statements involving several columns of a table.
- [`SQLCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlcheckoperator): Can be used with any SQL statement that returns a single row of booleans.
- [`SQLIntervalCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlintervalcheckoperator): Runs checks against historical data.
- [`SQLValueCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlvaluecheckoperator): Compares the result of a SQL query against a value with or without a tolerance window.
- [`SQLThresholdCheckOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/sqlthresholdcheckoperator): Compares the result of a SQL query against upper and lower thresholds which may also be described as SQL queries.

Reasons to use SQL Check operators:

- Implementation like regular operators without the need to install additional software.
- Full observability directly in the Airflow task logs, including the full SQL statement that caused a task to fail.
- All checks are defined either in SQL or python dictionaries.
- Any SQL statement can be turned into a check as long as it returns a single row of booleans with the `SQLCheckOperator`.
- The `SQLColumnCheckOperator` offers the possibility to write common checks in a declarative way in a python dictionary without having to write SQL.

#### Requirements

To use SQL Check operators no additional software is needed. The `SQLColumnCheckOperator` and `SQLTableCheckOperator` are part of the [Common SQL provider](https://pypi.org/project/apache-airflow-providers-common-sql/1.0.0/), which can be installed with:

```bash
pip install apache-airflow-providers-common-sql
```

The other SQL check operators are built into core Airflow and do not require a separate package installation.

#### Example SQL Check operators

The example DAG below consists of 3 tasks:

- First the `SQLColumnCheckOperator` is used to perform checks on several columns in the target table.
- Afterwards the `SQLTableCheckOperator` performs two checks involving aggregate functions on the whole table.
- Lastly the `SQLCheckOperator` is used to make sure a categorical variable is set to one of 4 options.

Within these 3 tasks 8 individual data quality checks are performed:

- "MY_DATE_COL" only has unique values
- "MY_DATE_COL" only has values between 2017-01-01 and 2022-01-01
- "MY_TEXT_COL" has no null values
- "MY_TEXT_COL" has at least 10 distinct values
- "MY_NUM_COL" has a minimum value between 90 and 110
- `example_table` has at least 1000 rows
- The sum of all rows in "MY_COL_1" is less than the sum of all rows in "MY_COL_2"
- "MY_COL_3" only contains the values `val1`, `val2`, `val3` and `val4`

While this example shows all the checks being written within the python file defining the DAG, of course it is possible to modularize commonly used checks and SQL statements in separate files (for Astro CLI users, those files can be put into the `/include` directory).

```python
from airflow import DAG
from datetime import datetime

# import of operators
from airflow.operators.sql import SQLCheckOperator
from airflow.providers.common.sql.operators.sql import SQLColumnCheckOperator
from airflow.providers.common.sql.operators.sql import SQLTableCheckOperator

# defining the DAG
with DAG(
    dag_id="example_dag_sql_check_operators",
    schedule_interval='@daily',
    start_date=datetime(2022, 7, 15),
    catchup=False,
    doc_md="""
    Example DAG for SQL Check operators.
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
        conn_id=example_connection,
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

    # SQLTableCheckOperator example: This Operator performs two checks:
    #   - a row count check, making sure the table has >= 1000 rows
    #   - a columns sum comparison check to the sum of MY_COL_1 is below the
    #     sum of MY_COL_2
    table_checks = SQLTableCheckOperator(
        task_id="table_checks",
        conn_id=example_connection,
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

    # SQLCheckOperator example: ensure categorical values in MY_COL_3
    # are one of a list of 4 options
    check_today_val_in_bounds = SQLCheckOperator(
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

### GreatExpectations

> **Note**: You can find more information on how to use GreatExpectations with Airflow in the ['Integrating Airflow and Great Expectations' guide](https://www.astronomer.io/guides/airflow-great-expectations/).

GreatExpectations is an open source data validation framework that allows the user to define multiple lists of data quality checks called 'Expectations Suite's as a json file. The checks can be run from any position in the DAG using the [`GreatExpectationsOperator`](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsoperator).

Reasons to use GreatExpectations:

- If an expectation exists for your use case it is possible to implement it in a declarative way without needing to write any SQL.
- Useful when many checks are expected to fail to collect all results in a central place in an easily readable form.
- Abstracts data quality checks away from the DAG code.

> **Note** All currently available expectations can be discovered on the [GreatExpectations website](https://greatexpectations.io/expectations).

#### Requirements

To use GreatExpectations you will need to install the open source GreatExpectations software and set up a GreatExpectations project with at least one instance of each of the following components:

- Data Context
- Datasource
- Expectation Suite
- Checkpoint

The GreatExpectations documentation offers a [step-by-step tutorial](https://docs.greatexpectations.io/docs/tutorials/getting_started/tutorial_overview) for this setup.  

Additionally the GreatExpectations provider package has to be installed with:

```bash
pip install airflow-provider-great-expectations
```

#### Example GreatExpectations

The following example runs the same data quality checks as the SQL Check operators example against the same database, with one exception: there is currently no expectation that can compare the sum of two columns, for this a [custom expectation](https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/overview) would need to be defined.

The json file below shows a GreatExpectations Expectations Suite called `my_suite` containing 7 data quality checks:
- "MY_DATE_COL" only has unique values
- "MY_DATE_COL" only has values between 2017-01-01 and 2022-01-01
- "MY_TEXT_COL" has no null values
- "MY_TEXT_COL" has at least 10 distinct values
- "MY_NUM_COL" has a minimum value between 90 and 110
- `example_table` has at least 1000 rows
- "MY_COL_3" only contains the values `val1`, `val2`, `val3` and `val4`

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

The corresponding DAG code shows how all checks are run within one task using the `GreatExpectationsOperator`. Only the root directory of the data context and the checkpoint name have to be provided. It is important to note that to use XComs with the `GreatExpectationsOperator` it is necessary to enable XCom picking as described in the more in-depth [GreatExpectations guide](https://www.astronomer.io/guides/airflow-great-expectations/).

```python
from airflow import DAG
from datetime import datetime

from great_expectations_provider.operators.great_expectations import (
  GreatExpectationsOperator)

with DAG(
    schedule_interval=None,
    start_date=datetime(2022,7,1),
    dag_id="ge_example_dag",
    catchup=False,
) as dag:

    # task running the Expectation Suite defined in the json above
    ge_test = GreatExpectationsOperator(
        task_id="ge_test",
        data_context_root_dir="/usr/local/airflow/include/great_expectations",
        checkpoint_name="my_checkpoint",
        do_xcom_push = False
    )
```

When using GreatExpectations Airflow will only log whether the suite passed or failed, to get a detailed report on the checks that were run and their results you can refer to the html files in `great_expecations/uncommitted/data_docs/local_site/validations`, an screenshot of which is shown below:

![GreatExpectations Data Quality Report](https://assets2.astronomer.io/main/guides/data-quality/ge_html_example.png)

### Soda

Soda Core is an open source framework for data quality checks using the SodaCL command-line interface to run checks defined in a YAML file.

Reasons to use Soda Core are:

- Very flexible in how you can define your checks using predefined metrics or full SQL statements.
- [Offers check configurations](https://docs.soda.io/soda-cl/optional-config.html) that can add a warn state for a check. For example having values > 10 in a column might warrant a warning, while a value over 100 in the same column leads the check to fail.

#### Requirements

To use Soda Core, the Soda Core package for the database backend needs to be installed and configured. The [Soda documentation provides a list of supported databases](https://docs.soda.io/soda-core/configuration.html) and how to configure them.

For the DAG code no additional providers or packages need to be installed since the BashOperator is part of the Airflow core.

#### Example Soda

This example shows one possible way to set up data quality checks on a Snowflake database using Soda Core in a virtual python environment inside the Airflow environment.

The setup can be divided into the following steps:

- Create a configuration file that connects to the Snowflake database: `configuration.yml`
- Create a checks file containing the data quality checks: `checks.yml`
- Create a bash script that will run `soda scan` using the two files above: `my_soda_script.sh`
- Create the DAG code running the bash script using the `BashOperator`

The configuration file can be created from the template in the Soda documentation as shown below.

```YAML
# the first line names the datasource "MY_DATASOURCE"
data_source MY_DATASOURCE:
  type: snowflake
  connection:
    # provide your snowflake username and password in double quotes
    username: "MY_USERNAME"
    password: "MY_PASSWORD"
    # provide the account in the format xy12345.eu-central-1
    account: my_account
    database: MY_DATABASE
    warehouse: MY_WAREHOUSE
    # if your connection times out you may need to adjust the timeout value
    connection_timeout: 300
    role: MY_ROLE
    client_session_keep_alive:
    session_parameters:
      QUERY_TAG: soda-queries
      QUOTED_IDENTIFIERS_IGNORE_CASE: false
  schema: MY_SCHEMA
```

In the second step you can define your data quality checks using the [many checks available for Soda CL](https://docs.soda.io/soda-cl/soda-cl-overview.html). If you cannot find a predefined metric or check that works for your use case you can create a User-defined check using SQL as shown below.

```YAML
checks for example_table:
  # check that MY_DATE_COL has dates between 2017-01-01 and 2022-01-01 using regex
  - invalid_count(MY_DATE_COL) = 0:
      valid regex: (((20)?(1[7-9]|2[0-1]))[-](0?[0-9]|1[012])[-](0?[0-9]|[12][0-9]|3[01])|2022[-]01[-]01)
  # check that all entries in MY_DATE_COL are unique
  - duplicate_count(MY_DATE_COL) = 0
  # check that MY_TEXT_COL has no missing values
  - missing_count(MY_TEXT_COL) = 0
  # check that MY_TEXT_COL has at least 10 distinct values using SQL
  - distinct_vals >= 10:
      distinct_vals query: |
        SELECT DISTINCT(MY_TEXT_COL) FROM example_table
  # check that MY_NUM_COL has a minimum between 90 and 110
  - min(MY_NUM_COL) between 90 and 110
  # check that example table has at least 1000 rows
  - row_count >= 1000
  # check that the sum of MY_COL_2 is bigger than the sum of MY_COL_1
  - sum_difference > 0:
      sum_difference query: |
        SELECT SUM(MY_COL_2) - SUM(MY_COL_1) FROM example_table
  # checks that all entries in MY_COL_3 are part of a set or possible values
  - invalid_count(MY_COL_3) = 0:
      valid values: ['val1', 'val2', 'val3', 'val4']
```

After creation of the YAML files write a bash script that will be executed by the BashOperator in your Airflow environment. It is considered best practice to use Soda Core in a virtual environment.

The bash script below:

- creates a virtual environment
- provides it with the `checks.yml` and `configuration.yml` files
- enters the virtual environment
- installs the `soda-core-snowflake` package in the virtual environment
- runs the `soda scan` command on `MY_DATASOURCE` using the configuration files.

> **Note** It is important to make this script executable by running `chmod +x filepath/soda_script.sh` before providing it to your Airflow environment. For more information on using bash scripts with Airflow see the ['Running scripts using the BashOperator' guide](https://www.astronomer.io/guides/scripts-bash-operator/).

```bash
#!/bin/bash
python -m venv .venv
cp /usr/local/airflow/include/soda/checks.yml .venv/include
cp /usr/local/airflow/include/soda/configuration.yml .venv/include
source .venv/bin/activate
pip install --upgrade pip
pip install soda-core-snowflake
cd .venv/include
soda scan -d MY_DATASOURCE -c configuration.yml checks.yml
```

The DAG code itself stays very simple with one task using the `BashOperator` to execute the script.

```python
from airflow import DAG
from datetime import datetime
from airflow.operators.bash import BashOperator

with DAG(
    schedule_interval=None,
    start_date=datetime(2022,7,1),
    dag_id="soda_example_dag",
    catchup=False,
) as dag:

    soda_test = BashOperator(
        task_id="soda_test",
        # please not the space at the end of the command!
        bash_command="/usr/local/airflow/include/soda/soda_script.sh "
    )
```

The logs from the Soda Core checks can be found in the Airflow task logs.

### Other data quality check tools

Depending on your data stack you might be already using tools that offer some about of data quality checks. For example [dbt allows you to define assertions](https://docs.getdbt.com/docs/building-a-dbt-project/tests) about projects that can be run using a bash command and therefore of course can be kicked off from an Airflow DAG using the `BashOperator`.

## Conclusion

Data quality is important which is reflected in growth of tools designed to perform data quality checks. In-depth planning and collaborative exploration of what kind of data quality needs your organization is paramount in order to define checks to run and select the tools that are right for you. SQL Check operators offer a way to define your checks directly from within the DAG with no other tools necessary. If you run many checks on different databases you may profit from trialing a more complex testing solution like GreatExpectations or Soda.
