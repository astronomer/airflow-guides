---
title: "Facebook Ads API to Redshift with Airflow"
description: "Use Airflow to ingest ad data from the Facebook Ads API into Redshift"
date: 2018-05-21T00:00:00.000Z
slug: "facebook-ads-to-redshift"
heroImagePath: "https://assets.astronomer.io/website/img/guides/FBToRedshift_preview.png"
tags: ["DAGs", "Integrations", "Connections"]
---

In this guide, we’ll explore how you can use [Apache Airflow](https://airflow.apache.org/) to move your ad data from Facebook Ads to Redshift. Note that this is an effective and flexible alternative to point-and-click ETL tools like [Segment](https://segment.com), [Alooma](https://alooma.com), [Xplenty](https://www.xplenty.com), [Stitch](https://stitchdata.com), and [ETLeap](https://etleap.com/).

Before we get started, be sure you have the following on hand:

- A Facebook Ads
- An S3 bucket with a valid `aws_access_key_id` and `aws_secret_access_key`
- A Redshift instance with a valid host IP and login information
- An instance of Apache Airflow. You can either set this up yourself if you have devops resources or sign up and get going immediately with Astronomer’s managed Airflow service. Note that this guide will use commands using the Astronomer CLI to push dags into production and will assume you’ve spun up an Airflow instance via Astronomer, but the core code should work the same regardless of how you’re hosting Airflow
- Docker running on your machine

### This DAG will create four breakdown reports:

- age_gender
- device_platform
- region_country
- no_breakdown

### The standard fields included in each report are as follows:

- account_id
- ad_id
- adset_id
- ad_name
- adset_name
- campaign_id
- date_start
- date_stop
- campaign_name
- clicks
- cpc
- cpm
- cpp
- ctr
- impressions
- objective
- reach
- social_clicks
- social_impressions
- social_spend
- spend
- total_unique_actions

### 1. Add Connections in Airflow UI

Begin by creating all of the necessary connections in your Airflow UI. To do this, log into your Airflow dashboard and navigate to Admin-->Connections. In order to build this pipeline, you’ll need to create a connection to your Facebook Ads account, your S3 bucket, and your Redshift instance. For more info on how to fill out the fields within your connections, check out our [documentation here](https://astronomer.io/guides/connections).

### 2. Clone the plugin

If you haven't done so already, navigate into your project directory and create a `plugins` folder by running  `mkdir plugins` in your terminal.Navigate into this folder by running `cd plugins` and clone the [Facebook Ads Plugin](https://github.com/airflow-plugins/facebook_ads_plugin) using the following command:

`git clone https://github.com/airflow-plugins/facebook_ads_plugin.git`

This will allow you to use the Facebook Ads hook to establish a connection to Facebook Ads and extract data into a file. You will also be able to use the appropriate operators to transfer the Facebook Ads data to S3 and then from S3 to Redshift.

### 3. Copy the DAG file

Navigate back into your project directory and create a `dags` folder by running `mkdir dags`. Copy the [Facebook Ads to Redshift DAG file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/facebook_ads_to_redshift.py) into this folder.

### 4. Customize

Open up the [facebook_ads_to_redshift.py file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/facebook_ads_to_redshift.py#L51) from the repo you just cloned in a text editor of your choice and fill out the following fields fin lines 51-56:

```python
FACEBOOK_CONN_ID = ''
ACCOUNT_ID = ''
S3_BUCKET = ''
S3_CONN_ID = ''
REDSHIFT_CONN_ID = ''
REDSHIFT_SCHEMA = ''
```

### 5. Test + Deploy

Once you have those credentials plugged into your DAG, test and deploy it!

If you don't have Airflow already set up in your production environment, head over to [our getting started guide](https://astronomer.io/docs/getting-started) to get spun up with your own managed instance!
