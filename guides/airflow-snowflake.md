---
title: "Orchestrating Snowflake Queries with Airflow"
description: "How to use Airflow to get enhanced observability and compute savings while orchestrating your Snowflake jobs."
date: 2022-06-17T00:00:00.000Z
slug: "airflow-snowflake"
tags: ["Integrations", "ETL", "Database"]
---

## Overview

[Snowflake](https://www.snowflake.com/) is one of the most commonly used data warehouses, and features heavily in data engineering, data science, and data analytics workflows. As such, orchestrating Snowflake queries as part of a data pipeline is one of the most common use cases we see for Airflow. Using Airflow with Snowflake is straight forward, and there are multiple open source packages, tools, and integrations that can help you take your Snowflake query orchestration to the next level.

In this guide, we'll cover everything you need to know to make the most out of your "Airflow + Snowflake" experience, including:

- Using Snowflake providers, including what modules are out there and how to implement deferrable versions of common operators
- Leveraging the OpenLineage Airflow integration to get data lineage and enhanced observability from your Snowflake jobs
- Using the Astro SDK for the next generation of DAG authoring for Snowflake query tasks
- General best practices and considerations when interacting with Snowflake from Airflow

## Using Snowflake Providers

There are multiple open source packages with modules available to implement various Snowflake orchestration use cases in Airflow: 

- The [Snowflake provider package](https://registry.astronomer.io/providers/snowflake) contains hooks, operators, and transfer operators for Snowflake maintained by the Airflow community.
- The [Astronomer Providers](https://github.com/astronomer/astronomer-providers) package contains deferrable operators built and maintained by Astronomer, including a deferrable version of the `SnowflakeOperator`.
- The [Core SQL provider package](LINK) contains SQL check operators that can be used to perform data quality checks against data in Snowflake. 

To leverage all of the Snowflake modules available in Airflow, we recommend installing all three packages in your Airflow environment.

```bash
apache-airflow-providers-snowflake
apache-airflow-providers-core-sql
astronomer-providers[snowflake]
```

Modules for orchestrating basic queries and functions in Snowflake include:

- [`SnowflakeHook`](https://registry.astronomer.io/providers/snowflake/modules/snowflakehook): A hook abstracting the Snowflake API. Generally the hook would only be used by a DAG author when creating a custom operator or function. This hook is part of `apache-airflow-providers-snowflake`. 
- [`SnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator): Executes a SQL query in Snowflake. This operator is part of `apache-airflow-providers-snowflake`.
- [`S3ToSnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/s3tosnowflakeoperator): Executes a COPY command to transfer data from S3 into Snowflake.
- [`SnowflakeToSlackOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflaketoslackoperator): Executes a SQL query in Snowflake and sends the results to Slack.
- `SnowflakeOperatorAsync`: The deferrable version of the `SnowflakeOperator`, executes a SQL query in Snowflake.
- `SnowflakeHookAsync`: The deferrable version of the `SnowflakeHook`, abstracts the Snowflake API.

Modules for orchestrating **data quality checks** in Snowflake include:

- [`SQLColumnCheckOperator`](LINK): Performs a data quality check against columns of a given table. Using this operator with Snowflake requires a Snowflake connection ID, the name of the table to run checks on, and a `column_mapping` describing the relationship between columns and tests to run.
- [`SQLTableCheckOperator`](LINK): Performs a data quality check against a given table. Using this operator with Snowflake requires a Snowflake connection ID, the name of the table to run checks on, and a checks dictionary describing the relationship between the table and the tests to run.  

Note that the `apache-airflow-providers-snowflake` package also contains operators that can be used to run data quality checks in Snowflake, including the `SnowflakeCheckOperator`, `SnowflakeValueCheckOperator`, and `SnowflakeIntervalCheckOperator`. However, these operators are not as flexible as the operators in `apache-airflow-providers-core-sql` and will likely be deprecated in a future version of Airflow. We recommend using `apache-airflow-providers-core-sql` for the most up to date data quality check operators.

Below we show an example of how to use some of these modules in a DAG that implements a write, audit, publish pattern with data quality checks.

### Example Implementation

> **Note:** All of the code for this example can be found on the [Astronomer Registry](LINK). 

The exmaple DAG below implements a write, audit, publish pattern to showcase loading and data quality checking with Snowflake. The following steps are completed:

- Simultaneously create tables in Snowflake for the production data and the raw data that needs to be audited, using the `SnowflakeOperator`. Note that these tasks are not implemented with the deferrable version of the `SnowflakeOperator`, because `CREATE TABLE` statements typically run very quickly.
- Load data into the audit table using the `SnowflakeOperatorAsync`. This task *is* deferred to save on compute, because loading data can take some time if the dataset is large.
- Run data quality checks on the audit table to ensure that no erroneous data is moved to production. This Task Group includes column checks using the `SQLColumnCheckOperator` and table checks using the `SQLTableCheckOperator`. 
- Assuming the data quality checks passed, meaning those tasks were successful, copy data from the audit table into the production table using the `SnowflakeOperatorAsync`.
- Finally, delete the audit table since it only contained temporary data.

> **Note:** To make use of deferrable operators you must have a Triggerer running in your Airflow environment. For more on how to use deferrable operators, check out [this guide](https://www.astronomer.io/guides/deferrable-operators).

All of these tasks rely on SQL scripts that are stored in the `include/sql/` directory. 

The DAG looks like this:

```python
#add dag code here
```

GRAPH VIEW SCREENSHOT

Note that to run this DAG, you will need a connection to your Snowflake instance in your Airflow environment. This DAG uses a connection called `snowflake_default`. Your connection should be the `Snowflake` type, and should include the following information:

```yaml
Host: Your Snowflake Host, e.g. `account.region.snowflakecomputing.com`
Schema: Your Schema
Login: Your login
Password: Your password
Account: Your Snowflake account
Database: Your database
Region: Your account region
Role: Your role
Warehouse: Your warehouse
```

## Enhanced Observability with OpenLineage

The [OpenLineage project](https://openlineage.io/) maintains an integration with Airflow that allows users to obtain and view lineage data from their Airflow tasks. As long as an extractor exists for the operator being used, lineage data will be generated automatically from each task instance. For introductory information on how OpenLineage works with Airflow, check out [this guide](https://www.astronomer.io/guides/airflow-openlineage).

Users of the `SnowflakeOperator`, which does have an extractor, will be able to use lineage metadata to answer questions across DAGs such as:

- How does data stored in Snowflake flow through my DAGs? Are there any upstream dependencies?
- What downstream data does a task failure impact?
- Where did a change in data format originate?

At a high level, the OpenLineage - Airflow - Snowflake interaction works like this:

SCREENSHOT

Note that to view lineage data from your DAGs you need to have OpenLineage installed in your Airflow environment and a lineage front end running. For [Astro customers](https://docs.astronomer.io/astro/data-lineage), lineage is enabled automatically. For users working with open source tools, you can run Marquez locally and connect it to your Airflow environment following the instructions in [this guide](https://www.astronomer.io/guides/airflow-openlineage). 

To show an example of lineage resulting from Snowflake orchestration, we'll look at the write, audit, publish DAG from the example above. Note that screenshots below are from the Datakin UI integrated with Astro, but Marquez will show similar information.

SCREENSHOT

There are a few things to note about this lineage graph:

- 

## DAG Authoring with the Astro SDK

> **Note:** The Astro SDK is currently in a **preview release** state. It is not yet production-ready, and interfaces may change. We welcome users to try out the interface and [provide us with feedback](https://github.com/astronomer/astro-sdk).



## Best Practices and Considerations

Below are some best practices and considerations to keep in mind when orchestrating Snowflake queries from Airflow, based on the many implementations we've seen:

- Wherever possible, use the deferrable version of operators to save on compute. This will result in costs savings and greater scalability for your Airflow environment.
- Set your default Snowflake query specifications like Warehouse, Role, Schema, etc. in the Airflow connection. Then overwrite those parameters for specific tasks as necessary in your operator definitions. This is cleaner and easier to read than adding `USE Warehouse XYZ;` statements within your queries.
- Pay attention to which Snowflake compute resources your tasks are using, as overtaxing your assigned resources can cause slowdowns in your Airflow tasks. It is generally recommended to have different warehouses devoted to your different Airflow environments to ensure DAG development and testing does not interfere with DAGs running in production.
- Make use of [Snowflake stages](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html) when loading data from an external system using Airflow. Transfer operators like the `S3ToSnowflake` operator will require a Snowflake stage be set up. Stages generally make it much easier to repeatedly load data of a particular format.
