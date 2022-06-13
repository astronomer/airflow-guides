---
title: "Orchestrating Snowflake Queries with Airflow"
description: "How to use Airflow to get enhanced observability and compute savings while orchestrating your Snowflake jobs."
date: 2022-06-17T00:00:00.000Z
slug: "airflow-snowflake"
tags: ["Integrations", "ETL", "Database"]
---

## Overview

[Snowflake](https://www.snowflake.com/) is one of the most commonly used data warehouses thanks to its built-in compute and many data-centric features, and features heavily in data engineering, data science, and data analytics workflows. As such, orchestrating Snowflake queries as part of a data pipeline is one of the most common use cases we see for Airflow. Using Airflow with Snowflake is straight forward, and there are multiple open source packages, tools, and integrations that can help you take your Snowflake query orchestration to the next level.

In this guide, we'll cover everything you need to know to make the most out of your "Airflow + Snowflake" experience, including:

- Using Snowflake providers, including what modules are out there and how to implement deferrable versions of common operators
- Leveraging the OpenLineage Airflow integration to get data lineage and enhanced observability from your Snowflake jobs
- Using the Astro SDK for the next generation of DAG authoring for Snowflake query tasks
- General best practices and considerations when interacting with Snowflake from Airflow

## Using Snowflake Providers

There are multiple open source packages with modules available to implement various Snowflake orchestration use cases in Airflow. The [Snowflake provider package](https://registry.astronomer.io/providers/snowflake) contains hooks, operators, and transfer operators maintained by the Airflow community. Additionally, [Astronomer Providers](https://github.com/astronomer/astronomer-providers) contains deferrable operators built and maintained by Astronomer, including a deferrable version of the `SnowflakeOperator`. 

To leverage all of the Snowflake modules available in Airflow, we recommend installing both `apache-airflow-providers-snowflake` and `astronomer-providers[snowflake]` in your Airflow environment. In general, if a deferrable operator exists for your use case, we recommend using it over the analogous traditional operator to save on compute.

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

Below we show an example of how to use some of these modules in an ELT DAG.

#### Example Implementation

DAG using deferrable operators and data quality checks

Include setting up connection.

> **Note:** To make use of deferrable operators you must have a Triggerer running. For more on how to use deferrable operators, check out [this guide](https://www.astronomer.io/guides/deferrable-operators).

## Enhanced Observability with OpenLineage

The [OpenLineage project](https://openlineage.io/) maintains an integration with Airflow that allows users to obtain and view lineage data from their tasks. As long as an extractor exists for the operator being used, lineage data will be generated automatically from each task instance. For more general introductory information on how OpenLineage works with Airflow, check out [this guide](https://www.astronomer.io/guides/airflow-openlineage).

Users of the `SnowflakeOperator`, which does have an extractor, will be able to use lineage metadata to answer questions across DAGs, like:

- How does data stored in Snowflake flow through my DAGs? Are there any upstream dependencies?
- What downstream data does a task failure impact?
- Where did a change in data format originate?
- 



Lineage for example DAG from above.

## DAG Authoring with the Astro SDK

> **Note:** The Astro SDK is currently in a preview release state. It is not yet production-ready, and interfaces may change. We welcome users to try out the interface and [provide us with feedback](https://github.com/astronomer/astro-sdk).

Rewrite of DAG above with the sdk?

## Best Practices and Considerations

Based on feedback from team. Put this last or directly after overview?

- Wherever possible, use the deferrable version of operators to save on compute. This will result in costs savings and greater scalability for your Airflow environment. 
