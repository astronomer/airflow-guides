---
title: "Orchestrating Snowflake Queries with Airflow"
description: "How to use Airflow to get enhanced observability and compute savings while orchestrating your Snowflake jobs."
date: 2022-07-20T00:00:00.000Z
slug: "airflow-snowflake"
tags: ["Integrations", "ETL", "Database"]
---

## Overview

[Snowflake](https://www.snowflake.com/) is one of the most commonly used data warehouses and features heavily in data engineering, data science, and data analytics workflows. Orchestrating Snowflake queries as part of a data pipeline is one of the most common use cases we see for Airflow. Using Airflow with Snowflake is straightforward, and there are multiple open source packages, tools, and integrations that can help you take your Snowflake query orchestration to the next level.

In this guide, we cover everything you need to know to make the most out of Airflow and Snowflake, including:

- Using Snowflake providers, including what modules are out there and how to implement deferrable versions of common operators.
- Leveraging the OpenLineage Airflow integration to get data lineage and enhanced observability from your Snowflake jobs.
- Using the Astro SDK for the next generation of DAG authoring for Snowflake query tasks.
- General best practices and considerations when interacting with Snowflake from Airflow.

## Using Snowflake Providers

There are multiple open source packages that you can use to orchestrate Snowflake in Airflow: 

- The [Snowflake provider package](https://registry.astronomer.io/providers/snowflake) contains hooks, operators, and transfer operators for Snowflake maintained by the Airflow community.
- The [Astronomer Providers](https://github.com/astronomer/astronomer-providers) package contains deferrable operators built and maintained by Astronomer, including a deferrable version of the `SnowflakeOperator`.
- The [Common SQL provider package](https://registry.astronomer.io/providers/common-sql) contains SQL check operators that can be used to perform data quality checks against data in Snowflake. 

To leverage all of the Snowflake modules available in Airflow, we recommend installing all three packages in your Airflow environment. If you use the Astro CLI, you can do this by adding the following three lines to your `requirements.txt` file:

```bash
apache-airflow-providers-snowflake
apache-airflow-providers-common-sql
astronomer-providers[snowflake]
```

Modules for orchestrating basic queries and functions in Snowflake include:

- [`SnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflakeoperator): Executes a SQL query in Snowflake. This operator is part of `apache-airflow-providers-snowflake`.
- [`S3ToSnowflakeOperator`](https://registry.astronomer.io/providers/snowflake/modules/s3tosnowflakeoperator): Executes a COPY command to transfer data from S3 into Snowflake.
- [`SnowflakeToSlackOperator`](https://registry.astronomer.io/providers/snowflake/modules/snowflaketoslackoperator): Executes a SQL query in Snowflake and sends the results to Slack.
- `SnowflakeOperatorAsync`: The [deferrable](https://www.astronomer.io/guides/deferrable-operators) version of the `SnowflakeOperator`, executes a SQL query in Snowflake.
- [`SnowflakeHook`](https://registry.astronomer.io/providers/snowflake/modules/snowflakehook): A hook abstracting the Snowflake API. Generally, you only need to use this hook when creating a custom operator or function. This hook is part of `apache-airflow-providers-snowflake`. 
- `SnowflakeHookAsync`: The [deferrable](https://www.astronomer.io/guides/deferrable-operators) version of the `SnowflakeHook`, abstracts the Snowflake API.

Modules for orchestrating **data quality checks** in Snowflake include:

- [`SQLColumnCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqlcolumncheckoperator): Performs a data quality check against columns of a given table. Using this operator with Snowflake requires a Snowflake connection ID, the name of the table to run checks on, and a `column_mapping` describing the relationship between columns and tests to run.
- [`SQLTableCheckOperator`](https://registry.astronomer.io/providers/common-sql/modules/sqltablecheckoperator): Performs a data quality check against a given table. Using this operator with Snowflake requires a Snowflake connection ID, the name of the table to run checks on, and a checks dictionary describing the relationship between the table and the tests to run.  

Note that the `apache-airflow-providers-snowflake` package also contains operators that can be used to run data quality checks in Snowflake, including the `SnowflakeCheckOperator`, `SnowflakeValueCheckOperator`, and `SnowflakeIntervalCheckOperator`. However, these operators are not as flexible as the operators in `apache-airflow-providers-common-sql` and will likely be deprecated in a future version of Airflow. We recommend using `apache-airflow-providers-common-sql` for the most up to date data quality check operators. For more details on using the SQL check operators, check out [this guide](https://www.astronomer.io/guides/airflow-sql-data-quality-tutorial).

Let's walk through an example of how to use some of these modules in a DAG that implements a write, audit, publish pattern with data quality checks.

### Example Implementation

> **Note:** Example code using various Snowflake operators can be found on the [Astronomer Registry](https://registry.astronomer.io/dags/complex-snowflake-transform). 

The example DAG below runs a write, audit, publish pattern to showcase loading and data quality checking with Snowflake. The following steps are completed:

- Simultaneously create tables in Snowflake for the production data and the raw data that needs to be audited using the `SnowflakeOperator`. Note that these tasks are not implemented with the deferrable version of the `SnowflakeOperator` because `CREATE TABLE` statements typically run very quickly.
- Load data into the audit table using the `SnowflakeOperatorAsync`. This task *is* deferred to save on compute, because loading data can take some time if the dataset is large. Note that to use the deferrable operator, you must have a [triggerer running](https://www.astronomer.io/guides/deferrable-operators#running-deferrable-tasks-in-your-airflow-environment) in your Airflow environment.
- Run data quality checks on the audit table to ensure that no erroneous data is moved to production. This task group includes column checks using the `SQLColumnCheckOperator` and table checks using the `SQLTableCheckOperator`. 
- If the data quality checks are passed, copy data from the audit table into the production table using the `SnowflakeOperatorAsync`.
- Delete the audit table since it only contained temporary data.

> **Note:** To make use of deferrable operators you must have a Triggerer running in your Airflow environment. For more on how to use deferrable operators, check out [this guide](https://www.astronomer.io/guides/deferrable-operators).

All of these tasks rely on parameterized SQL scripts that are stored in the `include/sql/` directory and can be found in the Astronomer Registry link above. 

The DAG looks like this:

```python
import json

from pathlib import Path

from airflow import DAG
from airflow.models.baseoperator import chain
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from astronomer.providers.snowflake.operators.sensors.snowflake import SnowflakeOperatorAsync
from airflow.providers.common.sql.operators import SQLColumnCheckOperator, SQLTableCheckOperator
from airflow.utils.dates import datetime
from airflow.utils.task_group import TaskGroup

from include.libs.schema_reg.base_schema_transforms import snowflake_load_column_string


SNOWFLAKE_FORESTFIRE_TABLE = "forestfires"
SNOWFLAKE_AUDIT_TABLE = f"{SNOWFLAKE_FORESTFIRE_TABLE}_AUDIT"
SNOWFLAKE_CONN_ID = "snowflake_default"

base_path = Path(__file__).parents[2]
table_schema_path = (
    f"{base_path}/include/sql/snowflake_examples/table_schemas/"
)

with DAG(
    "snowflake_write_audit_publish",
    description="Example DAG showcasing loading and data quality checking with Snowflake.",
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,
    template_searchpath="/usr/local/airflow/include/sql/snowflake_examples/",
    catchup=False,
    default_args={"conn_id": SNOWFLAKE_CONN_ID, "snowflake_conn_id": SNOWFLAKE_CONN_ID}
) as dag:

    create_forestfire_audit_table = SnowflakeOperator(
        task_id="create_forestfire_audit_table",
        sql="create_forestfire_table.sql",
        params={"table_name": SNOWFLAKE_AUDIT_TABLE},
    )

    create_forestfire_production_table = SnowflakeOperator(
        task_id="create_forestfire_production_table",
        sql="create_forestfire_table.sql",
        params={"table_name": SNOWFLAKE_FORESTFIRE_TABLE}
    )

    load_data = SnowflakeOperatorAsync(
        task_id="insert_query",
        sql="load_snowflake_forestfire_data.sql",
        params={"table_name": SNOWFLAKE_AUDIT_TABLE}
    )

    with TaskGroup(group_id="quality_checks") as quality_check_group:

        column_checks = SQLColumnCheckOperator(
            task_id="column_checks",
            table=SNOWFLAKE_AUDIT_TABLE,
            column_mapping={"id": {"null_check": {"equal_to": 0}}}
        )

        table_checks = SQLTableCheckOperator(
            task_id="table_checks",
            table=SNOWFLAKE_AUDIT_TABLE,
            checks={"row_count_check": {"check_statement": "COUNT(*) = 9"}}
        )

    with open(
        f"{table_schema_path}/forestfire_schema.json",
        "r",
    ) as f:
        table_schema = json.load(f).get("forestfire")
        table_props = table_schema.get("properties")
        table_dimensions = table_schema.get("dimensions")
        table_metrics = table_schema.get("metrics")

        col_string = snowflake_load_column_string(table_props)

        copy_snowflake_audit_to_production_table = SnowflakeOperator(
            task_id="copy_snowflake_audit_to_production_table",
            sql="copy_forestfire_snowflake_audit.sql",
            params={
                "table_name": SNOWFLAKE_FORESTFIRE_TABLE,
                "audit_table_name": f"{SNOWFLAKE_FORESTFIRE_TABLE}_AUDIT",
                "table_schema": table_props,
                "col_string": col_string,
            },
            trigger_rule="all_success"
        )

    delete_audit_table = SnowflakeOperator(
        task_id="delete_audit_table",
        sql="delete_forestfire_table.sql",
        params={"table_name": f"{SNOWFLAKE_FORESTFIRE_TABLE}_AUDIT"},
        trigger_rule="all_success"
    )

    begin = DummyOperator(task_id="begin")
    end = DummyOperator(task_id="end")

    chain(
        begin,
        [create_forestfire_production_table, create_forestfire_audit_table],
        load_data,
        quality_check_group,
        copy_snowflake_audit_to_production_table,
        delete_audit_table,
        end
    )
```

![Snowflake DAG Graph](https://assets2.astronomer.io/main/guides/airflow-snowflake/snowflake_dag_graph.png)

Note that to run this DAG, you need an Airflow connection to your Snowflake instance. This DAG uses a connection called `snowflake_default`. Your connection should have a type of `Snowflake` include the following information:

```yaml
Host: <Your Snowflake host, e.g. `account.region.snowflakecomputing.com`>
Schema: <Your schema>
Login: <Your login>
Password: <Your password>
Account: <Your Snowflake account>
Database: <Your database>
Region: <Your account region>
Role: <Your role>
Warehouse: <Your warehouse>
```

## Enhanced Observability with OpenLineage

The [OpenLineage project](https://openlineage.io/) maintains an integration with Airflow that allows users to obtain and view lineage data from their Airflow tasks. As long as an extractor exists for the operator being used, lineage data will be generated automatically from each task instance. For introductory information on how OpenLineage works with Airflow, check out [this guide](https://www.astronomer.io/guides/airflow-openlineage).

Because `SnowflakeOperator` and `SnowflakeOperatorAsync` have an extractor, you can use lineage metadata to answer questions across DAGs such as:

- How does data stored in Snowflake flow through my DAGs? Are there any upstream dependencies?
- What downstream data does a task failure impact?
- Where did a change in data format originate?

At a high level, the OpenLineage - Airflow - Snowflake interaction works like this:

![Snowflake Openlineage](https://assets2.astronomer.io/main/guides/airflow-snowflake/snowflake_openlineage_architecture.png)

Note that to view lineage data from your DAGs you need to have OpenLineage installed in your Airflow environment and a lineage front end running. For [Astro users](https://docs.astronomer.io/astro/data-lineage), lineage is enabled automatically. For users working with open source tools, you can run Marquez locally and connect it to your Airflow environment following the instructions in [this guide](https://www.astronomer.io/guides/airflow-openlineage). 

To show an example of lineage resulting from Snowflake orchestration, we'll look at the write, audit, publish DAG from the example above. Note that screenshots below are from the Datakin UI integrated with Astro, but Marquez will show similar information.

![Lineage Graph](https://assets2.astronomer.io/main/guides/airflow-snowflake/lineage_graph.png)

Looking at the lineage graph, we can see the flow of data from the creation of the table, to the insertion of data, to the data quality checks. If any failures were to happen, particularly in the data quality checks, the lineage graph would quickly tell us which datasets were impacted. If our work on this dataset expanded into other DAGs in Airflow, we would see those connections here as well, all in one place.

## DAG Authoring with the Astro SDK Python

The Astro SDK Python is an open source DAG authoring tool maintained by Astronomer simplifies the data transformation process between different environments, such that you can focus solely on writing execution logic without worrying about Airflow orchestration logic. Details like creating dataframes, storing intermediate results, passing context and data between tasks, and creating Airflow task dependencies are all managed automatically.

> **Note:** The Astro SDK is currently in a preview release state. It is not yet production-ready, and interfaces may change. We welcome users to try out the interface and [provide us with feedback](https://github.com/astronomer/astro-sdk).

The Astro SDK Python supports Snowflake as a data warehouse and can be used to simplify ETL workflows with Snowflake. For example, the following DAG moves data from S3 into Snowflake, performs some data transformations, and loads the resulting data into a reporting table.

```python
from datetime import datetime

from airflow.models import DAG
from pandas import DataFrame

from astro import sql as aql
from astro.files import File
from astro.sql.table import Table

S3_FILE_PATH = "s3://<aws-bucket-name>"
S3_CONN_ID = "aws_default"
SNOWFLAKE_CONN_ID = "snowflake_default"
SNOWFLAKE_ORDERS = "orders_table"
SNOWFLAKE_FILTERED_ORDERS = "filtered_table"
SNOWFLAKE_JOINED = "joined_table"
SNOWFLAKE_CUSTOMERS = "customers_table"
SNOWFLAKE_REPORTING = "reporting_table"


@aql.transform
def filter_orders(input_table: Table):
    return "SELECT * FROM {{input_table}} WHERE amount > 150"


@aql.transform
def join_orders_customers(filtered_orders_table: Table, customers_table: Table):
    return """SELECT c.customer_id, customer_name, order_id, purchase_date, amount, type
    FROM {{filtered_orders_table}} f JOIN {{customers_table}} c
    ON f.customer_id = c.customer_id"""


@aql.dataframe
def transform_dataframe(df: DataFrame):
    purchase_dates = df.loc[:, "purchase_date"]
    print("purchase dates:", purchase_dates)
    return purchase_dates


dag = DAG(
    dag_id="astro_orders",
    start_date=datetime(2019, 1, 1),
    schedule_interval="@daily",
    catchup=False,
)

with dag:
    # Extract a file with a header from S3 into a Table object
    orders_data = aql.load_file(
        # data file needs to have a header row
        input_file=File(
            path=S3_FILE_PATH + "/orders_data_header.csv", conn_id=S3_CONN_ID
        ),
        output_table=Table(conn_id=SNOWFLAKE_CONN_ID),
    )

    # create a Table object for customer data in our Snowflake database
    customers_table = Table(
        name=SNOWFLAKE_CUSTOMERS,
        conn_id=SNOWFLAKE_CONN_ID,
    )

    # filter the orders data and then join with the customer table
    joined_data = join_orders_customers(filter_orders(orders_data), customers_table)

    # merge the joined data into our reporting table, based on the order_id .
    # If there's a conflict in the customer_id or customer_name then use the ones from
    # the joined data
    reporting_table = aql.merge(
        target_table=Table(
            name=SNOWFLAKE_REPORTING,
            conn_id=SNOWFLAKE_CONN_ID,
        ),
        source_table=joined_data,
        target_conflict_columns=["order_id"],
        columns=["customer_id", "customer_name"],
        if_conflicts="update",
    )

    purchase_dates = transform_dataframe(reporting_table)
```

Using Astro SDK `aql` functions, we are able to seamlessly transition between SQL transformations (`filter_orders` and `join_orders_customers`) to Python dataframe transformations (`transform_dataframe`). All intermediary data created by each task is automatically stored in Snowflake and made available to downstream tasks.

For more detailed instructions on running this example DAG, check out the [Astro SDK tutorial](https://github.com/astronomer/astro-sdk/blob/main/TUTORIAL.md).

## Best Practices and Considerations

Below are some best practices and considerations to keep in mind when orchestrating Snowflake queries from Airflow, based on the many implementations we've seen:

- Wherever possible, use the deferrable version of operators to save on compute. This will result in costs savings and greater scalability for your Airflow environment.
- Set your default Snowflake query specifications like Warehouse, Role, Schema, etc. in the Airflow connection. Then overwrite those parameters for specific tasks as necessary in your operator definitions. This is cleaner and easier to read than adding `USE Warehouse XYZ;` statements within your queries.
- Pay attention to which Snowflake compute resources your tasks are using, as overtaxing your assigned resources can cause slowdowns in your Airflow tasks. It is generally recommended to have different warehouses devoted to your different Airflow environments to ensure DAG development and testing does not interfere with DAGs running in production.
- Make use of [Snowflake stages](https://docs.snowflake.com/en/sql-reference/sql/create-stage.html) when loading data from an external system using Airflow. Transfer operators like the `S3ToSnowflake` operator will require a Snowflake stage be set up. Stages generally make it much easier to repeatedly load data of a particular format.
