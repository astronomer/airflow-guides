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

There are multiple open source packages with modules available to implement various Snowflake orchestration use cases in Airflow. The [Snowflake provider package](https://registry.astronomer.io/providers/snowflake) contains hooks, operators, and transfer operators maintained by the Airflow community. Additionally, [Astronomer Providers](https://github.com/astronomer/astronomer-providers) contains deferrable operators built and maintained by Astronomer, including a deferrable version of the `SnowflakeOperator`. 

To leverage all of the Snowflake modules available in Airflow, we recommend installing both `apache-airflow-providers-snowflake` and `astronomer-providers[snowflake]` in your Airflow environment.

Modules for orchestrating basic queries and functions in Snowflake include:

- [`SnowflakeHook`](https://registry.astronomer.io/providers/snowflake/modules/snowflakehook): A hook abstracting the Snowflake API. Generally the hook would only be used by a DAG author when creating a custom operator or function. This hook is part of `apache-airflow-providers-snowflake`. 
- [`SnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator): Executes a SQL query in Snowflake. This operator is part of `apache-airflow-providers-snowflake`.
- [`S3ToSnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/s3tosnowflakeoperator): Executes a COPY command to transfer data from S3 into Snowflake.
- [`SnowflakeToSlackOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflaketoslackoperator): Executes a SQL query in Snowflake and sends the results to Slack.
- `SnowflakeOperatorAsync`: The deferrable version of the `SnowflakeOperator`, executes a SQL query in Snowflake.
- `SnowflakeHookAsync`: The deferrable version of the `SnowflakeHook`, abstracts the Snowflake API.

Modules for orchestrating **data quality checks** in Snowflake include:

- [`SnowflakeCheckOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakecheckoperator): Performs a check against Snowflake. The SQL provided should return a single row, and if any value in that row is `False`, the task will fail. This operator is used to implement data quality checks in Snowflake.
- [`SnowflakeValueCheckOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakecheckoperator): Performs a check against a specific value in Snowflake, within a given tolerance. 
- [`SnowflakeIntervalCheckOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakeintervalcheckoperator): Performs a check against the value of metrics compared to the same metrics a given number of days before. 

Below we show an example of how to use some of these modules in an ELT DAG with data quality checks.

#### Example Implementation

DAG using deferrable operators and data quality checks

Include setting up connection.

> **Note:** To make use of deferrable operators you must have a Triggerer running in your Airflow environment. For more on how to use deferrable operators, check out [this guide](https://www.astronomer.io/guides/deferrable-operators).

## Enhanced Observability with OpenLineage

The [OpenLineage project](https://openlineage.io/) maintains an integration with Airflow that allows users to obtain and view lineage data from their tasks. As long as an extractor exists for the operator being used, lineage data will be generated automatically from each task instance. For introductory information on how OpenLineage works with Airflow, check out [this guide](https://www.astronomer.io/guides/airflow-openlineage).

Users of the `SnowflakeOperator`, which does have an extractor, will be able to use lineage metadata to answer questions across DAGs such as:

- How does data stored in Snowflake flow through my DAGs? Are there any upstream dependencies?
- What downstream data does a task failure impact?
- Where did a change in data format originate?

At a high level, the OpenLineage - Airflow - Snowflake interaction works like this:

SCREENSHOT

Note that to view lineage data from your DAGs you need to have OpenLineage installed in your Airflow environment, and a lineage front end running. For [Astro customers](https://docs.astronomer.io/astro/data-lineage), lineage is enabled automatically. For users working with open source tools, you can run Marquez locally and connect it to your Airflow environment following the instructions in [this guide](https://www.astronomer.io/guides/airflow-openlineage). 

To show an example of lineage resulting from Snowflake orchestration, we'll look at the lineage graph generated by the example DAG above. Note that screenshots below are from the Datakin UI integrated with Astro, but Marquez will show similar information.

SCREENSHOT

There are a few things to note about this lineage graph:

- 

## DAG Authoring with the Astro SDK

> **Note:** The Astro SDK is currently in a **preview release** state. It is not yet production-ready, and interfaces may change. We welcome users to try out the interface and [provide us with feedback](https://github.com/astronomer/astro-sdk).



## Best Practices and Considerations

Below are some best practices and considerations to keep in mind when orchestrating Snowflake queries from Airflow, based on the many implementations we've seen.

- Wherever possible, use the deferrable version of operators to save on compute. This will result in costs savings and greater scalability for your Airflow environment.
- Set your default Snowflake query specifications like Warehouse, Role, Schema, etc. in the Airflow connection. Then overwrite those parameters for specific tasks as necessary in your operator definitions. This is cleaner and easier to read than adding `USE Warehouse XYZ;` statements within your queries.
- Pay attention to which Snowflake compute resources your tasks are using, as overtaxing your assigned resources can cause unnecessary slowdowns in your Airflow tasks. It is generally recommended to have different warehouses devoted to your different Airflow environments to ensure DAG development and testing does not interfere with DAGs running in production.
- Make use of [Snowflake stages](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html) when loading data from an external system using Airflow. Transfer operators like the `S3ToSnowflake` operator will require a Snowflake stage be set up. Stages generally make it much easier to repeatedly load data of a particular format.
