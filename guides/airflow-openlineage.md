---
title: "OpenLineage and Airflow"
description: "Using OpenLineage and Marquez to get lineage data from your Airflow DAGs."
date: 2022-03-30T00:00:00.000Z
slug: "airflow-openlineage"
heroImagePath: null
tags: ["Lineage"]
---

## Overview

[Data lineage](https://en.wikipedia.org/wiki/Data_lineage) is the concept of tracking and visualizing data from its origin to wherever it flows and is consumed downstream. Its prominence in the data space is growing rapidly as companies have increasingly complex data ecosystems alongside increasing reliance on accurate data for making business decisions. Data lineage can help with everything from understanding your data sources, to troubleshooting job failures, to managing PII, to ensuring compliance with data regulations.

It follows that data lineage is a natural integration with Apache Airflow. Airflow is often used as a one-stop-shop orchestrator for an organization’s data pipelines, and is an ideal place for integrating data lineage to understand the movement and interactions of your data.

In this guide, we’ll define data lineage, review the OpenLineage standard and core lineage concepts, describe why you would want data lineage with Airflow, and show an example local integration of Airflow and OpenLineage for tracking data movement in Postgres.

> Note: This guide focuses on using OpenLineage with Airflow 2. Some topics may differs lightly if you are using it with earlier versions of Airflow.

## What is Data Lineage

Data lineage is a way of tracing the complex set of relationships that exist among datasets within an ecosystem.  The concept of data lineage encompasses:

- **Lineage metadata** that describes your datasets (e.g. a table in Snowflake) and jobs (e.g. tasks in your DAG).
- **A Lineage backend** that stores and processes lineage metadata.
- **A lineage frontend** that allows you to view and interact with your lineage metadata, including a graph that visualizes your jobs and datasets and shows how they are connected.

If you want to read more on the concept of data lineage and why it’s important, check out this [Astronomer blog post](https://www.astronomer.io/blog/what-is-data-lineage).

Visually, your data lineage graph might look something like this:

![Lineage Graph](https://assets2.astronomer.io/main/guides/airflow-openlineage/example_lineage_graph.png)

If you are using data lineage, you will likely have a lineage tool that collects lineage metadata, as well as a front end for visualizing the lineage graph. There are paid tools (including Astro) that provide these services, but in this guide we will focus on the open source options that can be integrated with Airflow: namely OpenLineage (the lineage tool) and [Marquez](https://marquezproject.github.io/marquez/) (the lineage front end).

### OpenLineage

[OpenLineage](https://openlineage.io/) is the open source industry standard framework for data lineage. Launched by Datakin, it standardizes the definition of data lineage, the metadata that makes up lineage data, and the approach for collecting lineage data from external systems. In other words, it defines a [formalized specification](https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md) for all of the core concepts (see below) related to data lineage.

The purpose of a standard like OpenLineage is to create a more cohesive lineage experience across the industry and reduce duplicated work for stakeholders. It allows for a simpler, more consistent experience when integrating lineage with many different tools, similar to how Airflow providers reduce the work of DAG authoring by providing standardized modules for integrating Airflow with other tools.

If you are working with lineage data from Airflow, that integration will be built from OpenLineage using the `openlineage-airflow` package. You can read more about that integration in the [OpenLineage documentation](https://openlineage.io/integration/apache-airflow/).

### Core Concepts

The following terms are used frequently when discussing data lineage and OpenLineage in particular. We define them here specifically in the context of using OpenLineage with Airflow.

- **Integration:** A means of gathering lineage data from a source system (e.g. a scheduler or data platform). For example, the OpenLineage Airflow integration allows lineage data to be collected from Airflow DAGs. Existing integrations automatically gather lineage data from the source system every time a job runs, preparing and transmitting OpenLineage events to a lineage backend. A full list of OpenLineage integrations can be found [here](https://openlineage.io/integration).
- **Extractor:** An extractor is a module that gathers lineage metadata from a specific hook or operator. For example, in the openlineage-airflow package, extractors exist for the `PostgresOperator` and `SnowflakeOperator`, meaning that if `openlineage-airflow` is installed and running in your Airflow environment, lineage data will be generated automatically from those operators when your DAG runs. An extractor must exist for a specific operator to get lineage data from it.
- **Job:** A process which consumes or produces datasets. Jobs can be viewed on your lineage graph. In the context of the Airflow integration, an OpenLineage job corresponds to a task in your DAG. Note that only tasks that come from operators with extractors will have input and output metadata; other tasks in your DAG will show as orphaned on the lineage graph.
- **Dataset:** A representation of a set of data in your lineage data and graph. For example, it might correspond to a table in your database or a set of data you run a Great Expectations check on. Typically a dataset is registered as part of your lineage data when a job writing to the dataset is completed (e.g. data is inserted into a table).
- **Run:** An instance of a job where lineage data is generated. In the context of the Airflow integration, an OpenLineage run will be generated with each DAG run.
- **Facet:** A piece of lineage metadata about a job, dataset, or run (e.g. you might hear “job facet”).

## Why OpenLineage with Airflow?

In the section above, we describe *what* lineage is, but a question remains *why* you would want to have data lineage in conjunction with Airflow. Using OpenLineage with Airflow allows you to have more insight into complex data ecosystems and can lead to better data governance. Airflow is a natural place to integrate data lineage, because it is often used as a one-stop-shop orchestrator that touches data across many parts of an organization.

More specifically, OpenLineage with Airflow provides the following capabilities:

- Quickly find the root cause of task failures by identifying issues in upstream datasets (e.g. if an upstream job outside of Airflow failed to populate a key dataset).
- Easily see the blast radius of any job failures or changes to data by visualizing the relationship between jobs and datasets.
- Identify where key data is used in jobs across an organization.

These capabilities translate into real world benefits by:

- Making recovery from complex failures quicker. The faster you can identify the problem and the blast radius, the easier it is to solve and prevent any erroneous decisions being made from bad data.
- Making it easier for teams to work together across an organization. Visualizing the full scope of where a dataset is used reduces “sleuthing” time.
- Helping ensure compliance with data regulations by fully understanding where data is used.

## Example OSS Integration

In this example, we’ll show how to run OpenLineage with Airflow locally using Marquez as a lineage front end. We’ll then show how to use and interpret the lineage data generated by a simple DAG that processes data in Postgres. All of the tools used in this example are open source.

### Running Marquez and Airflow Locally

For this example, we’ll run Airflow with OpenLineage and Marquez locally. You will need to install Docker and the [Astro CLI](https://docs.astronomer.io/cloud/install-cli) before starting.

1. Run Marquez locally using the quickstart in the [Marquez README](https://github.com/MarquezProject/marquez#quickstart).
2. Start an Astro project using the CLI by creating a new directory and running `astrocloud dev init`.
3. Add `openlineage-airflow` to your `requirements.txt` file. Note if you are using Astro Runtime 4.2.1 or greater, this package is already included.
4. Add the environment variables below to your `.env` file. These will allow Airflow to connect with the OpenLineage API and send your lineage data to Marquez.
    
    ```bash
    OPENLINEAGE_URL=http://host.docker.internal:5000
    OPENLINEAGE_NAMESPACE=example
    AIRFLOW__LINEAGE__BACKEND=openlineage.lineage_backend.OpenLineageBackend
    ```
    
    By default, Marquez uses port 5000 when you run it using Docker. If you are using a different OpenLineage front end instead of Marquez, or you are running Marquez remotely, you can modify the `OPENLINEAGE_URL` as needed.
    
5. Modify your `config.yaml` in the `.astrocloud/` directory to choose a different port for Postgres. Marquez also uses Postgres, so you will need to have Airflow use a different port than the default 5432, which will already be allocated.
    
    ```yaml
    project:
      name: openlineage
    postgres:
      port: 5435
    ```
    
6. Run Airflow locally using `astrocloud dev start`.
7. Confirm Airflow is running by going to `http://localhost:8080`, and Marquez is running by going to `http://localhost:3000`.

#### Postgres Connection
Check to see if your deployment has a connection called `postgres_default`:
```sh
astrocloud dev run connections get postgres_default
id | conn_id          | conn_type | ... | get_uri
1  | postgres_default | postgres  | ... | postgres://postgres:postgres@postgres:5432
```

If this command doesn't return anything or doesn't include a line with `postgres_default` in the `conn_id` column, you'll need to create a connection. To do so from the Airflow UI, hover over the "Admin" dropdown and click "Connections". Then, click the blue "+" icon. Define the connection with the following values:
- Connection Id: postgres_default
- Connection Type: Postgres
- Host: postgres
- Login: postgres
- Password: postgres
- Port: 5432

> NOTE: This creates a connection to the Airflow metadata database. It is not recommended to store significant amounts of additional data in the metadata database in production for performance reasons.

### Generating and Viewing Lineage Data

To show the lineage data that can result from Airflow DAG runs, we'll use an example of two DAGs that process data in Postgres. The first DAG creates and populates tables called `adoption_center_1` and `adoption_center_2`. The second creates a table called `animal_adoptions_combined` with data aggregated from two source tables (`adoption_center_1` and `adoption_center_2`). 

You can also update the table names and schemas in the DAG to reference existing tables in your own environment.

lineage_create_tables.py:
```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from datetime import datetime, timedelta

create_table_1_query = """
CREATE TABLE IF NOT EXISTS adoption_center_1
(date DATE, type VARCHAR, name VARCHAR, age INTEGER);
"""

create_table_2_query = """CREATE TABLE IF NOT EXISTS adoption_center_2
(date DATE, type VARCHAR, name VARCHAR, age INTEGER);
"""

insert_table_1_query = """
INSERT INTO
    adoption_center_1 (date, type, name, age)
VALUES
    ('2022-01-01', 'Dog', 'Bingo', 4),
    ('2022-02-02', 'Cat', 'Bob', 7),
    ('2022-03-04', 'Fish', 'Bubbles', 2);
"""

insert_table_2_query = """
INSERT INTO
    adoption_center_2 (date, type, name, age)
VALUES
    ('2022-06-10', 'Horse', 'Seabiscuit', 4),
    ('2022-07-15', 'Snake', 'Stripes', 8),
    ('2022-08-07', 'Rabbit', 'Hops', 3);
"""

with DAG('lineage-create-tables',
         start_date=datetime(2020, 6, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args = {
            'retries': 1,
            'retry_delay': timedelta(minutes=1)
        },
         catchup=False
         ) as dag:

    create_table_1 = PostgresOperator(
        task_id='create_table_1',
        postgres_conn_id='postgres_default',
        sql=create_table_1_query
    ) 

    create_table_2 = PostgresOperator(
        task_id='create_table_2',
        postgres_conn_id='postgres_default',
        sql=create_table_2_query
    )

    insert_table_1 = PostgresOperator(
        task_id='insert_table_1',
        postgres_conn_id='postgres_default',
        sql=insert_table_1_query
    )

    insert_table_2 = PostgresOperator(
        task_id='insert_table_2',
        postgres_conn_id='postgres_default',
        sql=insert_table_2_query
    )

    create_table_1 >> insert_table_1
    create_table_2 >> insert_table_2

```

lineage_combine_postgres.py:
```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from datetime import datetime, timedelta

create_table_query= '''
CREATE TABLE IF NOT EXISTS animal_adoptions_combined (date DATE, type VARCHAR, name VARCHAR, age INTEGER);
'''

combine_data_query= '''
INSERT INTO animal_adoptions_combined (date, type, name, age) 
SELECT * 
FROM adoption_center_1
UNION 
SELECT *
FROM adoption_center_2;
'''


with DAG('lineage-combine-postgres',
         start_date=datetime(2020, 6, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args = {
            'retries': 1,
            'retry_delay': timedelta(minutes=1)
        },
         catchup=False
         ) as dag:

    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql=create_table_query
    ) 

    insert_data = PostgresOperator(
        task_id='combine',
        postgres_conn_id='postgres_default',
        sql=combine_data_query
    ) 

    create_table >> insert_data
```

lineage_reporting_postgres.py:

```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from datetime import datetime, timedelta

aggregate_reporting_query = '''
INSERT INTO adoption_reporting_long (date, type, number)
SELECT c.date, c.type, COUNT(c.type)
FROM animal_adoptions_combined c
GROUP BY date, type;
'''

with DAG('lineage-reporting-postgres',
         start_date=datetime(2020, 6, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args={
            'retries': 1,
            'retry_delay': timedelta(minutes=1)
        },
         catchup=False
         ) as dag:

    create_table = PostgresOperator(
        task_id='create_reporting_table',
        postgres_conn_id='postgres_default',
        sql='CREATE TABLE IF NOT EXISTS adoption_reporting_long (date DATE, type VARCHAR, number INTEGER);',
    ) 

    insert_data = PostgresOperator(
        task_id='reporting',
        postgres_conn_id='postgres_default',
        sql=aggregate_reporting_query
    ) 

    create_table >> insert_data
```

If we run these DAGs in Airflow (first `lineage-create-tables`, then `lineage-combine-postgres`, and finally `lineage-reporting-postgres`), and then go to Marquez, we will see a list of our jobs, including the four tasks from the DAGs above.

![Marquez Jobs](https://assets2.astronomer.io/main/guides/airflow-openlineage/marquez_jobs.png)

Then, if we click on one of the jobs from our DAGs, we see the full lineage graph.

![Marquez Graph](https://assets2.astronomer.io/main/guides/airflow-openlineage/marquez_lineage_graph.png)

The lineage graph shows:

- Two origin datasets that are used to populate the combined data table
- The two jobs (tasks) from our DAGs that result in new datasets: `combine` and `reporting`
- Two new datasets that are created by those jobs

The lineage graph shows us how these two DAGs are connected and how data flows through the entire pipeline, giving us insight we wouldn't have if we were to view these DAGs in the Airflow UI alone.

## Lineage on Astro

For Astronomer customers using [Astro](https://www.astronomer.io/product/), OpenLineage is integrated and available out of the box. The **Lineage** tab in the Astronomer UI provides multiple pages that can help you troubleshoot issues with your data pipelines and understand the movement of data across your Organization. For more on lineage capabilities with Astro, check out [our documentation](https://docs.astronomer.io/astro/data-lineage) or [reach out to us](https://www.astronomer.io/openlineage). 

## Limitations

OpenLineage is rapidly evolving, and new functionality and integrations are being added all the time. At the time of writing, the following are limitations when using OpenLineage with Airflow:

- The OpenLineage integration with Airflow 2 is currently experimental.
- You must be running Airflow 2.3.0+ with OpenLineage 0.8.1+ to get lineage data for *failed* task runs.
- Only the following operators have bundled extractors (needed to collect lineage data out of the box):

    - `PostgresOperator`
    - `SnowflakeOperator`
    - `BigQueryOperator`
    
    To get lineage data from other operators, you can create your own custom extractor.
- To get lineage from an external system connected to Airflow, such as [Apache Spark](https://openlineage.io/integration/apache-spark/), you will need to configure an [OpenLineage integration](https://openlineage.io/integration) with that system in addition to Airflow.
