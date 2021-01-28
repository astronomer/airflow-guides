---
title: "Executing Azure Data Factory Pipelines with Airflow"
description: "Triggering remote jobs in Azure Data Factory from your Apache Airflow DAGs."
date: 2020-12-09T00:00:00.000Z
slug: "airflow-azure-data-factory-integration"
tags: ["Integrations"]
---

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/airflow-azure-data-factory-tutorial).

## Overview

Azure Data Factory (ADF) is a commonly used service for constructing data pipelines and jobs. With a little preparation, it can be used in combination with Airflow to leverage the best of both tools. Here we'll discuss why you might want to use these two tools together, how Airflow can be used to execute ADF jobs, and a simple example tutorial showing how it all fits together.

## Why Use Airflow with ADF

ADF is an easy to learn tool that allows you to quickly create jobs without writing tons of code. It integrates seamlessly with on-prem data sources and other Azure services. However, it has some disadvantages when used alone - namely: 

- Building and integrating custom tools can be difficult
- Integrations with services outside of Azure are limited
- Orchestration capabilities are limited
- Custom packages and dependencies can be complex to manage

That's where Airflow comes in. ADF jobs can be run using an Airflow DAG, giving the full capabilities of Airflow orchestration beyond using ADF alone. This allows users that are comfortable with ADF to write their job there, while Airflow acts as the control plane for orchestration.

## How to Execute ADF Pipelines with Airflow

Operators and hooks are the main building blocks of Airflow, and both can be used easily to execute, or interact with, an ADF pipeline.

### Hooks

We recommend using Airflow hooks when interacting with any external system. Hooks are used as a way to abstract the methods you would use against a source system. Airflow does not currently have built-in hooks for ADF, but they have been developed and can be found on [Github](https://github.com/flvndh/airflow/blob/issue/10995/azure-data-factory/airflow/providers/microsoft/azure/hooks/azure_data_factory.py). 


It is likely that these will be merged into the Airflow project soon, but in the meantime, you can always import them separately, which is what we do in the example below. 

These hooks build off of the `azure-mgmt-datafactory` Python package; since this is used under the hood, [this](https://docs.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-python) resource on interacting with ADF using Python could be helpful for determining parameter names, etc.


It is worth noting that you could also use the ADF API directly to run a pipeline or perform some other operations. Even though we don't recommend this method over using hooks, it is still helpful to understand how the [API](https://docs.microsoft.com/en-us/rest/api/datafactory/v1/data-factory-data-factory) works when developing a DAG that interacts with ADF since the API is used under the hood.


### Operators

There is currently no published Azure Data Factory operator, although given that hooks have been developed we expect that an operator will not be far behind. You could make your own ADF operator that builds off of the hooks mentioned above. Or you can use the PythonOperator and build your own function that suits your use case; this is the method we show in the example below.

## Example

### Create an ADF Pipeline

To create an ADF Pipeline you will need to create a Data Factory resource in your resource group. To do this go to your resources group or create a new resource group from your Azure Portal. Once in the resource group click 'add resource' and search for Data Factory. Once the resource is created click on the resource to get an overview of the current runs. Next click on 'Author and Monitor' to create or own pipeline.

![ADF Author Pipeline](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_pipeline_author.png)

Once in 'Author and Monitor' you can create a pipeline from a variety of options or watch tutorials. If it's your first ADF pipeline either watch a tutorial or create a pipeline from a template. In the example shown the 'Copy from REST or HTTP using OAuth' template was used. This template creates a [Copy Activity](https://docs.microsoft.com/en-us/azure/data-factory/copy-activity-overview) pipeline that gets data from a REST API and saves it in the storage system of your choice. 

![ADF Rest API Activity](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_rest_api.png)

In the example pipeline shown below there are 5 Copy Activities that each request Covid-19 data for 5 different states from a [REST API](https://covidtracking.com/data/api) and stores the data in Azure Blob storage. The pipeline has one parameter `date` which allows a user to enter a date for when they want the data. 

![ADF Pipeline Parameters](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_pipeline_param.png)

Once you have built a pipeline like the one above you can enter a parameter and run the pipeline. You can find more information on creating a data pipeline at this [doc](https://docs.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-portal).

### Make your ADF Pipeline Runnable

Next, to make your ADF pipeline accessible by Airflow you will need to register an App with Azure Active Directory to get a Client ID and Client Secret (API Key) for your Data Factory. First go to Azure Active Directory and click on 'Registered Apps' to see a list of registered apps. If you created a Resource group you should already have an app registered with the same name. 

![ADF App Registration](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_app_registration.png)

Once there click on the app associated with your resource group to find the Client Id and to create a secret. 

![ADF App ID](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_app_id.png)

Click on  'Certificates & Secretes' to create a Client Secret for your application. Once there click on 'New client secret' to create a client secret which will be used to connect Data Factory in Airflow. 

![ADF Client Secret](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_client_secret.png)

Once you have a Client ID and Secret you need to connect the your API key to the your Data Factory instance. To do this go back to the overview of your Data Factory and click Access Control. Once there click on 'Add role assignments' to add your Application(API) as a contributor to the Data Factory. 

![ADF Access Control](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_add_role_assignment.png)

Next a screen asking you to add a role assignment will pop up. Add the following settings:

Role: Contributor

Assign access to: User, group, or service principal

Next search for your app ('david-astro' in this example), add it to 'Selected members' and click save. 

![ADF Role Assignment](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_add_role_assignment2.png)

Now you should be able to connect to your Data Factory from Airflow using your Client ID and Client Secret. 

Additional detail on requirements for interacting with Azure Data Factory using the REST API can be found [here](https://docs.microsoft.com/en-us/azure/data-factory/quickstart-create-data-factory-rest-api). You can also see [this link](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal) for more information on creating a registered application in Azure Active Directory

### Create a DAG to run the ADF job

Now that we have an existing ADF job that should be runnable externally to Azure, we will create a DAG that will execute that pipeline with parameters we pass in. Let's say in this scenario we want to create a DAG that will execute the pipeline described above for yesterday's date, so that we grab recent Covid data and drop it in our file storage.

As mentioned above, we will use the ADF hooks already developed with the PythonOperator. The DAG code is straight forward:

```python
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from hooks.azure_data_factory_hook import AzureDataFactoryHook

azure_data_factory_conn = 'azure_data_factory_conn'

#Get yesterday's date, in the correct format
yesterday_date = '{{ yesterday_ds_nodash }}'

def run_adf_pipeline(pipeline_name, date):
    '''Runs an Azure Data Factory pipeline using the AzureDataFactoryHook and passes in a date parameter
    '''
    
    #Create a dictionary with date parameter 
    params = {}
    params["date"] = date

    #Make connection to ADF, and run pipeline with parameter
    hook = AzureDataFactoryHook(azure_data_factory_conn)
    hook.run_pipeline(pipeline_name, parameters=params)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

with DAG('azure_data_factory',
         start_date=datetime(2019, 1, 1),
         max_active_runs=1,
         schedule_interval=timedelta(minutes=30), 
         default_args=default_args,
         catchup=False
         ) as dag:

         opr_run_pipeline = PythonOperator(
            task_id='run_pipeline',
            python_callable=run_adf_pipeline,
            op_kwargs={'pipeline_name': 'pipeline1', 'date': yesterday_date}
         )
```

There are a few important things to note about this DAG: 

- We have used the ADF hook code from the Github link above and brought it locally, imported as `AzureDataFactoryHook`. Your import path may vary.
- The `run_pipeline` task uses the PythonOperator that looks for the `pipeline_name` parameter and a date. If you have other pipelines you want to execute in the same DAG, you can add additional tasks in the same manner.
- This DAG requires an Airflow connection (`azure_data_factory_conn`) to connect to your Azure instance and ADF factory. The connection requires your Tenant ID, Subscription ID, Resource Group, Factory, Client ID, and Client secret. They should be entered into the connection like this:

![Airflow ADF Connection](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_airflow_connection.png)

The Client ID is the login, Client Secret is the password, and the rest are JSON-formatted extras. Note that the 'Azure Data Lake' connection type is chosen because there is not currently an ADF option; this is arbitrary, and the connection type could be anything as long as the correct fields are available.

Once everything is set up, executing the pipeline is as simple as triggering the DAG. We can see the successful DAG run:

![ADF DAG Graph View](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_dag_graph_view.png)

And the pipeline run on the Azure side:

![ADF Pipeline Run](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_pipeline_run.png)

And yesterday's file in the file storage:

![Azure Blob Loaded Files](https://assets2.astronomer.io/main/guides/azure-data-factory/adf_loaded_files.png)

And now that we have a DAG that can execute the ADF pipeline, we can easily add any other tasks or notifications we need leveraging Airflow's capabilities.
