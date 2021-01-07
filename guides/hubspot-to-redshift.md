---
title: "Hubspot API to Redshift with Airflow"
description: "Use Airflow to ingest CRM data from the Hubspot API into Redshift"
date: 2018-05-23T00:00:00.000Z
slug: "hubspot-to-redshift"
heroImagePath: "https://assets.astronomer.io/website/img/guides/HubspotToRedshift_preview.png"
tags: ["Integrations", "Connections", "DAGs"]
---
<!-- markdownlint-disable-file -->
In this guide, we’ll explore how you can use [Apache Airflow](https://airflow.apache.org/) to move your CRM data from Hubspot to Redshift. Note that this is an effective and flexible alternative to point-and-click ETL tools like [Segment](https://segment.com), [Alooma](https://alooma.com), [Xplenty](https://www.xplenty.com), [Stitch](https://stitchdata.com), and [ETLeap](https://etleap.com/).

Before we get started, be sure you have the following on hand:

* A Hubspot account
* An S3 bucket with a valid `aws_access_key_id` and `aws_secret_access_key`
* A Redshift instance with a valid host IP and login information
* An instance of Apache Airflow. You can either set this up yourself if you have devops resources or sign
  up and get going immediately with Astronomer’s managed Airflow service. Note that this guide will use
  commands using the Astronomer CLI to push dags into production and will assume you’ve spun up an Airflow
  instance via Astronomer, but the core code should work the same regardless of how you’re hosting Airflow
* Docker running on your machine

This dag pulls the following endpoints and inserts data to the following table/subtable based on the followings schedules:

*NOTE:* Only endpoints with the appropriate scope will be included in this dag.

The associated scope to the various endpoints can be found in the "scope" field within the endpoints array below. The scope available to a given token can be found by passing the associated token to: `https://api.hubapi.com/oauth/v1/access-tokens/{OAUTH_TOKEN}`

*NOTE:* The contacts table and associated subtables are built based on an incrementing contact id that is stored as an Airflow Variable with the
naming convention "INCREMENTAL_KEY__{DAG_ID}_{TASK_ID}_vidOffset" at the end of each run and then pulled on the next to be used as an offset. As such, while accessing the Contacts endpoint, "max_active_runs" should be set to 1 to avoid pulling the same incremental key offset and therefore pulling the same data twice.

* Campaigns - Rebuild
* Companies - Rebuild
* Contacts - Append - Built based on incremental contact id
  * Form Submissions - Append
  * Identity Profiles - Append
  * List Memberships - Append
  * Merge Audits - Append
* Deals - rebuild
  * Associations_AssociatedVids - Append
  * Associations_AssociatedCompanyVids - Append
  * Associations_AssociatedDealIds - Append
* Deal Pipelines - Rebuild
* Engagements - Rebuild
  * Associations - Rebuild
  * Attachments - Rebuild
* Events - Append - Built based on incremental date
* Forms - Rebuild
  * Field Groups - Rebuild
* Keywords - Rebuild
* Lists - Rebuild
  * Filters - Rebuild
* Owners - Rebuild
  * Remote List - Rebuild
* Social - Rebuild
* Timeline - Append - Built based on incremental date
* Workflow - Rebuild
  * Persona Tag Ids - Rebuild
  * Contact List Ids Steps - Rebuild

Before we get started, be sure you have the following on hand:

* A Hubspot account with valid credentials
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

Begin by creating all of the necessary connections in your Airflow UI. To do this, log into your Airflow dashboard and navigate to Admin-->Connections. In order to build this pipeline, you’ll need to create a connection to your Hubspot account, your S3 bucket, and your Redshift instance. For more info on how to fill out the fields within your connections, check out our [documentation here](https://www.astronomer.io/guides/connections/).

### 2. Clone the plugin

If you haven't done so already, navigate into your project directory and create a `plugins` folder by running  `mkdir plugins` in your terminal.Navigate into this folder by running `cd plugins` and clone the [Hubspot Plugin](https://github.com/airflow-plugins/hubspot_plugin) using the following command:

`git clone https://github.com/airflow-plugins/hubspot_plugin.git`

This will allow you to use the Hubspot hook to establish a connection to Hubspot and extract data into a file. You will also be able to use the appropriate operators to transfer the Hubspot data to S3 and then from S3 to Redshift.

### 3. Copy the DAG file

Navigate back into your project directory and create a `dags` folder by running `mkdir dags`. Copy the [Hubspot to Redshift DAG file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/hubspot_to_redshift.py) into this folder.

### 4. Customize

Open up the [hubspot_to_redshift.py file](https://github.com/airflow-plugins/Example-Airflow-DAGs/blob/master/etl/hubspot_to_redshift.py#L74) from the repo you just cloned in a text editor of your choice and input the following credentials in lines 74-78:

```python
S3_CONN_ID = ''
S3_BUCKET = ''
HUBSPOT_CONN_ID = ''
REDSHIFT_SCHEMA = ''
REDSHIFT_CONN_ ''
```

### 5. Test + Deploy

Once you have those credentials plugged into your DAG, test and deploy it!

If you don't have Airflow already set up in your production environment, head over to [our getting started guide](https://astronomer.io/docs/getting-started) to get spun up with your own managed instance!
