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

<table class="collection-content"><thead><tr><th><span class="icon property-icon"><svg viewBox="0 0 14 14" style="width:14px;height:14px;display:block;fill:rgba(55, 53, 47, 0.4);flex-shrink:0;-webkit-backface-visibility:hidden" class="typesTitle"><path d="M7.73943662,8.6971831 C7.77640845,8.7834507 7.81338028,8.8943662 7.81338028,9.00528169 C7.81338028,9.49823944 7.40669014,9.89260563 6.91373239,9.89260563 C6.53169014,9.89260563 6.19894366,9.64612676 6.08802817,9.30105634 L5.75528169,8.33978873 L2.05809859,8.33978873 L1.72535211,9.30105634 C1.61443662,9.64612676 1.2693662,9.89260563 0.887323944,9.89260563 C0.394366197,9.89260563 0,9.49823944 0,9.00528169 C0,8.8943662 0.0246478873,8.7834507 0.0616197183,8.6971831 L2.46478873,2.48591549 C2.68661972,1.90669014 3.24119718,1.5 3.90669014,1.5 C4.55985915,1.5 5.12676056,1.90669014 5.34859155,2.48591549 L7.73943662,8.6971831 Z M2.60035211,6.82394366 L5.21302817,6.82394366 L3.90669014,3.10211268 L2.60035211,6.82394366 Z M11.3996479,3.70598592 C12.7552817,3.70598592 14,4.24823944 14,5.96126761 L14,9.07922535 C14,9.52288732 13.6549296,9.89260563 13.2112676,9.89260563 C12.8169014,9.89260563 12.471831,9.59683099 12.4225352,9.19014085 C12.028169,9.6584507 11.3257042,9.95422535 10.5492958,9.95422535 C9.60035211,9.95422535 8.47887324,9.31338028 8.47887324,7.98239437 C8.47887324,6.58978873 9.60035211,6.08450704 10.5492958,6.08450704 C11.3380282,6.08450704 12.040493,6.33098592 12.4348592,6.81161972 L12.4348592,5.98591549 C12.4348592,5.38204225 11.9172535,4.98767606 11.1285211,4.98767606 C10.6602113,4.98767606 10.2411972,5.11091549 9.80985915,5.38204225 C9.72359155,5.43133803 9.61267606,5.46830986 9.50176056,5.46830986 C9.18133803,5.46830986 8.91021127,5.1971831 8.91021127,4.86443662 C8.91021127,4.64260563 9.0334507,4.44542254 9.19366197,4.34683099 C9.87147887,3.90316901 10.6232394,3.70598592 11.3996479,3.70598592 Z M11.1778169,8.8943662 C11.6830986,8.8943662 12.1760563,8.72183099 12.4348592,8.37676056 L12.4348592,7.63732394 C12.1760563,7.29225352 11.6830986,7.11971831 11.1778169,7.11971831 C10.5616197,7.11971831 10.056338,7.45246479 10.056338,8.0193662 C10.056338,8.57394366 10.5616197,8.8943662 11.1778169,8.8943662 Z M0.65625,11.125 L13.34375,11.125 C13.7061869,11.125 14,11.4188131 14,11.78125 C14,12.1436869 13.7061869,12.4375 13.34375,12.4375 L0.65625,12.4375 C0.293813133,12.4375 4.43857149e-17,12.1436869 0,11.78125 C-4.43857149e-17,11.4188131 0.293813133,11.125 0.65625,11.125 Z"></path></svg></span>Method</th><th><span class="icon property-icon"><svg viewBox="0 0 14 14" style="width:14px;height:14px;display:block;fill:rgba(55, 53, 47, 0.4);flex-shrink:0;-webkit-backface-visibility:hidden" class="typesText"><path d="M7,4.56818 C7,4.29204 6.77614,4.06818 6.5,4.06818 L0.5,4.06818 C0.223858,4.06818 0,4.29204 0,4.56818 L0,5.61364 C0,5.88978 0.223858,6.11364 0.5,6.11364 L6.5,6.11364 C6.77614,6.11364 7,5.88978 7,5.61364 L7,4.56818 Z M0.5,1 C0.223858,1 0,1.223858 0,1.5 L0,2.54545 C0,2.8216 0.223858,3.04545 0.5,3.04545 L12.5,3.04545 C12.7761,3.04545 13,2.8216 13,2.54545 L13,1.5 C13,1.223858 12.7761,1 12.5,1 L0.5,1 Z M0,8.68182 C0,8.95796 0.223858,9.18182 0.5,9.18182 L11.5,9.18182 C11.7761,9.18182 12,8.95796 12,8.68182 L12,7.63636 C12,7.36022 11.7761,7.13636 11.5,7.13636 L0.5,7.13636 C0.223858,7.13636 0,7.36022 0,7.63636 L0,8.68182 Z M0,11.75 C0,12.0261 0.223858,12.25 0.5,12.25 L9.5,12.25 C9.77614,12.25 10,12.0261 10,11.75 L10,10.70455 C10,10.4284 9.77614,10.20455 9.5,10.20455 L0.5,10.20455 C0.223858,10.20455 0,10.4284 0,10.70455 L0,11.75 Z"></path></svg></span>Docker + KubernetesPodOperator</th><th><span class="icon property-icon"><svg viewBox="0 0 14 14" style="width:14px;height:14px;display:block;fill:rgba(55, 53, 47, 0.4);flex-shrink:0;-webkit-backface-visibility:hidden" class="typesText"><path d="M7,4.56818 C7,4.29204 6.77614,4.06818 6.5,4.06818 L0.5,4.06818 C0.223858,4.06818 0,4.29204 0,4.56818 L0,5.61364 C0,5.88978 0.223858,6.11364 0.5,6.11364 L6.5,6.11364 C6.77614,6.11364 7,5.88978 7,5.61364 L7,4.56818 Z M0.5,1 C0.223858,1 0,1.223858 0,1.5 L0,2.54545 C0,2.8216 0.223858,3.04545 0.5,3.04545 L12.5,3.04545 C12.7761,3.04545 13,2.8216 13,2.54545 L13,1.5 C13,1.223858 12.7761,1 12.5,1 L0.5,1 Z M0,8.68182 C0,8.95796 0.223858,9.18182 0.5,9.18182 L11.5,9.18182 C11.7761,9.18182 12,8.95796 12,8.68182 L12,7.63636 C12,7.36022 11.7761,7.13636 11.5,7.13636 L0.5,7.13636 C0.223858,7.13636 0,7.36022 0,7.63636 L0,8.68182 Z M0,11.75 C0,12.0261 0.223858,12.25 0.5,12.25 L9.5,12.25 C9.77614,12.25 10,12.0261 10,11.75 L10,10.70455 C10,10.4284 9.77614,10.20455 9.5,10.20455 L0.5,10.20455 C0.223858,10.20455 0,10.4284 0,10.70455 L0,11.75 Z"></path></svg></span>API + SimpleHttpOperator</th></tr></thead><tbody><tr id="57603e92-b09f-49c9-b740-2f0e2e245a51"><td class="cell-title"><p>Pros</p></td><td class="cell-rRHo">- Containerizing jobs brings the benefits of containerization including efficiency, flexibility, and scaling
- Easily allows for downstream dependencies 
- Logs from jobs are shown in Airflow UI</td><td class="cell-:g~E">- Very easy and accessible. Little setup and knowledge of other tools is required</td></tr><tr id="a3c468a6-e359-46b2-9e0c-37504d67fff6"><td class="cell-title"><p>Cons</p></td><td class="cell-rRHo">- Must have Talend Studio to containerize jobs
- More requirements and complexity to setup</td><td class="cell-:g~E">- Not well suited for triggering jobs that have downstream dependencies
- Logs from Talend job are not automatically sent to Airflow</td></tr><tr id="1ab9f4b9-6132-49d5-a523-f8218821ca2d"><td class="cell-title"><p>Requirements</p></td><td class="cell-rRHo">- Talend Studio license
- Docker registry (can use Dockerhub if public is okay)
- Kubernetes</td><td class="cell-:g~E">- Talend cloud license that allows API access</td></tr></tbody></table>

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

![Talend UI](https://assets2.astronomer.io/main/guides/talend/talend_ui_4.png)

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