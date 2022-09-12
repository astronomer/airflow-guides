---
title: "Soda Core and Airflow"
description: "Using Soda Core to implement data quality checks in Airflow DAGs."
date: 2022-08-11T00:00:00.000Z
slug: "soda-data-quality"
heroImagePath: null
tags: ["Soda", "Data Quality"]
---

[Soda Core](https://www.soda.io/core) is an open source framework for checking data quality. It uses the Soda Checks Language (SodaCL) to run checks defined in a YAML file.

Soda Core lets you:

- Define checks as YAML configuration, including many preset checks.
- Provide a SQL query within the YAML file and check against a returned value if no preset checks fit your use case.
- Integrate data quality checks with commonly used data engineering tools such as Airflow, Apache Spark, PostgreSQL, Snowflake [and more](https://www.soda.io/integrations).

In this guide, we will cover key features of Soda Core and how to use it with Airflow.

> **Note**: For a general overview on how to approach data quality, and of different tools available to run data quality checks using Airflow, see the '[Data quality and Airflow](https://www.astronomer.io/guides/data-quality)' guide.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- How to design a data quality approach. See [Data quality and Airflow](https://www.astronomer.io/guides/data-quality).
- The basics of Soda Core. See [How Soda Core works](https://docs.soda.io/soda-core/how-core-works.html).
- How to use the BashOperator. See [Using the BashOperator](https://www.astronomer.io/guides/scripts-bash-operator/).
- Relational Databases. See [IBM's "Relational Databases Explained"](https://www.ibm.com/cloud/learn/relational-databases).
- Basic familiarity with writing YAML configurations. See [yaml.org](https://yaml.org/).

## Features of Soda Core

Soda Core uses Soda Checks Language (SodaCL) to run data quality checks defined in a YAML file. Soda Core is a powerful tool on its own, but integrating it into your data pipelines with Airflow means that you can use the outcome of data quality checks to influence downstream tasks.

In this section, we will highlight different types of checks you can implement with Soda Core. For a complete overview, see the [SodaCL documentation](https://docs.soda.io/soda-cl/soda-cl-overview.html).

Soda Core offers the ability to run checks on different properties of your dataset against a numerically defined threshold:

```YAML
checks for MY_TABLE_1:
  # MY_NUM_COL_1 has a minimum of above or equal 0
  - min(MY_NUM_COL_1) >= 0
  # MY_TEXT_COL has less than 10% missing values
  - missing_percent(MY_TEXT_COL) < 10
checks for MY_TABLE_2:
  # MY_NUM_COL_2 has an average between 100 and 1000
  - avg(MY_NUM_COL_2) is between 100 and 1000
  # MY_ID_COL has no duplicates
  - duplicate_count(MY_ID_COL) = 0
```

You can add optional configurations, such as custom names for checks and varying error levels:

```YAML
checks for MY_TABLE_1:
  # fail the check when MY_TABLE_1 has less than 10 or more than a million rows
  # warn if there are less than 100 (but 10 or more) rows
  - row_count:
      warn: when < 100
      fail:
        when < 10
        when > 1000000
      name: Wrong number of rows!
```

Data can be checked according to validity criteria using the following methods:

- List of valid values
- Predefined valid format
- Regex
- SQL query

```YAML
checks for MY_TABLE_1:
  # MY_CATEGORICAL_COL has no other values than val1, val2 and val3
  - invalid_count(MY_CATEGORICAL_COL) = 0:
      valid values: [val1, val2, val3]
  # MY_NUMERIC_COL has no other values than 0, 1 and 2.
  # Single quotes are necessary for valid values checks involving numeric
  # characters.
  - invalid_count(MY_NUMERIC_COL) = 0:
      valid values: ['0', '1', '2']
  # less than 10 missing valid IP addresses
  - missing_count(IP_ADDRESS_COL) < 10:
      valid format: ip address
  # WEBSITE_COL has less than 5% entries that don't contain "astronomer.io"
  - invalid_percent(WEBSITE_COL) < 5:
      valid regex: astronomer\.io
  # The average of 3 columns for values of category_1 is between 10 and 100
  - my_average_total_for_category_1 between 10 and 100:
      my_average_total_for_category_1 query: |
        SELECT AVG(MY_COL_1 + MY_COL_2 + MY_COL_3)
        FROM MY_TABLE_1
        WHERE MY_CATEGORY = 'category_1'
```

Three more unique features of Soda Core are:

- [Freshness checks](https://docs.soda.io/soda-cl/freshness.html): Set limits to the age of the youngest row in the table.
- [Schema checks](https://docs.soda.io/soda-cl/schema.html): Run checks on the existence of columns and validate data types.
- [Reference checks](https://docs.soda.io/soda-cl/reference.html): Ensure parity in between columns in different datasets in the same data source.

```YAML
checks for MY_TABLE_1:
  # MY_DATE's youngest row is younger 10 days
  - freshness(MY_DATE) < 10d
  # The schema has to have the MY_KEY column
  - schema:
      fail:
        when required column missing: [MY_KEY]
  # all names listed in MY_TABLE_1's MY_NAMES column have to also exist
  # in the MY_CUSTOMER_NAMES column in MY_TABLE_2
  - values in (MY_NAMES) must exist in MY_TABLE_2 (MY_CUSTOMER_NAMES)
```

## Requirements

To use Soda Core, you first need to install the Soda Core package for your database backend. The [Soda documentation provides a list of supported databases](https://docs.soda.io/soda-core/configuration.html) and how to configure them.

When using Soda Core with Airflow, the Soda Core package needs to be installed in your Airflow environment. Additionally, two YAML files need to be made available to the Airflow environment: `configuration.yml`, which contains the connection information for the database backend, and `checks.yml`, which contains the data quality checks.

If you use the Astro CLI, you can add `soda-core-<database>` to `requirements.txt` and your YAML files to `/include` in your Astro project.

## Example: Run Soda Core checks from Airflow

This example shows one possible way to run data quality checks on a Snowflake database using Soda Core from within Airflow.

The setup can be divided into the following steps:

- Create a configuration file that connects to the Snowflake database: `configuration.yml`.
- Create a checks file containing the data quality checks: `checks.yml`.
- Install the `soda-core-snowflake` package in your Airflow environment.
- Run the checks from a DAG by running the `soda scan` command using the BashOperator.

### Step 1: Create the configuration file

First we need to create a configuration file to connect to Snowflake. The easiest way to create the file is to use the template in the Soda documentation as shown below.

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

Save the YAML instructions above in a file called `configuration.yml` and make it available to your Airflow environment. If you use the Astro CLI, you can do this by placing the file into the `/include` directory of your Astro project.

### Step 2: Create the checks file

You can define your data quality checks using the [many preset checks available for SodaCL](https://docs.soda.io/soda-cl/soda-cl-overview.html). If you cannot find a preset check that works for your use case, you can create a custom one using SQL as shown below.

```YAML
checks for example_table:
  # check that MY_EMAIL_COL contains only email addresses according to the
  # format name@domain.extension
  - invalid_count(MY_EMAIL_COL) = 0:
      valid format: email
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
  # checks that all entries in MY_COL_3 are part of a set of possible values
  - invalid_count(MY_COL_3) = 0:
      valid values: [val1, val2, val3, val4]
```

Save the YAML instructions above in a file called `checks.yml` and make it available to your Airflow environment. If you use the Astro CLI, you can place this file in your `/include` directory.

### Step 3: Install the Soda Core package

The `soda-core-snowflake` package needs to be installed in your Airflow environment. If you use the Astro CLI, you can do this by adding the following line to the `requirements.txt` file:

```text
soda-core-snowflake
```

### Step 4: Run soda scan using the BashOperator

In a DAG, Soda Core checks are executed by using the BashOperator to run the `soda scan` command. The DAG below shows how to reference the configuration and checks YAML files in the command.

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
```

Because Soda Core runs through the BashOperator, you can run your checks in any part of your DAG and trigger tasks with your results like you would with other Airflow operators.

The logs from the Soda Core checks can be found in the Airflow task logs. The logs list all checks that ran and their results.

This is an example of what your logs might look like if all 3 checks pass:

```text
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO - Scan summary:
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO - 3/3 checks PASSED:
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -     MY_TABLE in MY_DATASOURCE
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -       duplicate_count(MY_ID_COLUMN) = 0 [PASSED]
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -       missing_count(MY_ID_COLUMN) = 0 [PASSED]
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO -       min(MY_NUM_COL) between 0 and 10 [PASSED]
[2022-08-04, 13:07:22 UTC] {subprocess.py:92} INFO - All is good. No failures. No warnings. No errors.
```

In the case of a check failure, the logs show which check failed and the `check_value` that caused the failure:

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
