---
title: "Github API to Redshift with Airflow"
description: "Use Airflow to ingest data from the Github API into Redshift"
date: 2018-05-21T00:00:00.000Z
slug: "github-to-redshift"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/GithubToRedshit_preview.png"
tags: ["Building DAGs", "Redshift", "Github"]
---

In this guide, we’ll explore how you can use Airflow to move your data from Github to Redshift. Note that this is an effective and flexible alternative to point-and-click ETL tools like Segment, Alooma, Xplenty, Stitch, and ETLeap.

Before we get started, be sure you have the following on hand:

* A Github account
* An S3 bucket with a valid `aws_access_key_id` and `aws_secret_access_key`
* A Redshift instance with a valid host IP and login information
* An instance of Apache Airflow. You can either set this up yourself if you have devops resources or sign
  up and get going immediately with Astronomer’s managed Airflow service. Note that this guide will use
  commands using the Astronomer CLI to push dags into production and will assume you’ve spun up an Airflow
  instance via Astronomer, but the core code should work the same regardless of how you’re hosting Airflow
* Docker running on your machine

This DAG copies the following objects:

* commits
* issue_comments
* issues
* repositories
* members
* pull_requests

### 1. Add Connections in Airflow UI

Begin by creating all of the necessary connections in your Airflow UI. To do this, log into your Airflow dashboard and navigate to Admin-->Connections. In order to build this pipeline, you’ll need to create a connection to your Github account, your S3 bucket, and your Redshift instance. For more info on how to fill out the fields within your connections, check out our [documentation here](https://docs.astronomer.io/v2/apache_airflow/tutorial/connections.html).

### 2. Clone the plugin

If you haven't done so already, navigate into your project directory and create a `plugins` folder by running  `mkdir plugins` in your terminal. Navigate into this folder by running `cd plugins` and clone the [Github Plugin](https://github.com/airflow-plugins/github_plugin) using the following command:

`git clone https://github.com/airflow-plugins/github_plugin.git`

This will allow you to use the Github hook to establish a connection to Github and extract data into a file. You will also be able to use the appropriate operators to transfer the Github data to S3 and then from S3 to Redshift.

### 3. Copy the DAG file

Navigate back into your project directory and create a `dags` folder by running `mkdir dags`. Copy the [Github to Redshift DAG file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/github_to_redshift.py) into this folder.

### 4. Customize

Open up the [github_to_redshift.py file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/github_to_redshift.py#L29) that you just copied in a text editor of your choice and input the following credentials into lines 29-35:
```
S3_CONN_ID = ''
S3_BUCKET = ''
REDSHIFT_CONN_ID = ''
REDSHIFT_SCHEMA = ''
ORIGIN_SCHEMA = ''
SCHEMA_LOCATION = ''
LOAD_TYPE = ''
```

### 5. Test + Deploy

Once you have those credentials plugged into your DAG, test and deploy it!



If you don't have Airflow already set up in your production environment, head over to [our app](https://app.astronomer.io/signup) to get spun up with your own managed instance!
