---
title: "Understanding the Airflow Metadata Database"
description: "An structural walkthrough of Apache Airflow's metadata database, with a full ERD."
date: 2020-11-21T00:00:00.000Z
slug: "airflow-database"
tags: ["Database", "SQL", "Components"]
---

## Overview

> **Note**: This guide provides an informative overview of the inner workings of the Airflow metadata database. We strongly advise against directly modifying the metadata database since this can cause dependency issues and corrupt your Airflow instance!

The metadata database in Airflow is used to store crucial information about both the configuration of your Airflow environment as well as all metadata relevant for the scheduler regarding DAGs, tasks and individual runs.

In this guide we will explain what kind of data Airflow saves in its metadata database, give an overview over key tables and Airflow specific database best practises, as well as talk about disaster recovery in Airflow.

## Content of the Metadata Database

Airflow uses SQLAlchemy and Object Relational Mapping (ORM) in Python to connect and interact with the underlying metadata database from the application layer. Thus, any database supported by [SQLAlchemy](https://www.sqlalchemy.org/) can theoretically be configured to host Airflow's metadata. On Astronomer, each Airflow deployment is equipped with PostgreSQL database for this purpose.

There are several types of metadata stored in the metadata database. One group of tables handles users' login information and permissions for a specific airflow instance, another set of tables deals with storing variables, connections and XComs while other tables contain data the scheduler uses to organize DAG and task runs.

Changes to the Airflow metadata database configuration and its schema are very common and happen with almost every minor update. This used to be the reason why you could not downgrade your Airflow instance before Airflow version 2.3. With Airflow 2.3 the `db downgrade` command was added, providing an option to [downgrade Airflow](https://airflow.apache.org/docs/apache-airflow/2.3.0/usage-cli.html#downgrading-airflow).

> **Note** Always backup your database before running any database operations!

While changes to the schema happen regularly, key content is stored in the same tables spanning several recent versions.

A set of tables starting with `ab_*` bundles types of permissions for different sections of Airflow together to form roles which are assigned to individual users. As an admin user you can access some of the content of the tables in the Airflow UI under the **Security** tab.

Metadata which can be found under the **Admin** tab in the Airflow UI such as variables, [connections](https://www.astronomer.io/guides/connections) and [XComs](https://www.astronomer.io/guides/airflow-passing-data-between-tasks) are stored in their respective tables as well as [slots assigned to pools](https://www.astronomer.io/guides/airflow-pools/) and [SLA misses](https://www.astronomer.io/guides/error-notifications-in-airflow/#airflow-slas).  

Besides storing the metadata mentioned above, the Airflow metadata database is heavily used by the scheduler to keep track of past and current events.

- The `job` table is used by the scheduler to store information about past and current DAG run scheduling in different states (running, success, failed). You can view this table in the Airflow UI by navigating to **Browse** -> **Jobs**.
- The `log` table is used to actively log events of various types (e.g. cli_task run, dagrun_failed, trigger, paused among many others) to the metadata database. You can view this table in the Airflow UI by navigating to **Browse** -> **Audit Logs**.
- In the `dag_run` table all data related to current and past dag_runs is stored. (**Browse** -> **Dag Runs**).
- The `task instance` table (**Browse** -> **Task Instances**) keeps a detailed record of previous and currently running tasks.

There are many more tables in the metadata database storing data ranging from DAG tags over serialized DAG code to current states of sensors and rescheduled tasks.

## Airflow Metadata Database Best Practices

1. When up- or downgrading Airflow, which commonly includes changes to your metadata database make sure you always have a backup of your metadata database and follow the recommended steps for changing Airflow versions: backup the database, check for deprecated features, pause all DAGs and make sure no tasks are running.

2. Use caution when [pruning old records](https://airflow.apache.org/docs/apache-airflow/stable/usage-cli.html#purge-history-from-metadata-database) from your database with `db clean`.

3. Keep in mind that every time you access data from the metadata database from within a DAG (for example by fetching a variable, pulling from XCom or using a connection ID) you will make a connection to the metadata database which needs compute resources. It is therefore best practise to try to keep these actions within tasks so these connections are not created every time the scheduler parses the DAG file (every 30 seconds!).

4. Memory in the Airflow metadata database is limited depending on your setup. Astro CLI uses a Postgres database of the size of 1GB while local Airflow by default will use a 2GB SQLite database. This is one of the many reasons why we highly advise against moving large amounts of data via XCom.

5. Because of limited memory in the metadata database it is recommended to use a cleanup and archive mechanism in deployment (for example [Amazon Redshift](https://aws.amazon.com/redshift/)).

## Disaster Recovery

> [Astronomer customers](https://www.astronomer.io/) can profit from a comprehensive backup and recovery plan that will be configured according to your needs.

As mentioned above the metadata database contains all information about your past and current DAG runs as well as configurations of variables, roles and permissions, connections and XComs among other data. Loosing this data can interfere with the functioning of your DAGs (for example in case of loss of necessary variables or connections).

The tools and setup you use will depend on your organization's needs and use case. Astronomer recommends the open source software [Velero](https://velero.io/) for both backup and restore operations. Astronomer Documentation provides an [in-depth guide to disaster recovery using Velero](https://docs.astronomer.io/software/disaster-recovery).
