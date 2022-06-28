---
title: "KubernetesPodOperator on Astronomer"
description: "Use the KubernetesPodOperator on Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "kubepod-operator"
heroImagePath: null
tags: ["Kubernetes", "Operators"]
---

## Overview

The [`KubernetesPodOperator`](https://registry.astronomer.io/providers/kubernetes/modules/kubernetesPodoperator) (KPO) is an operator from the Kubernetes provider package designed to provide a straightforward way to execute a task in a Kubernetes Pod from your Airflow environment. In a nutshell, the KPO is an abstraction over a call to the Kubernetes API to launch a Pod.

In this guide, we list the requirements to run the `KubernetesPodOperator`, explain when to use it and cover its most important arguments, as well as the difference between the KPO and `KubernetesExecutor`. We also provide concrete examples on how to use the KPO to run a task in a language other than Python, how to use the KPO with XComs, and how to launch a Pod in a remote AWS EKS Cluster.  

> **Note**: Kubernetes is a powerful tool for Container Orchestration with complex functionality. If you are unfamiliar with Kubernetes we recommend taking a look at the [Kubernetes Documentation](https://kubernetes.io/docs/home/).  

## Requirements For Using the KubernetesPodOperator

To use the `KubernetesPodOperator` it is necessary to install the Kubernetes provider package.

```bash
pip install apache-airflow-providers-cncf-kubernetes==<version>
```

To double check which version of the Kubernetes provider package is compatible with your version of Airflow and to view dependencies that will be installed automatically please refer to the [Airflow Kubernetes provider Documentation](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/index.html#requirements).

You will also need an existing Kubernetes cluster to connect to, which commonly but not necessarily is the same cluster that Airflow is running on. It is _not_ necessary to use the Kubernetes Executor in order to use the KPO. You may use any of the following executors: `LocalExecutor`, `LocalKubernetesExecutor`, `CeleryExecutor`, `KubernetesExecutor`, [`CeleryKubernetesExecutor`](https://airflow.apache.org/docs/apache-airflow/2.0.0/executor/celery_kubernetes.html). When using Celery remember to install its [provider](https://registry.astronomer.io/providers/celery).

> **Note**: On Astro, the infrastructure needed to run KPO with CeleryExecutor is pre-built into every cluster. Astronomer provides [comprehensive documentation on using the KPO on Astro](https://docs.astronomer.io/astro/kubernetespodoperator).  

### Running the KubernetesPodOperator Locally

When developing and testing changes it can be tedious to deploy to a remote environment, which is why many users set up their local dev environment to support usage of the KPO. This can be accomplished in several ways.

For users of the Astro CLI there is a [step-by-step tutorial](https://docs.astronomer.io/software/kubepodoperator-local) available in the Astro Documentation, which can also be adapted for other dockerized Airflow setups.

It is also possible to run open source Airflow within a local Kubernetes cluster using the [Helm Chart for Apache Airflow](https://airflow.apache.org/docs/helm-chart/stable/index.html). For a walkthrough of this setup you can refer to the recording of the [Getting Started With the Official Airflow Helm Chart Webinar](https://www.youtube.com/watch?v=39k2Sz9jZ2c&ab_channel=Astronomer).

When running Airflow within a Kubernetes cluster, using the KPO does not require further configuration beyond leaving the `KubernetesPodOperator` parameter `in_cluster` on its default setting (`True`) to run a new Pod within the same cluster. An example on how to run a Pod on a remote cluster, including in the case of not running local Airflow on Kubernetes, is presented at the end of this guide.

## When to use the KubernetesPodOperator

The `KubernetesPodOperator` runs any Docker image provided to it, whether they are pulled from [DockerHub](https://hub.docker.com/) or from private repositories. Frequent use cases are:

- Running a task better described in a language other than Python. For an example see the section 'Example: Using the `KubernetesPodOperator` to run a script in Haskell' below.
- Having full control over how much compute resources and memory a single task can use.
- Executing tasks in an separate environment with individual packages and dependencies.
- Running tasks that necessitate using a version of Python not supported by your Airflow environment.
- Running tasks with specific Node (a virtual or physical machine in Kubernetes) constraints such as only running on Nodes located in the European Union.

Sometimes you may want to run Pods on different clusters, for example if only some need GPU resources while others do not. This is also possible with the KPO and a step-by-step example is provided at the end of this guide.

> **Note**: A simple way to execute tasks in different clusters with different compute resources using worker queues is an upcoming feature on Astro!

### KubernetesPodOperator vs KubernetesExecutor

In Airflow you have the option to choose between a variety of [executors](https://www.astronomer.io/guides/airflow-executors-explained) which determine how your Airflow tasks will be executed.

The `KubernetesExecutor` and the `KubernetesPodOperator` both dynamically launch and terminate Pods to run Airflow tasks. As the names suggest, `KubernetesExecutor` is an executor, which means it affects how all tasks in an Airflow instance are executed, while the `KubernetesPodOperator` is an operator defining that a single task is to be launched in a Kubernetes Pod with the given configuration and does not affect any other tasks in the Airflow instance. Details on how to configure the `KubernetesExecutor` can be found in the [Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/executor/kubernetes.html).

Compared to the KPO, the `KubernetesExecutor`:

- Runs Airflow tasks in a Kubernetes Pod without the user needing to specify a Docker image.
- Is implemented at the configuration level of the Airflow instance, which means _all_ tasks will each be run in their own Kubernetes Pod. This may be desired in some use cases to leverage auto-scaling, but is generally not ideal for environments with a high volume of shorter running tasks.
- Has less abstraction over Pod configuration. All task-level configurations have to be passed in as a dictionary via the `BaseOperator` argument `executor_config`, which is available to all operators.
- If a custom Docker image is passed to the `KubernetesExecutor`'s `base` container by providing it to either the `pod_template_file` or the `pod_override` key in the dictionary for the `executor_config` argument, it needs to have Airflow installed, otherwise the task will not run. A possible reason for customizing this Docker image would be to run a task in an environment with different versions of packages than the majority of the tasks an Airflow instance. This is not the case with the KPO, which can run any valid Docker image.

Both the `KubernetesPodOperator` and the `KubernetesExecutor` can use the entire Kubernetes API with regards to Pod creation. Which one to use is an individual choice based on the user's requirements and preferences. You can think of the KPO as "Docker image first" and the `KubernetesExecutor` as "operator first" implementations. The KPO is generally ideal for controlling the environment the task is run in, while the `KubernetesExecutor` is ideal for controlling resource optimization. Frequently the KPO is used in an Airflow environment using the `KubernetesExecutor` to run some tasks where the focus is on environment control while the other tasks are run in Pods via the `KubernetesExecutor`.

## How to configure the `KubernetesPodOperator`

The KPO launches any valid Docker Image provided to it (passed via the `image` parameter) in a new Kubernetes Pod on an existing Kubernetes cluster. The operator has many other parameters which specify the Pod configuration which the KPO translates into a call to the [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/). The `KubernetesPodOperator` offers full access to Kubernetes API functionality relating to Pod creation.    

The `KubernetesPodOperator` can be instantiated like any other operator within the context of a DAG. The following are some of the arguments that can be passed to the operator.

**Mandatory arguments** are:

- `task_id`: a unique string identifying the task within Airflow.
- `namespace`: the namespace within your Kubernetes cluster the new Pod should be assigned to.
- `name`: the name of the Pod created. This name needs to be unique for each Pod within a namespace.
- `image`: a Docker image to launch. Images from [hub.docker.com](https://hub.docker.com/) can be passed in with just the image name, custom repositories have to be given as full URLs.

Commonly used **optional arguments** include:

- `random_name_suffix`: generates a random suffix for the Pod name if set to `True`. Avoids naming conflicts when running a large number of Pods.
- `labels`: add key:value pairs to the Pod which can be used to logically group decoupled objects together.
- `ports`: provides the possibility to override default ports for the Pod.
- `reattach_on_restart`: defines how to handle losing the worker while the Pod is running, by default (`True`) the existing Pod will reattach to the worker on the next try. `False` creates a new Pod for each try.
- `is_delete_operator_pod`: `True` by default, will delete the Pod when it reaches its final state or when the execution is interrupted.
- `get_logs`: provides the `stdout` of the container as task-logs to the Airflow logging system.
- `log_events_on_failure`: if set to `True` events will be logged in case the Pod fails (default: `False`).
- `env_vars`: allows the user to specify individual environment variables for a Pod.
- `resources`: allows the user to pass a dictionary with resource requests (keys: `request_memory`, `request_cpu`) and limits (keys: `limit_memory`, `limit_cpu`, `limit_gpu`). See the [Kubernetes Documentation on Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) for more information.
- `volumes`: can be used to pass in a modified `k8s.V1Volume`, see also the [Kubernetes example DAG from the Airflow documentation](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_modules/tests/system/providers/cncf/kubernetes/example_kubernetes.html).
- `affinity` and `tolerations` are ways to further specify rules for [Pod to Node assignment](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/). Like the `volumes` parameter they also require their input as a `k8s` object.

There are also many other arguments that can be used to configure the Pod and pass information to the Docker image. For example, the 'Spinning up a Pod in EKS from Airflow' section below shows how to define an entrypoint (`cmds`) and its arguments (`arguments`) for your container.

> **Note**: The following KPO arguments can be used with Jinja templates: `image`, `cmds`, `arguments`, `env_vars`, `labels`, `config_file`, `pod_template_file`, and `namespace`.

> **Note**: Many more arguments are available to customize the `KubernetesPodOperator` further. For a complete and up to date list see the [`KubernetesPodOperator` source code](https://github.com/apache/airflow/blob/main/airflow/providers/cncf/kubernetes/operators/kubernetes_pod.py).

### Configuring Kubernetes Connection

When leaving the `in_cluster` parameter on its default setting (`True`) it is not necessary to further configure the Kubernetes connection, beyond specifying the required parameter `namespace`. The Pod specified by the `KubernetesPodOperator` will be run on the same Kubernetes cluster as your Airflow instance is running on.

If you are not running Airflow on Kubernetes or want to send the Pod to a different cluster than the one currently hosting your Airflow instance, you can set up a Kubernetes Cluster [Connection](https://www.astronomer.io/guides/connections) in the Airflow UI under **Admin** -> **Connections**, which will use the [Kubernetes Hook](https://registry.astronomer.io/providers/kubernetes/modules/kuberneteshook) to connect to the [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/) of a different Kubernetes cluster. This connection can be passed to the `KubernetesPodOperator` via the `kubernetes_conn_id` argument and needs two components to work:

- a `KubeConfig` file, provided as either a path to the file or in JSON format.
- the cluster context to select a specific cluster from the provided `KubeConfig` file.

The picture below shows how to set up a Kubernetes Cluster Connection in the Airflow UI.

![Kubernetes Cluster Connection](https://assets2.astronomer.io/main/guides/kubepod-operator/kubernetes_cluster_connection.png)

The components of the connection can also be set or overwritten at the task level by using the arguments `config_file` (to specify the path to the `KubeConfig` file) and `cluster_context`. Setting these parameters at the level of `airflow.cfg` has been deprecated.

### Example: Using the KPO to Run a Script in Another Language

A frequent use case for the `KubernetesPodOperator` is to run scripts for tasks better described in a language other than Python. For this purpose a custom Docker image has to be built and either run from a public or private [DockerHub repository](https://docs.docker.com/docker-hub/repos/).

> **Note**: Astro provides documentation on [how to run images from private repositories](https://docs.astronomer.io/astro/kubernetespodoperator).

The code below shows a Haskell script which takes the environment variable `NAME_TO_GREET` and prints a message containing it to the console:

```haskell
import System.Environment

main = do
        name <- getEnv "NAME_TO_GREET"
        putStrLn ("Hello, " ++ name)
```

The Dockerfile creates the necessary environment to run the script and then executes it with a `CMD` command.

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

After making the Docker image available it can be run from the KPO via the `image` argument. The example DAG below showcases a variety of arguments of the `KubernetesPodOperator`, including how to pass the environment variable `NAME_TO_GREET` which is used from within the Haskell code.

```python
from airflow import DAG
from datetime import datetime
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
                                                        KubernetesPodOperator)
from airflow.configuration import conf

## get the current Kubernetes namespace Airflow is running in
namespace = conf.get("kubernetes", "NAMESPACE")

## set the name that will be printed
name = 'your_name'

## instantiate the DAG
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
        # the Docker image to launch
        image='<image location>',

        ## arguments pertaining to where the Pod is launched
        # launch the Pod on the same cluster as Airflow is running on
        in_cluster=True,
        # launch the Pod in the same namespace as Airflow is running in
        namespace=namespace,

        ## Pod configuration
        # name the Pod
        name='my_pod',
        # give the Pod name a random suffix, ensure uniqueness in the namespace
        random_name_suffix=True,
        # attach labels to the Pod, can be used for grouping
        labels={'app':'backend', 'env':'dev'},
        # reattach to worker instead of creating a new Pod on worker failure
        reattach_on_restart=True,
        # delete Pod after the task is finished
        is_delete_operator_pod=True,
        # get log stdout of the container as task logs
        get_logs=True,
        # log events in case of Pod failure
        log_events_on_failure=True,
        # pass your name as an environment var
        env_vars={"NAME_TO_GREET": f"{name}"}
        )
```

## Example: Using the KubernetesPodOperator with XComs

[XCom](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html) is a commonly used Airflow feature for passing small amounts of data between tasks. It is possible to use this feature with the KPO to both receive values stored in XCom and push values to XCom.

The DAG below shows a straightforward ETL pipeline with an `extract_data` task that runs a query on a database and returns a value; the return value is automatically pushed to XComs thanks to the [TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html#tutorial-on-the-taskflow-api).  

The `transform` task is a `KubernetesPodOperator` which requires the XCom data pushed from the upstream task before it, and launches an image having been built with the following Dockerfile:

```dockerfile
FROM python

WORKDIR /

# creating the file to write XComs to
RUN mkdir -p airflow/xcom         
RUN echo "" > airflow/xcom/return.json

COPY multiply_by_23.py ./

CMD ["python", "./multiply_by_23.py"]
```

When using XComs with the KPO, it is very important to create the file `airflow/xcom/return.json` in your Docker container (ideally from within your Dockerfile as seen above), because Airflow will only look for XComs to pull at that specific location. The image also contains a simple Python script to multiply an environment variable by 23, package the result into a json and write that json to the correct file to be retrieved as an XCom. The XComs from the KPO will only be pushed if the task itself was marked as successful.  

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

Below you can find the full DAG code. Remember to only turn on `do_xcom_push` if you have created the `airflow/xcom/return.json` within the Docker container run by the KPO, otherwise the task will fail.


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
        # simulating querying from a database
        data_point = random.randint(0,100)
        return data_point

    transform = KubernetesPodOperator(
        # operator specific argument
        task_id='transform',

        # arguments pertaining to the image and commands executed
        image='< image location >', # the Docker Image to launch

        # arguments pertaining to where the Pod is launched
        in_cluster=True, # launch the Pod on the same cluster as Airflow is running on
        namespace=namespace, # launch the Pod in the same namespace as Airflow is running in

        # Pod configuration
        name='my_pod', # naming the Pod
        get_logs=True, # log stdout of the container as task logs
        log_events_on_failure=True, #log events in case of Pod failure
        env_vars={"DATA_POINT": "{{ ti.xcom_pull(task_ids='extract_data', key='return_value') }}"},
        do_xcom_push=True #push the contents from xcom.json to xcoms
        )

    @task
    def load_data(**context):
        transformed_data_point = context['ti'].xcom_pull(task_ids='extract_data', key='return_value')
        print(transformed_data_point)

    extract_data() >> transform >> load_data()
```

## Example: Using KPO to Run a Pod in a Separate Cluster

If some of your tasks require specific resources like a GPU you may want to run them in a different cluster than your Airflow Instance. In setups where both clusters are used by the same AWS or GCP account, this can be managed with roles and permissions. There is also the possibility to use a CI account and enable [cross-account access to AWS EKS cluster resources](https://aws.amazon.com/blogs/containers/enabling-cross-account-access-to-amazon-eks-cluster-resources/).  

However, you may want to use a specific AWS or GCP account that you keep separate from your Airflow environment. Or you are currently running Airflow on a local setup not using Kubernetes, but still want to run some tasks in a Kubernetes Pod on a remote cluster.

The example below shows the steps to take to set up an EKS cluster on AWS and run a Pod on it from an Airflow instance where cross-account access is not feasible. After setup of the EKS cluster, the `KubeConfig` as well as the `AWS Profile` have to be provided to Airflow to make the connection to the remote cluster. Note that the same general steps are applicable to other Kubernetes services (e.g. GKE).  

> **Note**: Some platforms which can host Kubernetes clusters have their own specialised operators available like the [GKEStartPodOperator](https://registry.astronomer.io/providers/google/modules/gkestartPodoperator) and the [EksPodOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/eks/index.html#module-airflow.providers.amazon.aws.operators.eks).

### Step 1: Set up an EKS cluster on AWS

To set up a new EKS cluster on AWS you first need to create an IAM role with suitable permissions.
On AWS navigate to **Identity and Access Management (IAM)** -> **Roles** -> **Create role**. Select AWS service and `EKS` from the dropdown menu as well as `EKS - Cluster`. Make sure to give the role a unique name and to add the permission policies `AmazonEKSWorkerNodePolicy`, `AmazonEKS_CNI_Policy` and `AmazonEC2ContainerRegistryReadOnly`.

Edit the trust policy (**IAM** -> **Roles** -> role name) of this new role to include your user and necessary AWS Services. This step ensures that the role can be assumed by your user.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<aws account id>:<your user>",
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

Add the new role to your local AWS credentials file which by default can be found at `~/.aws/config`.

```text
[default]
region = <your region>

[profile <name of the new role>]
role_arn = <EKS role arn>
source_profile = <your user>
```

Make sure your default credentials in `~/.aws/credentials` are using a valid and active key for your username (keys can be generated at **IAM** -> **Users** -> your user -> **Security Credentials**).

Make a copy of `~/.aws` available to your Airflow environment (for Astro users: copy it into the `include` folder).

Lastly, create a new EKS cluster (**EKS** -> **Clusters** -> **Add cluster**) and assign the the newly created role to it. The cluster might take a few minutes to become active.

### Step 2: Retrieve the KubeConfig file from the EKS cluster

To be able to remotely connect to the newly created EKS cluster the `KubeConfig` file is needed. It can be retrieved by running:

```bash
aws eks --region region update-kubeconfig --name cluster_name
```

The command above will copy information relating to the new cluster into your existing `KubeConfig` file at `~/.kube/config`. Select the information pertaining to your EKS cluster and make it available to your Airflow environment (for Astro users: copy it into the `include` folder). It is likely that you will have to add the last 5 lines to get to the following structure:

```text
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <your certificate>
    server: <your AWS server address>
  name: <arn of your cluster>
contexts:
- context:
    cluster: <arn of your cluster>
    user: <arn of your cluster>
  name: <arn of your cluster>
current-context: <arn of your cluster>
kind: Config
preferences: {}
users:
- name: <arn of your cluster>
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      args:
      - --region
      - <your cluster's AWS region>
      - eks
      - get-token
      - --cluster-name
      - <name of your cluster>
      - --profile
      - default
      command: aws
      interactiveMode: IfAvailable
      provideClusterInfo: false
```

The `KubeConfig` file is how the KPO will connect to a Kubernetes cluster by running the `awscli` with the default profile, using the credentials you provided in Step 1.

### Step 3: Add a namespace and service account to the EKS Cluster

It is best practice to use a new namespace for all Pods sent to the EKS cluster from the Airflow environment.  

```bash
# create a new namespace on the EKS cluster
kubectl create namespace <your namespace name>
```

### Step 4: Adjust the Airflow configuration files

This step will differ depending on the Airflow setup. When running Airflow locally, it is necessary to make sure `awscli`, `apache-airflow-providers-cncf-kubernetes`,
and `apache-airflow-providers-amazon` are installed correctly on the local machine.

If you are running Airflow with Docker, add the following line to your Dockerfile to copy your aws credentials from `/include` (or any other location) into the container:

```dockerfile
COPY --chown=astro:astro include/.aws /home/astro/.aws
```

To be able to correctly authenticate yourself to the remote cluster it is also important to add the AWS command line tool (`awscli`) to your `packages.txt`, and the necessary provider packages to `requirements.txt` (the provider packages will differ depending on what cloud you are connecting to):

```text
awscli
```

```text
apache-airflow-providers-cncf-kubernetes
apache-airflow-providers-amazon
```

### Step 5: Add AWS connection ID

In the Airflow UI navigate to **Admin** -> **Connections** to set up the connection to the AWS account running the target EKS cluster. Chose a unique connection ID, the Connection Type 'Amazon Web Services' and use your `aws_access_key_id` as login and your `aws_secret_access_key` as password.

### Step 6: Create the DAG with the KPO

> **Note**: When creating new deployments, users of the Astro cloud will need to set one additional argument in the KPO: `labels={"airflow_kpo_in_cluster": "False"}` to connect to a remote cluster. If you are trying to set up the KPO connecting to a remote cluster in an existing deployment please contact Customer Support.

If dynamic behavior of the EKS cluster is desired, e.g. Nodes get created with specifications for a task and deleted after the task has run, it is necessary to use several classes from the Amazon provider package as shown in the example DAG below. If your remote Kubernetes cluster has Nodes already available you will only need the `KubernetesPodOperator` itself (task number 3 in the example).

The example DAG contains 5 consecutive tasks:

- Create a node group according to the users' specifications (in the example using GPU resources).
- Use a sensor to check that the cluster is running correctly.
- Use the `KubernetesPodOperator` to run any valid Docker image in a Pod on the newly created node group on the remote cluster. The example DAG uses the standard `Ubuntu` image to print "hello" to the console using a `bash` command.
- Delete the node group.
- Verify that the node group has been deleted.

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

# custom class to create a node group with Nodes on EKS
class EKSCreateNodegroupWithNodesOperator(EKSCreateNodegroupOperator):

    def execute(self, context):
        # instantiating an EKSHook on the basis of the AWS connection (Step 5)
        eks_hook = EKSHook(
            aws_conn_id=self.aws_conn_id,
            region_name=self.region,
        )

        # define the Node group to create
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

    # task 1 creates the node group
    create_gpu_nodegroup=EKSCreateNodegroupWithNodesOperator(
        task_id='create_gpu_nodegroup',
        cluster_name='<your cluster name>',  
        nodegroup_name='gpu-nodes',
        nodegroup_subnets=['<your subnet>', '<your subnet>'],
        nodegroup_role_arn='<arn of your EKS role>',
        aws_conn_id='<your aws conn id>',
        region='<your region>'
    )

    # task 2 check for node group status, if it is up and running
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
    # here, cluster_context and the config_file are defined at the task level
    # it is of course also possible to abstract these values
    # in a Kubernetes Cluster Connection
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
        startup_timeout_seconds=240,
    )

    # task 4 deleting the node group
    delete_gpu_nodegroup=EKSDeleteNodegroupOperator(
        task_id='delete_gpu_nodegroup',
        cluster_name='<your cluster name>',  
        nodegroup_name='gpu-nodes',
        aws_conn_id='<your aws conn id>',
        region='<your region>'
    )

    # task 5 checking that the node group was deleted successfully
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

It is possible to view the remote Pod while it runs using `kubectl` (if the local command line connection to the remote cluster has been configured):

![Kubectl remote Pod running](https://assets2.astronomer.io/main/guides/kubepod-operator/kubectl_remote_pod.png)
