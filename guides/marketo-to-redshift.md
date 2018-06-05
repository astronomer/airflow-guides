---
title: "Marketo to Redshift"
description: "A guide to outline how to use Airflow to move your data from Marketo to Redshift."
date: 2018-05-23T00:00:00.000Z
slug: "marketo-to-redshift"
heroImagePath: null
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

### 1. Add Connections in Airflow UI

Begin by creating all of the necessary connections in your Airflow UI. To do this, log into your Airflow dashboard and navigate to Admin-->Connections. In order to build this pipeline, you’ll need to create a connection to your Marketo account, your S3 bucket, and your Redshift instance. For more info on how to fill out the fields within your connections, check out our [documentation here](https://docs.astronomer.io/v2/apache_airflow/tutorial/connections.html).

### 2. Clone the plugin

If you haven't done so already, navigate into your project directory and create a `plugins` folder by running  `mkdir plugins` in your terminal. Navigate into this folder by running `cd plugins` and clone the [Marketo Plugin](https://github.com/airflow-plugins/marketo_plugin) using the following command:

`git clone https://github.com/airflow-plugins/marketo_plugin.git`

This will allow you to use the Marketo hook to establish a connection to Marketo and extract data into a file. You will also be able to use the appropriate operators to transfer the Marketo data to S3 and then from S3 to Redshift.

### 3. Copy the DAG file

Navigate back into your project directory and create a `dags` folder by running `mkdir dags`. Copy the [Marketo to Redshift DAG file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/marketo_to_redshift.py) into this folder.

### 4. Customize

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
```

### 5. Test + Deploy

Once you have those credentials plugged into your DAG, test and deploy it!



If you don't have Airflow already set up in your production environment, head over to [our app](https://app.astronomer.io/signup) to get spun up with your own managed instance!

