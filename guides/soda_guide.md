---
title: "Soda and Airflow"
description: "Use Soda Core for data quality checks with Airflow"
date: 2022-08-02T00:00:00.000Z
slug: "data-quality"
heroImagePath: null
tags: ["Soda", "Data Quality"]
---

## Overview

Soda Core is an open source framework for data quality checks using the SodaCL command-line interface to run checks defined in a YAML file.

Reasons to use Soda Core are:

- Very flexible in how you can define your checks using predefined metrics or full SQL statements.
- [Offers check configurations](https://docs.soda.io/soda-cl/optional-config.html) that can add a warn state for a check. For example having values > 10 in a column might warrant a warning, while a value over 100 in the same column leads the check to fail.

## Requirements

To use Soda Core, the Soda Core package for the database backend needs to be installed and configured. The [Soda documentation provides a list of supported databases](https://docs.soda.io/soda-core/configuration.html) and how to configure them.

For the DAG code no additional providers or packages need to be installed since the BashOperator is part of the Airflow core.

## Example

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
