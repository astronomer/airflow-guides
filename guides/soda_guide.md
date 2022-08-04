---
title: "Soda Core and Airflow"
description: "Use Soda Core for data quality checks with Airflow"
date: 2022-08-02T00:00:00.000Z
slug: "data-quality"
heroImagePath: null
tags: ["Soda", "Data Quality"]
---

[Soda Core](https://www.soda.io/core) is an open source framework for data quality checks using the SodaCL interface to run checks defined in a YAML file.

Reasons to use Soda Core are:

- Lets you define checks as YAML configuration with many predefined metrics available.
- If there is no metric available for your use case you can provide any SQL query within the YAML file and check against its returned value.
- Easy to set up a large amount of data quality checks.
- Integrates with commonly used data engineering tools such as Airflow, Apache Spark, PostgreSQL, Snowflake [and more](https://www.soda.io/integrations).

> **Note**: For a general overview on how to approach data quality and of different tools available to run data quality checks using Airflow see the 'Data Quality and Airflow' guide.

## Assumed Knowledge

To get the most out of this guide, users should have knowledge of:

- How to design a data quality approach
- What Airflow is and when to use it
- Airflow Operators
- Relational Databases
- Basic familiarity with writing YAML configurations

The following resources are recommended:

- Data Quality and Airflow
- [Introduction to Apache Airflow](Introduction to Apache Airflow)
- [Operators 101](Operators 101)
- [Relational database on Wikipedia](https://en.wikipedia.org/wiki/Relational_database)
- [The Official YAML Web Site](https://yaml.org/)

## Requirements

To use Soda Core, the Soda Core package for the database backend needs to be installed and configured. The [Soda documentation provides a list of supported databases](https://docs.soda.io/soda-core/configuration.html) and how to configure them.

For the DAG code no additional providers or packages need to be installed since the BashOperator is part of the Airflow core.

## Example: Run Soda Core checks on a Snowflake database

This example shows one possible way to set up data quality checks on a Snowflake database using Soda Core.

The setup can be divided into the following steps:

- Create a configuration file that connects to the Snowflake database: `configuration.yml`.
- Create a checks file containing the data quality checks: `checks.yml`.
- Install the `soda-core-snowflake` package in your Airflow environment.
- Create the DAG code running the `soca scan` command using the `BashOperator`.


### Step 1: Create the configuration file

The configuration file needed to connect to Snowflake can be created from the template in the Soda documentation as shown below.

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

### Step 2: Create the checks file

You can define your data quality checks using the [many checks available for Soda CL](https://docs.soda.io/soda-cl/soda-cl-overview.html). If you cannot find a predefined metric or check that works for your use case you can create a user-defined check using SQL as shown below.

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

> **Note**: You need to make both YAML files available to your Airflow environment. Users of the Astro CLI can simply put them into the `/include` folder.

### Step 3: Install the Soda Core package

The `soda-core-snowflake` package needs to be installed in your Airflow environment. Astro CLI users can add the following line to the `requirements.txt` file:

```text
soda-core-snowflake
```

### Step 4: Run soda scan using the BashOperator

The DAG code itself stays very simple with one task using the `BashOperator` to execute the `soda scan` command. Of course it is possible to incorporate data quality checks using Soda Core in different locations within your data pipeline.  

```python
from airflow import DAG
from datetime import datetime

from airflow.operators.bash import BashOperator

SODA_PATH="<filepath>" # can be specified as an env variable

with DAG(
    dag_id="soda_example_dag",
    schedule_interval='@daily',
    start_date=datetime(2022,8,1),
    catchup=False
) as dag:

    soda_test = BashOperator(
        task_id="soda_test",
        bash_command=f"soda scan -d MY_DATASOURCE -c \
            {SODA_PATH}/configuration.yml {SODA_PATH}/checks.yml"
    )

    soda_test
```

The logs from the Soda Core checks can be found in the Airflow task logs. They will list all checks that ran with their result.

Below an example of the logs in the case of 3 checks passing:

```text
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO - Scan summary:
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO - 3/3 checks PASSED:
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -     MY_TABLE in MY_DATASOURCE
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -       duplicate_count(MY_ID_COLUMN) = 0 [PASSED]
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -       missing_count(MY_ID_COLUMN) = 0 [PASSED]
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -       min(MY_NUM_COL) between 0 and 10 [PASSED]
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO - All is good. No failures. No warnings. No errors.
```

In case of failure of a check, the logs will show which check failed and what the `check_value` was that caused the failure. 

```text
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO - Scan summary:
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO - 2/3 checks PASSED:
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO -     MY_TABLE in MY_DATASOURCE
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO -       duplicate_count(MY_ID_COLUMN) = 0 [PASSED]
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO -       missing_count(MY_ID_COLUMN) = 0 [PASSED]
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO - 1/3 checks FAILED:
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO -     MY_TABLE in MY_DATASOURCE
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO -       max(MY_NUM_COL) between 10 and 20 [FAILED]
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO -         check_value: 3
[2022-08-04, 13:23:59 UTC] {subprocess.py:92} INFO - Oops! 1 failures. 0 warnings. 0 errors. 2 pass.
[2022-08-04, 13:24:00 UTC] {subprocess.py:96} INFO - Command exited with return code 2
[2022-08-04, 13:24:00 UTC] {taskinstance.py:1909} ERROR - Task failed with exception
Traceback (most recent call last):
  File "/usr/local/lib/python3.9/site-packages/airflow/operators/bash.py", line 194, in execute
    raise AirflowException(
airflow.exceptions.AirflowException: Bash command failed. The command returned a non-zero exit code 2.
```
