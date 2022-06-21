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

## Requirements to use KPO

To use the KubernetesPodOperator it is necessary to install the Kubernetes provider package.

```bash
pip install apache-airflow-providers-cncf-kubernetes==<version>
```

Required versions of the `apache-airflow`, `cryptography` and `kubernetes` packages for specific versions of the Kubernetes provider package are listed in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/index.html#requirements).

You will also need an existing Kubernetes cluster to connect to. It is _not_ necessary to use the Kubernetes Executor in order to use the KPO. You may use any of the following executors: `CeleryExecutor`, `KubernetesExecutor`, [`CeleryKubernetesExecutor`](https://airflow.apache.org/docs/apache-airflow/2.0.0/executor/celery_kubernetes.html). When using Celery remember to install its [provider](https://registry.astronomer.io/providers/celery).

> **Note**: On Astro the infrastructure needed to run KPO with CeleryExecutor is pre-built into every Cluster. Astronomer provides [comprehensive documentation on using KPO on Astro](https://docs.astronomer.io/astro/kubernetespodoperator).  

## When to use KPO

The KubernetesPodOperator runs any Docker image provided to it, whether they are pulled from [DockerHub](https://hub.docker.com/) or from private repositories. Frequent use cases are:

- Running a task better described in a language other than Python.
- Having full control over how much compute resources and memory a single task can use.
- Executing tasks in an separate environment with individual packages and dependencies.

Sometimes you may want to run pods on different clusters, for example if only some need GPU resources while others do not. This is also possible with the KPO and a step-by-step example is provided at the end of this guide.

## How to configure KPO

In this section we will list some of the parameters of the KubernetesPodOperator, for concrete use cases see the two examples at the end of this guide.

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

To specify environment variables for a pod it is possible to use the argument `env_vars` for individual variables or pass in a [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) via `volumes`.

Management of distributed resources and balancing of workloads are some of the core functionalities of Kubernetes. The [Kubernetes Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) on the Kubernetes Control Plane matches each pod to the best physical or virtual machine (called Node in Kubernetes) possible. When using the KPO there are multiple ways to add information configuring this process:

- `resources`: allows the user to pass a dictionary with resource requests (keys: `request_memory`, `request_cpu`) and limits (keys: `limit_memory`, `limit_cpu`, `limit_gpu`). See the [Kubernetes Documentation on Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) for more information.
- `node_selectors`, `affinity` and `tolerations` are ways to further specify rules for [pod to node assignment](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/).

To pass small amounts of information between tasks Airflow uses [XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html). It is possible to push content from the container within a pod, specifically from the file `/airflow/xcom/return.json`, by setting the KPO argument `do_xcom_push` to `True`.

> Note: Many more arguments are available to customize the KubernetesPodOperator further. For a complete and up to date list see the [KubernetesPodOperator source code](https://github.com/apache/airflow/blob/main/airflow/providers/cncf/kubernetes/operators/kubernetes_pod.py).

### Configuring Kubernetes Connection

The KubernetesPodOperator uses the [Kubernetes Hook](https://registry.astronomer.io/providers/kubernetes/modules/kuberneteshook) to connect to the [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/) of a Kubernetes cluster. The KPO has 4 parameters pertaining to the Kubernetes Connection:

- `kubernetes_conn_id`: uses a [connection](https://www.astronomer.io/guides/connections) stored in the [Airflow metadata database](https://www.astronomer.io/guides/airflow-database), which can be configured in the Airflow UI under **Admin** -> **Connections**.
- `in_cluster`: by default set to `True`, which means the new pod will be spun up in the same cluster, you are running your Airflow instance in.
- `config_file`: The path to the Kubernetes config file. If not specified, default value is `~/.kube/config`.
- `cluster_context`: is used to specify a context that points to a Kubernetes cluster when `in_cluster` is set to `False`. This parameter is used to select a specific cluster if several are defined within your config file.

The `kubernetes_conn_id` is the preferred way of setting up your Kubernetes connection. `in_cluster`, `cluster_context` and the path to the `config_file` can be set within your connection and overwritten by using the parameters in the KPO. Setting these parameters at the level of `airflow.cfg` has been deprecated.

## KPO vs KubernetesExecutor

In Airflow you have the option to choose between a variety of [executors](https://www.astronomer.io/guides/airflow-executors-explained) which determine how your Airflow tasks will be executed.

The [KubernetesExecutor](https://airflow.apache.org/docs/apache-airflow/stable/executor/kubernetes.html) and the KubernetesPodOperator both dynamically launch and terminate Pods to run Airflow tasks in. As the names suggest, KubernetesExecutor is an executor, which means it affects how all tasks in an Airflow instance are executed while the KubernetesPodOperator is an operator defining that a single task is to be launched in a Kubernetes pod with the given configuration, which does not affect any other tasks in the Airflow instance.

Compared to the KPO the KubernetesExecutor:

- is set at the configuration level of the Airflow instance, which means _all_ tasks will each be run in their own Kubernetes pod.
- has less abstraction over pod configuration. All configurations have to be passed in as a dictionary via the argument `executor_config`.
- creates a new field in the view of individual task instances in the Airflow UI `K8s Pod Spec` which shows the specifications of the pod that was run.
- can only use Docker images that have Airflow installed, otherwise they will not be able to run the task. This is not the case with the KPO, which can run any valid Docker image.

## KPO local development

There are several ways in which the KubernetesPodOperator can be run in local development. For users of the Astro CLI there is a [step-by-step tutorial](https://docs.astronomer.io/software/kubepodoperator-local) available in the Astro Documentation, which can also be adapted for other dockerized Airflow setups.

It is also possible to run Open Source Airflow within a local Kubernetes Cluster by following these steps:

- Install Docker, Docker Compose, Helm, kubectl and a service to create a local Kubernetes cluster like [KinD](https://kind.sigs.k8s.io/) or [Minikube](https://minikube.sigs.k8s.io/docs/).
- Create a local Kubernetes Cluster.
- Download and install the [Helm Chart for Apache Airflow](https://airflow.apache.org/docs/helm-chart/stable/index.html).
- To be able to use additional packages (e.g. Celery to use CeleryExecutor) build a custom Airflow Dockerfile.
- Add a possibility to deploy DAGs, for example using GitSync.
- Use kubectl to port-forward the Airflow webserver.

When running Airflow in a Kubernetes cluster using the KPO operator does not require further configuration beyond leaving the setting `in_cluster` on `True` to run a new pod within the same cluster.

## KPO best practices

SECTION INCOMPLETE

Suggestions from issues:  

- CI/CD guidelines (such as you need to be pushing updates to the KPO image)
- make sure each KPO image update has a unique tag
Some advice on where to store the images such that they can be retrieved on Astro
- how to best set env variables

## Example: Spinning up a pod in the same cluster

When Airflow is set up to run within a Kubernetes cluster, whether locally or in the cloud, using the KubernetesPodOperator is fairly simple. The parameter `in_cluster` will default to `True` and the KPO will run any pods within the same cluster and context as Airflow is already running in.

The DAG below contains one task using the KPO to execute a bash command within a new pod.

```python
from airflow import DAG
from datetime import datetime
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
                                                        KubernetesPodOperator)
from airflow.configuration import conf

# import the namespace from the airflow configuration
namespace = conf.get("kubernetes", "NAMESPACE")

# instantiate the DAG
with DAG(
    start_date=datetime(2022,6,1),
    catchup=False,
    schedule_interval='@daily',
    dag_id='a_dag_in_k8s'
) as dag:

    # instantiate the KPO
    KPO_bash_command = KubernetesPodOperator(
        task_id='KPO_bash_command', # task id unique within the DAG
        namespace=namespace, # default namespace = 'default'
        name='my_pod_1', # pod name, unique within the namespace
        image='ubuntu', # pulling the ubuntu image from DockerHub
        cmds=['bash', '-cx'], # entry point
        arguments=["echo hello"], # arguments for the entry point
        get_logs=True, # provides stdout from the container as task logs
        is_delete_operator_pod=True # deletion of the pod after the task ends
        )
```

## Example: Spinning up a pod in EKS from Airflow

If some of your tasks require specific resources like a GPU you may want to run them in a different cluster than your Airflow Instance. In setups where both clusters are used by the same AWS or GCP account this can be managed with roles and permissions. There is also the possibility to use a CI account and enable [cross-account access to AWS EKS cluster resources](https://aws.amazon.com/blogs/containers/enabling-cross-account-access-to-amazon-eks-cluster-resources/).  

The example below shows the steps to take to set up an EKS cluster on AWS and run a pod on it from an Airflow instance if cross-account access is not feasible. After setup of the EKS cluster the `KubeConfig` as well as the `AWS Profile` have to be provided to Airflow to make the connection to the remote cluster.  

### Step 1: Set up an EKS cluster on AWS

To set up a new EKS cluster on AWS you first need to create an IAM role with suitable permissions.
On AWS navigate to **Identity and Access Management (IAM)** -> **Roles** -> **Create role**. Select AWS service and `EKS` from the dropdown menu as well as `EKS - Cluster`. Make sure to give the role a unique name and to add the permission policies `AmazonEKSWorkerNodePolicy` and `AmazonEC2ContainerRegistryReadOnly`.

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
