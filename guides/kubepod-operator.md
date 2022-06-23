---
title: "KubernetesPodOperator on Astronomer"
description: "Use the KubernetesPodOperator on Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "kubepod-operator"
heroImagePath: null
tags: ["Kubernetes", "Operators"]
---

## Overview

The [KubernetesPodOperator](https://registry.astronomer.io/providers/kubernetes/modules/kubernetespodoperator) (KPO) is an operator from the Kubernetes provider package designed to provide a straightforward way to execute a task in a Kubernetes Pod from your Airflow environment. In a nutshell the KPO is an abstraction over a call to the Kubernetes API to launch a pod.

In this guide we will list the requirements to run the KubernetesPodOperator, explain when to use it and cover its most important arguments, as well as the difference between the KPO and KubernetesExecutor. At the end of the guide we will provide two step-by-step examples on how to launch a pod within the same and within a different cluster.

> **Note**: Kubernetes is a powerful tool for Container Orchestration with complex functionality. If you are unfamiliar with Kubernetes we recommend taking a look at the [Kubernetes 101 Guide](https://www.astronomer.io/guides/intro-to-kubernetes/) to get a general overview. For in-depth information check out the [Kubernetes Documentation](https://kubernetes.io/docs/home/).  

> **Note**: If you are using [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/) consider using [GKEStartPodOperator](https://registry.astronomer.io/providers/google/modules/gkestartpodoperator).

## Requirements to use the KubernetesPodOperator

To use the KubernetesPodOperator it is necessary to install the Kubernetes provider package.

```bash
pip install apache-airflow-providers-cncf-kubernetes==<version>
```

Required versions of the `apache-airflow`, `cryptography` and `kubernetes` packages for specific versions of the Kubernetes provider package are listed in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/index.html#requirements).

You will also need an existing Kubernetes cluster to connect to. It is _not_ necessary to use the Kubernetes Executor in order to use the KPO. You may use any of the following executors: `CeleryExecutor`, `KubernetesExecutor`, [`CeleryKubernetesExecutor`](https://airflow.apache.org/docs/apache-airflow/2.0.0/executor/celery_kubernetes.html). When using Celery remember to install its [provider](https://registry.astronomer.io/providers/celery).

> **Note**: On Astro the infrastructure needed to run KPO with CeleryExecutor is pre-built into every Cluster. Astronomer provides [comprehensive documentation on using KPO on Astro](https://docs.astronomer.io/astro/kubernetespodoperator).  

### KubernetesPodOperator in local development

There are several ways in which the KubernetesPodOperator can be run in local development. For users of the Astro CLI there is a [step-by-step tutorial](https://docs.astronomer.io/software/kubepodoperator-local) available in the Astro Documentation, which can also be adapted for other dockerized Airflow setups.

It is also possible to run Open Source Airflow within a local Kubernetes Cluster using the [Helm Chart for Apache Airflow](https://airflow.apache.org/docs/helm-chart/stable/index.html). For a walkthrough of this setup you can refer to the recording of the [Getting Started With the Official Airflow Helm Chart Webinar](https://www.youtube.com/watch?v=39k2Sz9jZ2c&ab_channel=Astronomer).

When running Airflow in a Kubernetes cluster using the KPO operator does not require further configuration beyond leaving the setting `in_cluster` on `True` to run a new pod within the same cluster.

## When to use the KubernetesPodOperator

The KubernetesPodOperator runs any Docker image provided to it, whether they are pulled from [DockerHub](https://hub.docker.com/) or from private repositories. Frequent use cases are:

- Running a task better described in a language other than Python.
- Having full control over how much compute resources and memory a single task can use.
- Executing tasks in an separate environment with individual packages and dependencies.

Sometimes you may want to run pods on different clusters, for example if only some need GPU resources while others do not. This is also possible with the KPO and a step-by-step example is provided at the end of this guide.

### KubernetesPodOperator vs KubernetesExecutor

SECTION INCOMPLETE

In Airflow you have the option to choose between a variety of [executors](https://www.astronomer.io/guides/airflow-executors-explained) which determine how your Airflow tasks will be executed.

The [KubernetesExecutor](https://airflow.apache.org/docs/apache-airflow/stable/executor/kubernetes.html) and the KubernetesPodOperator both dynamically launch and terminate Pods to run Airflow tasks in. As the names suggest, KubernetesExecutor is an executor, which means it affects how all tasks in an Airflow instance are executed while the KubernetesPodOperator is an operator defining that a single task is to be launched in a Kubernetes pod with the given configuration, which does not affect any other tasks in the Airflow instance.

Compared to the KPO the KubernetesExecutor:

- is set at the configuration level of the Airflow instance, which means _all_ tasks will each be run in their own Kubernetes pod.
- has less abstraction over pod configuration. All configurations have to be passed in as a dictionary via the argument `executor_config`.
- creates a new field in the view of individual task instances in the Airflow UI `K8s Pod Spec` which shows the specifications of the pod that was run.
- can only use Docker images that have Airflow installed, otherwise they will not be able to run the task. This is not the case with the KPO, which can run any valid Docker image.

## How to configure the KubernetesPodOperator

In this section we will list some of the parameters of the KubernetesPodOperator, for concrete use cases see section 'When to use the KPO' earlier in this guide. The KPO launches any valid Docker Image provided to it (`image`) in a new Kubernetes Pod on an existing Kubernetes cluster. The many other parameters available to the user are all specifications of the pod configuration which the KPO translates into a call to the [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/). The KubernetesPodOperator offers full access to KubernetesAPI functionality relating to pod creation.    

The KubernetesPodOperator can be instantiated like any other Operator within the context of a DAG. It can run with only a few arguments being mandatory. In fact the KPO will run a new pod in the same cluster with only the following arguments supplied:

- `task_id`: a unique string identifying the task within Airflow.
- `namespace`: the namespace within your Kubernetes cluster the new pod should be assigned to.
- `name`: the name of the pod created. This name needs to be unique for each pod within a namespace.
- `image`: a Docker image to launch. Images from [hub.docker.com](https://hub.docker.com/) can be passed in with just the image name, custom repositories have to be given as full URLs.

Of course the pod created can be configured further, some of the most commonly used arguments are:

- `random_name_suffix`: generates a random suffix for the pod name if set to `True`. Avoids naming conflicts when running a large number of pods.
- `labels`: add key:value pairs to the pod which can be used to logically group decoupled objects together.
- `ports`: provides the possibility to override default ports for the pod.
- `reattach_on_restart`: defines how to handle losing the worker while the pod is running, by default (`True`) the existing pod will reattach to the worker on the next try. `False` creates a new pod for each try.
- `is_delete_operator_pod`: `True` by default, will delete the pod when it reaches its final state or when the execution is interrupted.
- `get_logs`: provides the `stdout` of the container as task-logs to the Airflow logging system.
- `log_events_on_failure`: if set to `True` events will be logged in case the pod fails (default: `False`).

As shown in 'Example: Spin up a pod in the same cluster' below, you can define an entrypoint (`cmds`) and its arguments (`arguments`) for your container, these two fields can be used with Jinja templates.

> **Note**: The following KPO arguments can be used with Jinja templates: image, cmds, arguments, env_vars, labels, config_file, pod_template_file and namespace.

To specify environment variables for a pod it is possible to use the argument `env_vars` for individual variables or pass in a [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) via `volumes`.

Management of distributed resources and balancing of workloads are some of the core functionalities of Kubernetes. The [Kubernetes Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) on the Kubernetes Control Plane matches each pod to the best physical or virtual machine (called Node in Kubernetes) possible. When using the KPO there are multiple ways to add information configuring this process:

- `resources`: allows the user to pass a dictionary with resource requests (keys: `request_memory`, `request_cpu`) and limits (keys: `limit_memory`, `limit_cpu`, `limit_gpu`). See the [Kubernetes Documentation on Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) for more information.
- `node_selectors`, `affinity` and `tolerations` are ways to further specify rules for [pod to node assignment](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/).

To pass small amounts of information between tasks Airflow uses [XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html). It is possible to push content from the container within a pod, specifically from the file `/airflow/xcom/return.json`, by setting the KPO argument `do_xcom_push` to `True`. Please remember that the `return.json` file does not exist and `do_xcom_push` to `True` will cause a task to fail if the file has not been created by the user via the Docker image.

> **Note**: Many more arguments are available to customize the KubernetesPodOperator further. For a complete and up to date list see the [KubernetesPodOperator source code](https://github.com/apache/airflow/blob/main/airflow/providers/cncf/kubernetes/operators/kubernetes_pod.py).

### Configuring Kubernetes Connection

The KubernetesPodOperator uses the [Kubernetes Hook](https://registry.astronomer.io/providers/kubernetes/modules/kuberneteshook) to connect to the [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/) of a Kubernetes cluster. The KPO has 4 parameters pertaining to the Kubernetes Connection:

- `kubernetes_conn_id`: uses a [connection](https://www.astronomer.io/guides/connections) stored in the [Airflow metadata database](https://www.astronomer.io/guides/airflow-database), which can be configured in the Airflow UI under **Admin** -> **Connections**.
- `in_cluster`: by default set to `True`, which means the new pod will be spun up in the same cluster, you are running your Airflow instance in.
- `config_file`: The path to the Kubernetes config file. If not specified, default value is `~/.kube/config`.
- `cluster_context`: is used to specify a context that points to a Kubernetes cluster when `in_cluster` is set to `False`. This parameter is used to select a specific cluster if several are defined within your config file.

The `kubernetes_conn_id` is the preferred way of setting up your Kubernetes connection. `in_cluster`, `cluster_context` and the path to the `config_file` can be set within your connection and overwritten by using the parameters in the KPO. Setting these parameters at the level of `airflow.cfg` has been deprecated.

### Example: Using KubernetesPodOperator to run a script in Haskell

A frequent use case for the KubernetesPodOperator is to run scripts in languages other than Python. For this purpose a custom Docker Image has to be build and either run a public or private [DockerHub repository]((https://docs.docker.com/docker-hub/repos/).

> **Note**: Astro provides documentation on [how to run images from private repositories](https://docs.astronomer.io/astro/kubernetespodoperator).

The code below shows a Haskell script which takes the environment variable `NAME_TO_GREET` and prints a message containing it to the console:

```haskell
import System.Environment

main = do
        name <- getEnv "NAME_TO_GREET"
        putStrLn ("Hello, " ++ name)
```

The Dockerfile uses `cabal` as a system for building and packaging Haskell programs, for this example the `haskell_example.cabal` file built automatically when running `cabal init` in a directory name `haskell_example` is sufficient.

```Dockerfile
FROM haskell
WORKDIR /opt/hello_name
RUN cabal update
COPY ./haskell_example.cabal /opt/hello_name/haskell_example.cabal
RUN cabal build --only-dependencies -j4
COPY . /opt/hello_name
RUN cabal install
CMD ["haskell_example"]
```

After making the Docker image available it is possible to pull it into the KPO via the `image` argument. The example DAG below showcases a variety of arguments of the KubernetesPodOperator including how to pass the an environment variable `NAME_TO_GREET` which can be used from within the Haskell code.

```python
from airflow import DAG
from datetime import datetime
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.configuration import conf

## get the current Kubernetes namespace Airflow is running in
namespace = conf.get("kubernetes", "NAMESPACE")

name = 'your_name'

## instatiate the DAG
with DAG(
    start_date=datetime(2022,6,1),
    catchup=False,
    schedule_interval='@daily',
    dag_id='KPO_different_language_example'
) as dag:

    say_hello_name_in_haskell = KubernetesPodOperator(
        ## operator specific argument
        # unique id of the task within the DAG
        task_id='say_hello_name_in_haskell',

        ## arguments pertaining to the image and commands executed
        # the Docker Image to launch
        image='<image location>',

        ## arguments pertaining to where the pod is launched
        # launch the pod on the same cluster as Airflow is running on
        in_cluster=True,
        # launch the pod in the same namespace as Airflow is running in
        namespace=namespace,

        ## pod configuration
        # name the pod
        name='my_pod',
        # give the pod name a random suffix, ensure uniqueness in the namespace
        random_name_suffix=True,
        # attach labels to the pod, can be used for grouping
        labels={'app':'backend', 'env':'dev'},
        # reattach to worker instead of creating a new pod on worker failure
        reattach_on_restart=True,
        # delete pod after the task is finished
        is_delete_operator_pod=True,
        # log stdout of the container as task logs
        get_logs=True,
        #log events in case of pod failure
        log_events_on_failure=True,
        # passes your name as an environment var
        env_vars={"NAME_TO_GREET": f"{name}"}
        )
```

## KubernetesPodOperator best practices

SECTION INCOMPLETE

Suggestions from issues:  

- CI/CD guidelines (such as you need to be pushing updates to the KPO image)
- make sure each KPO image update has a unique tag
Some advice on where to store the images such that they can be retrieved on Astro
- how to best set env variables

## Example: Using the KubernetesPodOperator with XComs

[XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html) is a commonly used way to pass small amounts of data between tasks. It is possible to use this feature with the KPO both for it to receive values stored in XCom and push to XComs itself.

The DAG below shows a straightforward ETL pipeline with an `extract_data` task simulating for example running a query on a database and returning one value that by being returned from the Python function is automatically pushed to XComs thanks to the [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html#tutorial-on-the-taskflow-api).  

The `transform` task is a KubernetesPodOperator which launches an image having been built with the following Dockerfile:

```dockerfile
FROM python

WORKDIR /

RUN mkdir -p airflow/xcom         
RUN echo "" > airflow/xcom/return.json

COPY multiply_by_23.py ./

CMD ["python", "./multiply_by_23.py"]
```

It is especially important to make sure to create the file `airflow/xcom/return.json` because Airflow will look for XComs to pull only there. The image also contains a simple Python script to multiply an environment variable by 23, package it in a json and write that json to the correct file.

```python
import os

# import the result of the previous task as an environment variable
data_point = os.environ['DATA_POINT']
multiplied_data_point = 23 * int(data_point)

# multiply the data point by 23 and package the result into a json
multiplied_data_point = str(23 * int(data_point))
return_json = {"return_value":f"{multiplied_data_point}"}

# write to the file checked by airflow for XComs
f = open('./airflow/xcom/return.json', 'w')
f.write(f"{return_json}")
f.close()
```

Lastly the `load_data` task pulls the XCom returned from the `transform` task and prints it to the console.


```python
from airflow import DAG
from datetime import datetime
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.configuration import conf
from airflow.decorators import task

import random

# get the current Kubernetes namespace Airflow is running in
namespace = conf.get("kubernetes", "NAMESPACE")

# instatiate the DAG
with DAG(
    start_date=datetime(2022,6,1),
    catchup=False,
    schedule_interval='@daily',
    dag_id='KPO_example_DAG'
) as dag:

    @task
    def extract_data():
        data_point = random.randint(0,100)
        return data_point

    transform = KubernetesPodOperator(
        # operator specific argument
        task_id='transform',

        # arguments pertaining to the image and commands executed
        image='< image location >', # the Docker Image to launch

        # arguments pertaining to where the pod is launched
        in_cluster=True, # launch the pod on the same cluster as Airflow is running on
        namespace=namespace, # launch the pod in the same namespace as Airflow is running in

        # pod configuration
        name='my_pod', # naming the pod
        get_logs=True, # log stdout of the container as task logs
        log_events_on_failure=True, #log events in case of pod failure
        env_vars={"DATA_POINT": "{{ ti.xcom_pull(task_ids='extract_data', key='return_value') }}"},
        do_xcom_push=True #push the contents from xcom.json to xcoms
        )

    @task
    def load_data(**context):
        transformed_data_point = context['ti'].xcom_pull(task_ids='extract_data', key='return_value')
        print(transformed_data_point)

    extract_data() >> transform >> load_data()
```

## Example: Spinning up a pod in EKS from Airflow

SECTION INCOMPLETE

If some of your tasks require specific resources like a GPU you may want to run them in a different cluster than your Airflow Instance. In setups where both clusters are used by the same AWS or GCP account this can be managed with roles and permissions. There is also the possibility to use a CI account and enable [cross-account access to AWS EKS cluster resources](https://aws.amazon.com/blogs/containers/enabling-cross-account-access-to-amazon-eks-cluster-resources/).  

The example below shows the steps to take to set up an EKS cluster on AWS and run a pod on it from an Airflow instance if cross-account access is not feasible. After setup of the EKS cluster the `KubeConfig` as well as the `AWS Profile` have to be provided to Airflow to make the connection to the remote cluster.  

### Step 1: Set up an EKS cluster on AWS

To set up a new EKS cluster on AWS you first need to create an IAM role with suitable permissions.
On AWS navigate to **Identity and Access Management (IAM)** -> **Roles** -> **Create role**. Select AWS service and `EKS` from the dropdown menu as well as `EKS - Cluster`. Make sure to give the role a unique name and to add the permission policies `AmazonEKSWorkerNodePolicy`, `AmazonEKS_CNI_Policy` and `AmazonEC2ContainerRegistryReadOnly`.

Edit the trust policy (**IAM** -> **Roles** -> role name) of this new role to include your account and necessary AWS Services:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<aws account id>:root",
        "Service": [
              "ec2.amazonaws.com",
              "eks.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Add the new role to your local AWS credentials file by default found at `~/.aws/config`.

```text
[default]
region = <your region>

[profile eksClusterRole]
role_arn = <EKS role arn>
source_profile = <your username>
```

Make sure your credentials in `~/.aws/credentials` are using a valid and active key for your username (keys can be generated at **IAM** -> **Users** -> your user -> **Security Credentials**).

Make a copy of `~/.aws` available to your Airflow environment (for Astro users: copy it into the `include` folder).

Lastly, create a new EKS cluster (**EKS** -> **Clusters** -> **Add cluster**) and assign the the newly created role to it. The cluster might take a few minutes to become active.

### Step 2 Retrieve the KubeConfig file from the EKS cluster

To be able to remotely connect to the newly created EKS cluster the KubeConfig file is needed. It can be retrieved by running:

```bash
aws eks --region region update-kubeconfig --name cluster_name
```

The command above will copy information into your existing `KubeConfig` file at `~/.kube/config`. Select the information pertaining to your EKS cluster and make it available to your Airflow environment (for Astro users: copy it into the `include` folder). It should have the following structure:

```text
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <key>
    server: <address of your EKS server>
  name: <arn of your EKS server>
contexts:
- context:
    cluster: <arn of your EKS server>
    user: <arn of your EKS server>
  name: <arn of your EKS server>
current-context: <arn of your EKS server>
kind: Config
preferences: {}
users:
- name: <arn of your EKS server>
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      args:
      - --region
      - < your region>
      - eks
      - get-token
      - --cluster-name
      - < your cluster name>
      command: aws
```

### Step 3 Add a namespace and service account to the EKS Cluster

It is best practice to use a new namespace for all pods sent to the EKS cluster from the Airflow environment and a separate service account.  

```bash
# create a new namespace on the EKS cluster
kubectl create namespace airflow-kpo-default

# create a new service account in your namespace using the namespace of
# your Airflow Data Plane Cluster
kubectl create serviceaccount <your-namespace>-kpo -n airflow-kpo-default
```

### Step 4 Adjust Airflow configuration files

This step will differ depending on the Airflow setup. When running Airflow locally it is just necessary to make sure `awscli`, `apache-airflow-providers-cncf-kubernetes`,
and `apache-airflow-providers-amazon` are installed correctly on the local machine.

For dockerized settings add the following line to your Dockerfile:

```dockerfile
COPY --chown=astro:astro include/.aws /home/astro/.aws
```

Next you can add the AWS command line to your `packages.txt`, and the necessary provider packages to `requirements.txt`:

```text
awscli
```

```text
apache-airflow-providers-cncf-kubernetes
apache-airflow-providers-amazon
```

### Step 5 Add AWS connection ID

In the Airflow UI navigate to **Admin** -> **Connections** to set up the connection to the AWS account running the EKS. Chose a unique connection ID and use your `aws_access_key_id` as login and your `aws_secret_access_key` as password.

### Step 6 Add the DAG interacting with EKS  

If dynamic behavior of the EKS cluster is desired, e.g. nodes get created with specifications for a task and deleted after the task has run, it is necessary to use several classes from the Amazon provider package. The DAG below has 5 tasks. The first one creates a nodegroup according to the users' specifications and afterwards a sensor checks that the cluster is running correctly. The third tasks is the actual KubernetesPodOperator running any valid Docker image. Lastly the nodegroup gets deleted and the deletion gets verified.

```python
# import DAG object and utility packages
from airflow import DAG
from datetime import datetime
from airflow.configuration import conf

# import the KPO
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
                                                        KubernetesPodOperator)

# import EKS related packages from the Amazon Provider
from airflow.providers.amazon.aws.hooks.eks import EKSHook, NodegroupStates
from airflow.providers.amazon.aws.operators.eks import (
                      EKSCreateNodegroupOperator, EKSDeleteNodegroupOperator)
from airflow.providers.amazon.aws.sensors.eks import EKSNodegroupStateSensor

# custom class to create a nodegroup with Nodes on EKS
class EKSCreateNodegroupWithNodesOperator(EKSCreateNodegroupOperator):

    def execute(self, context):
        # instantiating an EKSHook on the basis of the AWS connection (Step 5)
        eks_hook = EKSHook(
            aws_conn_id=self.aws_conn_id,
            region_name=self.region,
        )

        # define the node group to create
        eks_hook.create_nodegroup(
            clusterName=self.cluster_name,
            nodegroupName=self.nodegroup_name,
            subnets=self.nodegroup_subnets,
            nodeRole=self.nodegroup_role_arn,
            scalingConfig={
                'minSize': 1,
                'maxSize': 1,
                'desiredSize': 1
            },
            diskSize=20,
            instanceTypes=['g4dn.xlarge'],
            amiType='AL2_x86_64_GPU',   # get GPU resources
            updateConfig={
                'maxUnavailable': 1
            },
        )

# instantiate the DAG
with DAG(
    start_date=datetime(2022,6,1),
    catchup=False,
    schedule_interval='@daily',
    dag_id='a_dag_in_k8s'
) as dag:

    # task 1 creates the nodegroup
    create_gpu_nodegroup=EKSCreateNodegroupWithNodesOperator(
        task_id='create_gpu_nodegroup',
        cluster_name='<your cluster name>',  
        nodegroup_name='gpu-nodes',
        nodegroup_subnets=['<your subnet>', '<your subnet>'],
        nodegroup_role_arn='<arn of your EKS role>',
        aws_conn_id='<your aws conn id>',
        region='<your region>'
    )

    # task 2 check for nodegroup status, if it is up and running
    check_nodegroup_status=EKSNodegroupStateSensor(
        task_id='check_nodegroup_status',
        cluster_name='<your cluster name>',
        nodegroup_name='gpu-nodes',
        mode='reschedule',
        timeout=60 * 30,
        exponential_backoff=True,
        aws_conn_id='<your aws conn id>',
        region='<your region>'
    )

    # task 3 the KPO running a task
    run_on_EKS=KubernetesPodOperator(
        task_id="run_on_EKS",
        cluster_context='<arn of your cluster>',
        namespace="airflow-kpo-default",
        name="example_pod",
        image='ubuntu',
        cmds=['bash', '-cx'],
        arguments=["echo hello"],
        get_logs=True,
        is_delete_operator_pod=False,
        in_cluster=False,
        config_file='/usr/local/airflow/include/config',
        startup_timeout_seconds=240
    )

    # task 4 deleting the nodegroup
    delete_gpu_nodegroup=EKSDeleteNodegroupOperator(
        task_id='delete_gpu_nodegroup',
        cluster_name='<your cluster name>',  
        nodegroup_name='gpu-nodes',
        aws_conn_id='<your aws conn id>',
        region='<your region>'
    )

    # task 5 checking that the nodegroup was deleted successfully
    check_nodegroup_termination=EKSNodegroupStateSensor(
        task_id='check_nodegroup_termination',
        cluster_name='<your cluster name>',
        nodegroup_name='gpu-nodes',
        aws_conn_id='<your aws conn id>',
        region='<your region>',
        mode='reschedule',
        timeout=60 * 30,
        target_state=NodegroupStates.NONEXISTENT
    )


    # setting the dependencies
    create_gpu_nodegroup >> check_nodegroup_status >> run_on_EKS
    run_on_EKS >> delete_gpu_nodegroup >> check_nodegroup_termination
```

troubleshoot KPO  
added
```
      - --profile
      - default
      command: aws
      interactiveMode: IfAvailable
      provideClusterInfo: false
```
