---
title: "IMAP to Redshift with Airflow"
description: "Use Airflow to ingest data from an IMAP server to Redshift"
date: 2018-05-21T00:00:00.000Z
slug: "imap-to-redshift"
heroImagePath: null
tags: ["Building DAGs", "Redshift", "IMAP"]
---

In this guide, we’ll explore how you can use [Apache Airflow](https://airflow.apache.org/) to move your data from an IMAP server to Redshift. Note that this is an effective and flexible alternative to point-and-click ETL tools like [Segment](https://segment.com), [Alooma](https://alooma.com), [Xplenty](https://xplenty.com), [Stitch](https://stitchdata.com), and [ETLeap](https://etleap.com/).

Before we get started, be sure you have the following on hand:

* An accessible IMAP server
* An S3 bucket with a valid `aws_access_key_id` and `aws_secret_access_key`
* A Redshift instance with a valid host IP and login information
* An instance of Apache Airflow. You can either set this up yourself if you have devops resources or sign
  up and get going immediately with Astronomer’s managed Airflow service. Note that this guide will use
  commands using the Astronomer CLI to push dags into production and will assume you’ve spun up an Airflow
  instance via Astronomer, but the core code should work the same regardless of how you’re hosting Airflow
* Docker running on your machine

### 1. Add Connections in Airflow UI

Begin by creating all of the necessary connections in your Airflow UI. To do this, log into your Airflow dashboard and navigate to Admin-->Connections. In order to build this pipeline, you’ll need to create a connection to your IMAP server, your S3 bucket, and your Redshift instance. For more info on how to fill out the fields within your connections, check out our [documentation here](https://docs.astronomer.io/v2/apache_airflow/tutorial/connections.html).

### 2. Clone the plugin

If you haven't done so already, navigate into your project directory and create a `plugins` folder by running  `mkdir plugins` in your terminal.Navigate into this folder by running `cd plugins` and clone the [IMAP](https://github.com/airflow-plugins/imap_plugin) using the following command:

`git clone https://github.com/airflow-plugins/imap_analytics_plugin.git`

This will allow you to use the IMAP hook to access your IMAP server, search your inbox for emails with specific subjects, pull in the csv attachments of the emails, and store them in S3 using the IMAP to S3 operator.

### 3. Copy the DAG file

Navigate back into your project directory and create a `dags` folder by running `mkdir dags`. Copy the [IMAP to Redshift DAG file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/imap_to_redshift.py) into this folder.

### 4. Customize

Open up the [google_analytics_to_redshift.py file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/imap_to_redshift.py#L25) that you just copied in a text editor of your choice and input the following credentials into lines 25-34:

```py
IMAP_CONN_ID = ''
IMAP_EMAIL = ''

S3_CONN_ID = ''
S3_BUCKET = ''

REDSHIFT_SCHEMA = ''
REDSHIFT_CONN_ID = ''
```

### 5. Test + Deploy

Once you have those credentials plugged into your DAG, test and deploy it!

If you don't have Airflow already set up in your production environment, head over to [our app](https://app.astronomer.io/signup) to get spun up with your own managed instance!
