---
title: "Executing Talend Jobs with Airflow"
description: ""
date: 2020-11-18T00:00:00.000Z
slug: "airflow-talend-integration"
heroImagePath: "https://assets2.astronomer.io/main/guides/talend/talend_airflow_hero.png"
tags: ["Integrations"]
---

## Why use Talend and Airflow

[Talend](https://www.talend.com/) is a popular tool for data integration and data management that can be easily used along with Airflow and Astronomer to have the best of multiple worlds for data management. 

There are a couple of benefits to using Airflow and Talend together:

- Using Airflow for orchestration allows for easily running multiple jobs with dependencies, parallelizing jobs, monitoring run status and failures, and more
- Combining Talend and Airflow allows you to use both tools for what they're good for. If Talend works particularly well for one use case and python for another, you can do both and still have a one-stop-shop for orchestration, monitoring, logs, etc. with Airflow and Astronomer
    - You can even combine both Talend jobs and other tasks in the same DAG if desired
- If your team is moving to Astronomer but has existing Talend jobs, using the two together eliminates the need to migrate existing jobs to python code

In this tutorial we'll show simple examples that highlight a few ways that Talend and Airflow can easily work together. 

## How to Execute Talend Jobs with Airflow

There are two easy ways to execute Talend jobs with Airflow:

1. Use the Talend Cloud API and execute the job using the SimpleHttpOperator
2. Containerize your Talend jobs and execute them using the KubernetesPodOperator

Each method has pros and cons, and the method you choose will likely depend on your Talend setup and workflow requirements.

|Method      |Docker + KubernetesPodOperator                                                                                                                                                                    |API + SimpleHttpOperator                                                                                                            |
|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
|Pros        |<ul><li>Containerizing jobs brings the benefits of containerization including efficiency, flexibility, and scaling </li> <li>  Easily allows for downstream dependencies</li><li>Logs from jobs are shown in Airflow UI| <ul><li>Very easy and accessible. Little setup and knowledge of other tools is required</li></ul>                                                   |
|Cons        | <ul><li>Must have Talend Studio to containerize jobs </li> <li>  More requirements and complexity to setup</li></ul>                                                                                                        | <ul><li>Not well suited for triggering jobs that have downstream dependencies </li> <li>  Logs from Talend job are not automatically sent to Airflow</li></ul>|
|Requirements| <ul><li>Talend Studio license </li> <li> Docker registry (can use Dockerhub if public is okay)</li> <li> Kubernetes</li></ul>                                                                                                      | <ul><li>Talend cloud license that allows API access</li></ul>                                                                                       |

<br/>

## Executing Talend Jobs Using the Cloud API

The first way of executing Talend jobs from Airflow is using the Talend Cloud API via the SimpleHttpOperator in Airflow. This method is ideal if you have Talend Cloud jobs that do not have downstream dependencies.

Below we will show how to configure your Talend Cloud account to work with the API, and an example DAG that will execute a workflow. If you are unfamiliar with the Talend Cloud API, the documentation at these links are helpful: 

- [Talend Public API Docs](https://community.talend.com/s/article/Using-the-Talend-Cloud-Management-Console-Public-API-O2Ndn)

- [Talend UI Docs](https://api.us-west.cloud.talend.com/tmc/swagger/swagger-ui.html#!/)

### Getting Started with the Talend Cloud API

Getting configured to use the API in Talend Cloud is straight forward. First, make sure the job you want to execute is present in the Talend Management Console as shown below. For this example, we will execute a sample 'SayHello' job.

![Say Hello Job](https://assets2.astronomer.io/main/guides/talend/talend_api_1.png)

Next, note your job's Task ID; this will be passed to the API to trigger this specific job.

![Task ID](https://assets2.astronomer.io/main/guides/talend/talend_api_2.png)

Finally, ensure your user has a personal access token created. This is required for authenticating to the API. To create one, under your user go to Profile Preferences, then Personal Access Tokens, and then add a token.

![Token](https://assets2.astronomer.io/main/guides/talend/talend_api_3.png)

That's all you have to do on the Talend side! Now you can move on to creating an Airflow DAG to execute this job.

### Using the Talend API with Airflow

Using Airflow to interact with the Talend Cloud API is easy using the SimpleHttpOperator. In this example we will show how to execute a job; however, note that there are many other actions you can perform with the Talend API as described in the documentation linked above, and all of these can be accomplished in a similar way. Also note that there are other ways of making an API call in Airflow besides using the SimpleHttpOperator; we have chosen to show this operator because it is the most straight forward for this use case.

First, we need to set up an Airflow connection to connect to the API. The connection should be an HTTP type, and should be configured like this:

![Talend Connection](https://assets2.astronomer.io/main/guides/talend/airflow_talend_5.png)

The host name should be the Talend Cloud API URL. This can vary depending on which region your account is hosted in and may not be the same as the one shown above. The extras should contain your authorization string, with 'Bearer' followed by your personal access token. 

Next we can create our DAG.

```python
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('talend_api_jobs',
          schedule_interval='@once',
          default_args=default_args
          ) as dag:

    talend1 = SimpleHttpOperator(
        task_id='talend_api',
        method='POST',
        http_conn_id='talend_api',
        endpoint='/tmc/v2.2/executions',
        data=json.dumps({"executable": "5fb2f5126a1cd451b07bee7a"}),
    )
```

This DAG has a single SimpleHttpOperator that will send a POST request to the Talend API to trigger our job. Ensure you enter the `http_conn_id` as the connection created above. The `endpoint` should be the Talend Cloud API executions endpoint for your region. And the `data` is the body of the request, and needs to contain the executable, which is the Task ID described in the previous section formatted in json.

Now if you run this DAG in Airflow, you should see a successful log that looks something like this:

![Success log](https://assets2.astronomer.io/main/guides/talend/airflow_talend_6.png)

And looking at the Talend Management Console, you can see the job is running:

![Talend Running Job](https://assets2.astronomer.io/main/guides/talend/airflow_talend_7.png)

Finally, note that because the API call will simply trigger the job, the Airflow task will be marked successful as soon as a response is received from the API; this is not tied to when the job actually completes, so if you have downstream tasks that need the Talend job to be complete you will either have to use another method like the KubernetesPodOperator described below, or design your workflow in another way that manages this dependency.

## Executing Talend Jobs with KubernetesPodOperator

The second way to execute Talend jobs with Airflow is to containerize them and execute them from Airflow using the KubernetesPodOperator. This is a good option if you are using Talend studio, and if you have tasks that are dependent on your Talend jobs completing first.

Here we'll show how to containerize an existing Talend job, and then execute some containerized jobs with dependencies using the KubernetesPodOperator in Airflow.

### Containerizing Talend Jobs

Existing Talend jobs and can be can be containerized with docker and pushed to a repository with the Talend Studio. To start go to Talend studio, find the job you would like to containerize, and select the publish feature from the right-click menu.

![Talend UI](https://assets2.astronomer.io/main/guides/talend/talend_ui_1.png)

Once clicked a publish job pop up will come up. Select Docker image as the 'Export Type' to publish the job as a docker image.

![Talend UI 2](https://assets2.astronomer.io/main/guides/talend/talend_ui_2.png)

Select next to set up your connection between Talend and your registry. In this example the job is being published to DockerHub and being built with a local Docker host. If you are using a remote Docker host, you will need to find the IP address Docker is running on and use TCP to connect. For example put `tcp://<docker-host-ip>` in the input box to the side of 'Remote'.

![Talend UI 3](https://assets2.astronomer.io/main/guides/talend/talend_ui_3.png)

Specifics on how the parameters need to connect to your registry are shown below. 

`<Image name>` the name of your repository (talendjob)

`<Image tag>` the image tag (0.1.0)

`<Registry>` Where the registry is located (docker.io/davidkoenitzer)

`<Username>` Your DockerHub username 

`<Password>` Your DockerHub Password 

When you select 'Finish' the job will be converted into Docker image and pushed to the indicated registry. In this example the job was pushed to [https://hub.docker.com/repository/docker/davidkoenitzer/talendjob](https://hub.docker.com/repository/docker/davidkoenitzer/talendjob) 

Talend can also publish jobs to Amazon ECR, Azure ACR, and Google GCR. Use this guide from Talend for connection parameter specifics [https://www.talend.com/blog/2019/03/12/how-to-deploy-talend-jobs-as-docker-images-to-amazon-azure-and-google-cloud-registries/](https://www.talend.com/blog/2019/03/12/how-to-deploy-talend-jobs-as-docker-images-to-amazon-azure-and-google-cloud-registries/)

![Executing%20Talend%20Jobs%20with%20Airflow%202a2beb0aae414e13b1fcf6db0c53e173/Screen_Shot_2020-10-28_at_3.37.35_PM.png](Executing%20Talend%20Jobs%20with%20Airflow%202a2beb0aae414e13b1fcf6db0c53e173/Screen_Shot_2020-10-28_at_3.37.35_PM.png)

You can now run this job locally by running:

`docker run davidkoenitzer/talendjob:0.1.0`

If you ran the command on the terminal you should see the output `hello`. Now you should be able to pull and run this image from Airflow. 

### Orchestrating Containerized Talend Jobs with Airflow

Once your Talend jobs are containerized and pushed to a registry, you can move on to creating a DAG that will orchestrate them. To do so we will mainly use the KubernetesPodOperator. If you are not familiar with how this operator works, [this is a great starting place for documentation](https://airflow.readthedocs.io/en/latest/howto/operator/kubernetes.html).

For this example, we are going to create a DAG that will execute two Talend jobs, one of which is dependent on the other, and then send an email notification if the jobs are successful. The full DAG code is copied here:

```python
from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.email_operator import EmailOperator
from airflow import configuration as conf

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

namespace = conf.get('kubernetes', 'NAMESPACE')

# This will detect the default namespace locally and read the 
# environment namespace when deployed to Astronomer.
if namespace =='default':
    config_file = '/usr/local/airflow/include/.kube/config'
    in_cluster=False
else:
    in_cluster=True
    config_file=None

# Define recipient emails for successful completion notification
email_to = ["noreply@astronomer.io"]

with DAG('talend_jobs',
          schedule_interval='@once',
          default_args=default_args
          ) as dag:

    talend1 = KubernetesPodOperator(
                namespace=namespace,
                image="your-repo/talendjob:hello",
                name="talend-test-hello",
                task_id="hello-world",
                in_cluster=in_cluster, # if set to true, will look in the cluster, if false, looks for file
                cluster_context='docker-desktop', # is ignored when in_cluster is set to True
                config_file=config_file,
                is_delete_operator_pod=True,
                get_logs=True
                )

    talend2 = KubernetesPodOperator(
                namespace=namespace,
                image="your-repo/talendjob:random",
                name="talend-test-random",
                task_id="random",
                in_cluster=in_cluster,
                cluster_context='docker-desktop', 
                config_file=config_file,
                is_delete_operator_pod=True,
                get_logs=True
                )

    send_email = EmailOperator(
                    task_id='send_email',
                    to=email_to,
                    subject='Talend Jobs Completed Successfully',
                    html_content='<p>Your containerized Talend jobs have completed successfully. <p>'
                )

    
    talend1 >> talend2 >> send_email
```

The first half of the code simply imports packages and sets the DAG up to work with Kubernetes. Then, after we define the DAG, we get to the task definitions. Each Talend job is one task using the KubernetesPodOperator. In this case we have two tasks for two Talend jobs, `talend1` and `talend2`. 

In each task, the `image` is the name of the image of the containerized job saved to a registry as described above. Note that in this example we use an image from DockerHub (i.e. a public registry); by default this is where the KubernetesPodOperator looks for the provided image name. If instead you want to pull an image from a private registry (e.g. ECR, GCR, etc.), the setup looks a little different. Refer to [this documentation](https://airflow.readthedocs.io/en/latest/howto/operator/kubernetes.html#how-to-use-private-images-container-registry) for details.

Since this example is very simple we don't need to provide any arguments, cmds, etc. to run the image. But if needed, these can all be specified in the operator.

Finally, we define a `send_email` task to notify us that the tasks completed successfully. Then, the final lines of code define task dependencies. 

Now, if we deploy this code to Astronomer and check out the Airflow UI, we should see a DAG that looks like this:

![Airflow Talend DAG](https://assets2.astronomer.io/main/guides/talend/airflow_talend_1.png)

If we run the DAG, any output from the containerized Talend jobs should be printed in the Airflow logs for that task. In this case, our first Talend job prints 'hello world', and our second prints a series of random strings. Looking at the task logs we should see:

Task 1:

![Airflow Talend Task Logs](https://assets2.astronomer.io/main/guides/talend/airflow_talend_2.png)

Task 2:

![Airflow Talend Task Log 2](https://assets2.astronomer.io/main/guides/talend/airflow_talend_3.png)

You can also view task statuses as you would normally using the Airflow UI. If your Talend job runs successfully, the Airflow task that executed it will have a 'success' status. If the Talend job fails, the Airflow task will be marked 'failed' (as shown on the second task in the screenshot below), and any error messages will be printed in the Airflow task logs.

![Airflow Task Statuss](https://assets2.astronomer.io/main/guides/talend/airflow_talend_4.png)

Pretty straight forward! Once your Talend jobs are containerized, they can be orchestrated using Airflow in any sort of DAG needed for your use case, by themselves, with other Talend jobs, with any other Airflow tasks, etc. 


## Troubleshooting - Common Issues

### Error when Building Images with Docker Mac

If you are getting an error that says `Cannot run program "docker-credential-desktop"` while building an image from a job using a local docker host on Mac then it may be due to an outdated Java plugin on Talend Studio V7.3.1  

You will need to edit your `.docker/config.json`. The file is localted at ~/.docker/config.json. Delete the line `"credsStore" : "desktop"` from you config.json :

```json
{
  ...
  "credsStore" : "desktop"
}
```

This will stop the error from happening when building images from Talend jobs with your local docker host. 

### SMTP Configuration

Note that if you are running the specific example DAG provided above in the KubernetesPodOperator section, SMTP will need to be configured on your Airflow instance in order for the `send_email` task to work. This requires an SMTP server that will allow a credentialed application to send emails. If you have that, it is simply a matter of configuring the following Airflow Environment variables: 

```yaml
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_USER=your-mail-id@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD=yourpassword
AIRFLOW__SMTP__SMTP_MAIL_FROM=your-mail-id@gmail.com
```

Note: values shown here are for example only. Fill in everything with your SMTP info.