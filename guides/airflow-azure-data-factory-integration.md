---
title: "Executing Azure Data Factory Pipelines with Airflow"
description: "Triggering remote jobs in Azure Data Factory from your Apache Airflow DAGs."
date: 2021-01-28T00:00:00.000Z
slug: "airflow-azure-data-factory-integration"
tags: ["Integrations", "Azure"]
---

## Overview

Azure Data Factory (ADF) is a commonly used service for constructing data pipelines and jobs. With a little preparation, it can be used in combination with Airflow to leverage the best of both tools. In this guide, we'll discuss why you might want to use these two tools together, how Airflow can be used to execute ADF jobs, and a simple example tutorial showing how it all fits together.

> **Note:** All code in this guide can be found on [the Astronomer Registry](https://registry.astronomer.io/dags/example-adf-run-pipeline).

## Why Use Airflow with ADF

ADF is an easy to learn tool that allows you to quickly create jobs without writing tons of code. It integrates seamlessly with on-prem data sources and other Azure services. However, it has some disadvantages when used alone - namely:

- Building and integrating custom tools can be difficult
- Integrations with services outside of Azure are limited
- Orchestration capabilities are limited
- Custom packages and dependencies can be complex to manage

That's where Airflow comes in. ADF jobs can be run using an Airflow DAG, giving the full capabilities of Airflow orchestration beyond using ADF alone. This allows users that are comfortable with ADF to write their job there, while Airflow acts as the control plane for orchestration.

## ADF Modules in Airflow

The [Microsoft Azure provider](https://registry.astronomer.io/providers/microsoft-azure) has multiple modules for orchestrating ADF pipelines with Airflow.

- [`AzureDataFactoryHook`](https://registry.astronomer.io/providers/microsoft-azure/modules/azuredatafactoryhook): Abstracts the ADF API and provides an easy way of connecting to ADF from Airflow
- [`AzureDataFactoryRunPipelineOperator`](https://registry.astronomer.io/providers/microsoft-azure/modules/azuredatafactoryrunpipelineoperator): Executes an ADF pipeline
- [`AzureDataFactoryPipelineRunStatusSensor`](https://registry.astronomer.io/providers/microsoft-azure/modules/azuredatafactorypipelinerunstatussensor): Waits for an ADF pipeline run to complete

If these modules are not quite right for your use case, you can use the `AzureDataFactoryHook` in your own Python function to take advantage of any ADF API functionality. Understanding how the [ADF API](https://docs.microsoft.com/en-us/rest/api/datafactory/v1/data-factory-data-factory) works can be helpful when designing your own custom functions or understanding of how the provider modules work.

## Example Implementation

This example shows how to use ADF operators and sensors to orchestrate multiple ADF pipelines using Airflow.

### ADF Prerequisites

Before you can orchestrate your ADF pipelines with Airflow, you have to make those pipelines runnable. 

> **Note:** If you do not currently have an ADF pipeline in your Azure account and are new to ADF, check out the [ADF quick start docs](https://docs.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-portal) for help getting started.

To make your ADF pipeline accessible by Airflow you will need to register an App with Azure Active Directory to get a Client ID and Client Secret (API Key) for your Data Factory. First, go to Azure Active Directory and click on 'Registered Apps' to see a list of registered apps. If you created a Resource group, you should already have an app registered with the same name.

![ADF App Registration](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_app_registration.png)

Once there click on the app associated with your resource group to find the Client Id and to create a secret.

![ADF App ID](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_app_id.png)

Click on  'Certificates & Secretes' to create a Client Secret for your application. Once there click on 'New client secret' to create a client secret which will be used to connect Data Factory in Airflow.

![ADF Client Secret](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_client_secret.png)

Once you have a Client ID and Secret you need to connect the your API key to the your Data Factory instance. To do this go back to the overview of your Data Factory and click Access Control. Once there click on 'Add role assignments' to add your Application(API) as a contributor to the Data Factory.

![ADF Access Control](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_add_role_assignment.png)

Next a screen asking you to add a role assignment will pop up. Add the following settings:

- Role: Contributor
- Assign access to: User, group, or service principal

Next search for your app (`david-astro` in this example), add it to 'Selected members' and click save.

![ADF Role Assignment](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_add_role_assignment2.png)

Now you should be able to connect to your Data Factory from Airflow using your Client ID and Client Secret.

Additional detail on requirements for interacting with Azure Data Factory using the REST API can be found [here](https://docs.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-rest-api). You can also see [this link](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal) for more information on creating a registered application in Azure Active Directory

### Create a DAG to Orchestrate ADF Jobs

Now that our ADF pipelines are runnable, we create a DAG that executes those pipelines using Azure provider modules. The DAG below executes two ADF pipelines in parallel (tasks `run_pipeline1` and `run_pipeline2`). It then uses an `AzureDataFactoryPipelineRunStatusSensor` to wait until "pipeline2" has completed before finishing the DAG.

```python
from datetime import datetime, timedelta

from airflow.models import DAG, BaseOperator

try:
    from airflow.operators.empty import EmptyOperator
except ModuleNotFoundError:
    from airflow.operators.dummy import DummyOperator as EmptyOperator
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.providers.microsoft.azure.sensors.data_factory import AzureDataFactoryPipelineRunStatusSensor
from airflow.utils.edgemodifier import Label

with DAG(
    dag_id="example_adf_run_pipeline",
    start_date=datetime(2021, 8, 13),
    schedule_interval="@daily",
    catchup=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=3),
        "azure_data_factory_conn_id": "azure_data_factory",
        "factory_name": "my-data-factory",  # This can also be specified in the ADF connection.
        "resource_group_name": "my-resource-group",  # This can also be specified in the ADF connection.
    },
    default_view="graph",
) as dag:
    begin = EmptyOperator(task_id="begin")
    end = EmptyOperator(task_id="end")

    # [START howto_operator_adf_run_pipeline]
    run_pipeline1: BaseOperator = AzureDataFactoryRunPipelineOperator(
        task_id="run_pipeline1",
        pipeline_name="pipeline1",
        parameters={"myParam": "value"},
    )
    # [END howto_operator_adf_run_pipeline]

    # [START howto_operator_adf_run_pipeline_async]
    run_pipeline2: BaseOperator = AzureDataFactoryRunPipelineOperator(
        task_id="run_pipeline2",
        pipeline_name="pipeline2",
        wait_for_termination=False,
    )

    pipeline_run_sensor: BaseOperator = AzureDataFactoryPipelineRunStatusSensor(
        task_id="pipeline_run_sensor",
        run_id=run_pipeline2.output["run_id"],
    )
    # [END howto_operator_adf_run_pipeline_async]

    begin >> Label("No async wait") >> run_pipeline1
    begin >> Label("Do async wait with sensor") >> run_pipeline2
    [run_pipeline1, pipeline_run_sensor] >> end
```

![Graph View](https://assets2.astronomer.io/main/guides/azure-data-factory/multiple_adf_pipeline_graph.png)

Note that this DAG requires an Airflow connection (`azure_data_factory`) to connect to your Azure instance and ADF. The connection requires the following information:

- Tenant ID 
- Subscription ID
- Resource Group
- Factory
- Client ID
- Client secret

They should be entered into the connection form like this:

![Airflow ADF Connection](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_airflow_connection.png)

The Client ID is the login, Client Secret is the password, and the rest are JSON-formatted extras.

For a more complex example of orchestrating dependent ADF pipelines with Airflow, check out [this example](https://registry.astronomer.io/dags/airflow-azure-data-factory) on the Astronomer Registry.
