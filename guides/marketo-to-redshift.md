---
title: "Marketo to Redshift"
description: "A guide to outline how to use Airflow to move your data from Marketo to Redshift."
date: 2018-05-23T00:00:00.000Z
slug: "marketo-to-redshift"
hero_image_path: null
tags: ["Building DAGs", "Redshift", "Marketo"]
---

## How to build a Marketo to Redshift pipeline using Airflow

In this guide, we’ll explore how you can use Airflow to move your data from Marketo to Redshift. Note that this is an effective and flexible alternative to point-and-click ETL tools like Segment, Alooma, Xplenty, Stitch, and ETLeap.

Before we get started, be sure you have the following on hand:

* A Marketo account
* An S3 bucket with a valid `aws_access_key_id` and `aws_secret_access_key`
* A Redshift instance with a valid host IP and login information
* An instance of Apache Airflow. You can either set this up yourself if you have devops resources or sign
  up and get going immediately with Astronomer’s managed Airflow service. Note that this guide will use
  commands using the Astronomer CLI to push dags into production and will assume you’ve spun up an Airflow
  instance via Astronomer, but the core code should work the same regardless of how you’re hosting Airflow
* Docker running on your machine

This ongoing DAG pulls the following Marketo objects:
    - Activities
    - Campaigns
    - Leads
    - Lead Lists
    - Programs

Note that, when backfilling, only the leads object is pulled. By default, it begins
pulling since Jan 1, 2013.



### Step 1

Begin by creating all of the necessary connections in your Airflow UI. To do this, log into your Airflow dashboard and navigate to Admin-->Connections. In order to build this pipeline, you’ll need to create a connection to your Marketo account, your S3 bucket, and your Redshift instance. For more info on how to fill out the fields within your connections, check out our [documentation here](https://docs.astronomer.io/v2/apache_airflow/tutorial/connections.html).

### Step 2

Download the Astronomer CLI by opening your terminal and running:

`curl -o- https//cli.astronomer.io/install.sh | bash`

### Step 3

Sign into the CLI by running the command `astro login` and inputting your Astronomer username and password when prompted.

### Step 4

If you haven’t already done so, you’ll want to begin by creating a project directory and navigating into it. To do this, open your terminal and run `mkdir airflow_project_directory`. Then, run `cd airflow_project_directory` to navigate into this folder. While the data we pull won’t actually end up in this folder, this is where we’ll store all of our code that will perform the operation of extracting the data from Marketo and scheduling it to be dumped into Redshift using Airflow.

### Step 5

Once you’ve navigated into your project directory, run `astro init` to initialize the project. This will create a dags and a plugins folder in your project directory.

### Step 6

Navigate into your plugins folder by running `cd plugins` and clone our [Marketo Plugin](https://github.com/airflow-plugins/marketo_plugin) using the following command:

`git clone https://github.com/airflow-plugins/marketo_plugin.git`

This will allow us to use the Marketo hook to establish a connection to Marketo and extract data into a file. We will also be able to use the appropriate operators to transfer the Marketo data to S3 and then from S3 to Redshift.

### Step 7

Now, navigate into your dags folder by running `cd ../dags` and clone our [Example DAGs](https://github.com/airflow-plugins/Example-Airflow-DAGs) repository by running the following command:

`git clone https://github.com/airflow-plugins/Example-Airflow-DAGs.git`

This repo contains the Marketo to Redshift DAG that will act as the orchestrator for your actual data movement. Note that, if you’re only using the Marketo to Redshift DAG, you can delete all of the other DAG files that you downloaded here. This will prevent them from showing up in the Airflow UI once you deploy.

Alternatively, if you'd rather not clone the entire repo and have to delete the extra files, you can just copy the actual [Marketo to Redshift DAG file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/marketo_to_redshift.py)into the dags folder of your project directory.

### Step 8

Open up the [marketo_to_redshift.py file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/marketo_to_redshift.py#L39) from the repo you just cloned in a text editor of your choice and input the following credentials in lines 39-50:

```py
MARKETO_CONN_ID = ''
MARKETO_SCHEMA = ''
REDSHIFT_SCHEMA = ''
REDSHIFT_CONN_ID = ''
S3_CONN_ID = ''
S3_BUCKET = ''
RATE_LIMIT_THRESHOLD = 0.8
RATE_LIMIT_THRESHOLD_TYPE = 'percentage'

hourly_id = '{}_to_redshift_hourly'.format(MARKETO_CONN_ID)
daily_id = '{}_to_redshift_daily_backfill'.format(MARKETO_CONN_ID)
monthly_id = '{}_to_redshift_monthly_backfill'.format(MARKETO_CONN_ID)
```

### Step 9

Once you have those credentials plugged into your DAG, make sure that you’re logged in and run `astro deploy` to push your DAG to your Airflow instance. You can then log into your Airflow UI through app.astronomer.io and see your DAGs running. Once the DAG run succeeds, you will see your Marketo data in the appropriate schema in your Redshift instance.

### Step 10

Now, you can add custom logic into the hooks, operators, and DAGs that you have saved locally. For more info on how to do that, feel free to drop us a note in the webchat below.
