---
title: "Orchestrating Azure Container Instances with Airflow"
description: "Orchestrating containers with Azure Container Instances from your Apache Airflow DAGs."
date: 2020-12-21T00:00:00.000Z
slug: "airflow-azure-container-instances"
tags: ["Integrations", "Azure", "DAGs"]
---

> Note: All code in this guide can be found in [this Github repo](https://github.com/astronomer/azure-operator-tutorials).

## Overview

[Azure Container Instances](https://azure.microsoft.com/en-us/services/container-instances/) (ACI) is one service that Azure users can leverage for working with containers. In this guide we'll cover the high level concepts of how to orchestrate ACI using Airflow and walk through an example DAG.

## Orchestrating ACI with Airflow

### The Azure Container Instances Operator

The easiest way to orchestrate Azure Container Instances with Airflow is to use the [AzureContainerInstancesOperator](https://airflow.apache.org/docs/apache-airflow/stable/_modules/airflow/contrib/operators/azure_container_instances_operator.html). This operator starts a container on ACI, runs the container, and terminates the container when all processes are completed. 

The only prerequisites for using this operator are:

- An Azure account with a resource group created
- An Azure Service Principle that has write permissions over that resource group
- A docker image to use for the container (either publicly or privately available)

Note that this operator can also be used to run existing container instances and make certain updates, including the docker image, environment variables, or commands. Some updates to existing container groups are not possible with the operator, including CPU, memory, and GPU; these updates require deleting the existing container group and recreating it, which can be accomplished using the [AzureContainerInstanceHook](https://github.com/apache/airflow/blob/master/airflow/providers/microsoft/azure/hooks/azure_container_instance.py).

### When to use ACI

There are multiple ways to work with containers with Airflow on Azure, each of which could be the right fit from your use case. The most flexible and scalable method would be to the [KubernetesPodOperator](https://airflow.apache.org/docs/apache-airflow/stable/kubernetes.html). This will not only let you run any container with Airflow, but also run it as a Kubernetes pod, which allows you to pass in resource requests and other Kubernetes native parameters. However, it requires an [AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/) cluster (or a hand rolled Kubernetes cluster).

If you are not running on [AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/), ACI can be a great choice:

- It requires very little setup, and is easy to use
- It allows you to run containers in different regions
- It is typically the cheapest; since no virtual machines or higher-level services are required, **you only pay for the memory and CPU used by your container group while it is active.**
- Unlike the [DockerOperator](https://airflow.apache.org/docs/apache-airflow/1.10.4/_api/airflow/operators/docker_operator/index.html), it does not require running a container on the host machine

With this in mind, we would recommend using ACI with the AzureContainerInstancesOperator for testing or for light weight tasks that don't require scaling. For heavy production workloads, we would recommend sticking with AKS and the KubernetesPodOperator.

## Example

Using Airflow to create and run an ACI is straight forward. First, identify the Azure resource group you want to create the ACI in (or create a new one); then ensure your Azure instance has a service principle with write access over that resource group. For more information on setting this up, see this [link](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal).

Next, create an Airflow connection with the type `Azure Container Instance`, and fill it out with your Client ID as the login, Client Secret as the password, and Tenant ID and Subscription ID in the extra's field as json. It should look something like this:

![ACI Connection](https://assets2.astronomer.io/main/guides/azure-container-instances/aci_connection.png)

Next, define a DAG using the AzureContainerInstancesOperator:

```python
from airflow import DAG
from airflow.providers.microsoft.azure.operators.azure_container_instances import AzureContainerInstancesOperator
from datetime import datetime, timedelta

# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG('azure_container_instances',
         start_date=datetime(2020, 12, 1),
         max_active_runs=1,
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False
         ) as dag:

    opr_run_container = AzureContainerInstancesOperator(
        task_id='run_container',
        ci_conn_id='azure_container_conn_id',
        registry_conn_id=None,
        resource_group='adf-tutorial',
        name='azure-tutorial-container',
        image='hello-world:latest',
        region='East US',
        cpu=1,
        memory_in_gb=1.5,
        fail_if_exists=False

    )
```

The parameters for the operator are:

- **ci_conn_id:** the connection ID for the connection we created above
- **registry_conn_id:** the connection ID to connect to a registry. In this case we used DockerHub, which is public and does not require credentials, so we pass in `None`
- **resource_group:** our Azure resource group
- **name:** the name we want to give our ACI. Note that this must be unique within the resource group
- **image:** the docker image we want to use for the container. In this case we use a simple Hello World example from Docker
- **region:** the Azure region we want our ACI deployed to
- **CPU:** the number of CPUs to allocate to the container. In this case we have used the default minimum for example. For more information on allocating CPU and memory, see this [link](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-faq).
- **memory_in_gb**: the amount of memory to allocate to the container. In this case we have used the default minimum for example.
- **fail_if_exists:** whether we want the the operator to raise an exception if the container group already exists (defaults to True). If set to False and the container group name already exists within the given resource group, the operator will attempt to update the container group based on the other parameters before running and terminating upon completion.

Note that you can also provide the operator with other parameters such as environment variables, volumes, and a command as needed to run the container.

Now if we run this DAG, an ACI will spin up, run the container with the Hello World image, and then spin down. If we look at the Airflow task log, we see the printout from the container has propagated to the logs:

![ACI Task Log](https://assets2.astronomer.io/main/guides/azure-container-instances/aci_task_log.png)

From here we can build out our DAG as needed with any other dependent or independent tasks.
