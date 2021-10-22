---
title: "Executing Azure Data Explorer Queries with Airflow"
description: "Executing Azure Data Explorer queries from your Apache Airflow DAGs."
date: 2021-01-08T00:00:00.000Z
slug: "airflow-azure-data-explorer"
tags: ["Integrations", "Azure", "DAGs"]
---

## Overview

[Azure Data Explorer](https://azure.microsoft.com/en-us/services/data-explorer/) (ADX) is a managed data analytics service used for performing real-time analysis of large volumes of streaming data. It's particularly useful for IoT applications, big data logging platforms, and SaaS applications.

Using Airflow's built-in Azure Data Explorer [Hook](https://registry.astronomer.io/providers/microsoft-azure/modules/azuredataexplorerhook) and [Operator](https://registry.astronomer.io/providers/microsoft-azure/modules/azuredataexplorerqueryoperator), you can easily integrate ADX queries into your DAGs. In this guide, we'll describe how to make your ADX cluster to work with Airflow and walk through an example DAG that runs a query against a database in that cluster.

If you don't already have an ADX cluster running and want to follow along with this example, you can find instructions for creating a cluster and loading it with some demo data in [Microsoft's documentation](https://docs.microsoft.com/en-us/azure/data-explorer/create-cluster-database-portal).

> Note: All code in this guide can be found on [the Astronomer Registry](https://registry.astronomer.io/dags/azure-data-explorer-tutorial).

## Configuring ADX to Work with Airflow

In order for Airflow to talk to your Azure Data Explorer database, you need to configure service principle authentication. To do this, you create and register an Azure AD service principle, then give that principle permission to access your Azure Data Explorer database. For detailed instructions on how to do this, refer to the [Azure documentation](https://docs.microsoft.com/en-us/azure/data-explorer/provision-azure-ad-app).

## Running an ADX Query with Airflow

Once you have your Azure Data Explorer cluster running and service principle authentication configured, you can get started querying a database with Airflow.

> Note: In Airflow 2.0, provider packages are separate from the core of Airflow. If you are running 2.0 with Astronomer, the [Microsoft Provider](https://registry.astronomer.io/providers/microsoft-azure) package is already included in our Airflow Certified Image; if you are not using Astronomer you may need to install this package separately to use the hooks, operators, and connections described here.

The first step is to set up an Airflow connection to your Azure Data Explorer cluster. If you do this using the Airflow UI, it should look something like this.
First, set up an Airflow connection to your Azure Data Explorer cluster. If you do this using the Airflow UI, it should look something like this:

![ADX Connection](https://assets2.astronomer.io/main/guides/azure-data-explorer/adx_connection.png)

The required pieces for the connection are:

- **Host:** your cluster URL
- **Login:** your client ID
- **Password:** your client secret
- **Extra:** should include at least "tenant" with your tenant ID, and "auth_method" with your chosen authentication method. Based on the auth method, you may also need to specify "certificate" and/or "thumbprint" parameters.

For more information on setting up this connection, including available authentication methods, see the [ADX hook documentation](https://registry.astronomer.io/providers/microsoft-azure/modules/azuredataexplorerhook).

Next, we define our DAG:

```python
from airflow import DAG
from airflow.providers.microsoft.azure.operators.adx import AzureDataExplorerQueryOperator
from datetime import datetime, timedelta

adx_query = '''StormEvents
| sort by StartTime desc
| take 10'''

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1)
}

with DAG('azure_data_explorer',
         start_date=datetime(2020, 12, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) as dag:

    opr_adx_query = AzureDataExplorerQueryOperator(
        task_id='adx_query',
        query=adx_query,
        database='storm_demo',
        azure_data_explorer_conn_id='adx'
    )
```

We define the query we want to run, `adx_query`, and pass that into the `AzureDataExplorerQueryOperator` along with the name of the database and the connection ID. When we run this DAG, the results of the query will automatically be pushed to XCom. When we go to XComs in the Airflow UI, we can see the data is there:

![ADX Xcom Results](https://assets2.astronomer.io/main/guides/azure-data-explorer/adx_xcom.png)

From here we can build out our DAG with any additional dependent or independent tasks as needed.
