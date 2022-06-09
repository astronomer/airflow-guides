---
title: "Understanding the Airflow Metadata Database"
description: "An structural walkthrough of Apache Airflow's metadata database, with a full ERD."
date: 2020-11-21T00:00:00.000Z
slug: "airflow-database"
tags: ["Database", "SQL", "Components"]
---

## Overview

The metadata database is a core component of Airflow, and is used to store crucial information about both the configuration of your Airflow environment as well as all metadata relevant for the scheduler regarding past and present DAG and task runs.

Loosing this data can not only interfere heavily with the functioning of your DAGs, for example if needed variables or connections are lost, but also cause you to be unable to access any history on past DAG runs or cause critical errors in your Airflow instance. This is why we highly recommend to have a backup and disaster recovery plan for your metadata database in place. The ideal tools and set up will depend on your organization's needs and use case.

In this guide we will explain Airflow metadata database specifications, what kind of content is saved, what the key best practises are when working with metadata database related commands as well as different ways you can access data of interest.

> **Note**: This guide provides an informative overview of the inner workings of the Airflow metadata database. We strongly advise against directly modifying the metadata database since this can cause dependency issues and corrupt your Airflow instance!

## Database Specifications

Airflow uses SQLAlchemy and Object Relational Mapping (ORM) in Python to connect and interact with the underlying metadata database from the application layer. Thus, any database supported by [SQLAlchemy](https://www.sqlalchemy.org/) can theoretically be configured to host Airflow's metadata. On Astronomer, each Airflow deployment is equipped with a PostgreSQL database for this purpose. PostgresSQL is both the most common choice and recommended to use for the metadata database by the Airflow community.

When running Airflow locally by default a 2GB SQLite database will be spun up, which is intended for development purposes only. Astro CLI by default will start Airflow with a PostgresSQL database of 1GB. When configuring a custom database backend it is advisable to make sure [your version is fully supported](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html#choosing-database-backend) by the Airflow.


## Content of the Metadata Database

> **Note**: For many use-cases you can access contents from the metadata database via the Airflow UI or the stable REST API. These points of access are always preferable to querying the metadata database directly!

There are several types of metadata stored in the metadata database.

- Tables related to users' login information and permissions for a specific airflow instance. The names of these tables all start with `ab_`.
- Tables storing input like variables, connections and XComs.
- Tables the scheduler uses to organize DAG and task runs.  
- Other tables for example to keep track of the current [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) version or of tasks that missed their [SLA](https://www.astronomer.io/guides/error-notifications-in-airflow/#airflow-slas).

Changes to the Airflow metadata database configuration and its schema are very common and happen with almost every minor update. For this reason, prior to Airflow 2.3 you could not downgrade your Airflow instance in place. With Airflow 2.3 the `db downgrade` command was added, providing an option to [downgrade Airflow](https://airflow.apache.org/docs/apache-airflow/2.3.0/usage-cli.html#downgrading-airflow).

> **Note**: Always backup your database before running any database operations!

### Security: Tables related to User Information

tab **Security**

### Admin: Tables Information used in DAGs

tab **Admin**

### Browse: Tables storing Information about DAG and Task Runs

tab **Browse**

### Other Tables

While changes to the schema happen regularly, key content is stored in the same tables spanning several recent versions.

A set of tables starting with `ab_` bundles types of permissions for different sections of Airflow together to form roles which are assigned to individual users. As an admin user you can access some of the content of the tables in the Airflow UI under the **Security** tab.

Metadata which can be found under the **Admin** tab in the Airflow UI such as variables, [connections](https://www.astronomer.io/guides/connections) and [XComs](https://www.astronomer.io/guides/airflow-passing-data-between-tasks) are stored in their respective tables as well as [slots assigned to pools](https://www.astronomer.io/guides/airflow-pools/) and [SLA misses](https://www.astronomer.io/guides/error-notifications-in-airflow/#airflow-slas).  

Besides storing the metadata mentioned above, the Airflow metadata database is heavily used by the scheduler to keep track of past and current events.

- The `job` table is used by the scheduler to store information about past and current DAG run scheduling in different states (running, success, failed). You can view this table in the Airflow UI by navigating to **Browse** -> **Jobs**.
- The `log` table is used to actively log events of various types (e.g. cli_task run, dagrun_failed, trigger, paused among many others) to the metadata database. You can view this table in the Airflow UI by navigating to **Browse** -> **Audit Logs**.
- In the `dag_run` table all data related to current and past dag_runs is stored. (**Browse** -> **Dag Runs**).
- The `task instance` table (**Browse** -> **Task Instances**) keeps a detailed record of previous and currently running tasks.

There are many more tables in the metadata database storing data ranging from DAG tags over serialized DAG code to current states of sensors and rescheduled tasks.

## Airflow Metadata Database Best Practices

1. When up- or downgrading Airflow, which commonly includes changes to your metadata database make sure you always have a backup of your metadata database and follow the [recommended steps for changing Airflow versions](https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading.html?highlight=upgrade): backup the database, check for deprecated features, pause all DAGs and make sure no tasks are running.

2. Use caution when [pruning old records](https://airflow.apache.org/docs/apache-airflow/stable/usage-cli.html#purge-history-from-metadata-database) from your database with `db clean`. The `db clean` command allows you to delete records older than `--clean-before-timestamp` from all metadata database tables or a list of tables specified.

3. Keep in mind that every time you access data from the metadata database from within a DAG (for example by fetching a variable, pulling from XCom or using a connection ID) you will make a connection to the metadata database which needs compute resources. It is therefore best practice to try to keep these actions within tasks, which will only create a connection to the database at run time. If they are written as top level code, connections will be created every time the scheduler parses the DAG file (every 30 seconds by default!).

4. Memory in the Airflow metadata database can be limited depending on your setup and running low on memory in your metadata database can cause performance issues in Airflow. This is one of the many reasons why we highly advise against moving large amounts of data via XCom, and recommend using a cleanup and archiving mechanism in any production deployments.

5. Since the metadata database is critical for the scalability and resiliency of your Airflow deployment, it is best practice at least for production Airflow deployments to use a managed database service, for example [AWS RDS](https://aws.amazon.com/rds/) or [Google Cloud SQL](https://cloud.google.com/sql).

## Example Queries

### Example: Retrieving Number of Successfully Completed Tasks

A common reason users may want to access the metadata database is to get metrics like the total count of successfully completed tasks.

In the Airflow UI you can navigate to **Browse** -> **Task Instances** and filter the task instances for all with a state of `success`. The `Record Count` will be on the right side of your screen.

![Count successful tasks Airflow UI](<https://assets2.astronomer.io/main/guides/your-guide-folder/successful_tasks_UI.png>)

Using the [stable REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#section/Overview) to query the metadata database is an equally valid way to get information. Make sure you have [correctly authorized API use](https://airflow.apache.org/docs/apache-airflow/stable/security/api.html) in your Airflow instance and set the `ENDPOINT_URL` (for local development: `http://localhost:8080/`).

```python
import requests

ENDPOINT_URL = "http://localhost:8080/"
user_name = "admin"
password = "admin"

# query the API for task instances from all dags and all dag runs (~)
req = requests.get(f"{ENDPOINT_URL}/api/v1/dags/~/dagRuns/~/taskInstances?state=success",  auth=(user_name, password))
print(req.json()['total_entries'])
```

### Example: Unpause a list of paused DAGs


### Example: Pause all active DAGs


### Example: Delete a DAG


### Example: Retrieving Alembic Version

> **Note**: For many use-cases you can access contents from the metadata database via the Airflow UI or the stable REST API. These points of access are always preferable to querying the metadata database directly!

For use cases where neither the Airflow UI nor the REST API can provide sufficient data it is recommended to use SQLAlchemy to query the metadata database.

The query below retrieves the current [alembic version id](https://alembic.sqlalchemy.org/en/latest/).

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

conn_url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'

engine = create_engine(conn_url)

stmt = """SELECT version_num
        FROM alembic_version;"""

with Session(engine) as session:
    result = session.execute(stmt)
    print(result.all()[0][0])
```
