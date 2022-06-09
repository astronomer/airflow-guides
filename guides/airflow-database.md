---
title: "Understanding the Airflow Metadata Database"
description: "An structural walkthrough of Apache Airflow's metadata database, with a full ERD."
date: 2020-11-21T00:00:00.000Z
slug: "airflow-database"
tags: ["Database", "SQL", "Components"]
---

## Overview

The metadata database is a core component of Airflow, and is used to store crucial information about both the configuration of your Airflow environment as well as all metadata relevant for the scheduler regarding past and present DAG and task runs.

A healthy metadata database is critical to a functioning Airflow environment. Losing data stored in the metadata database can not only interfere heavily with the functioning of your DAGs, but can also cause you to be unable to access any history on past DAG runs. As with any core Airflow component, understanding the function and having a  backup and disaster recovery plan in place is key.

In this guide, we will explain everything you need to know about the Airflow metadata database to ensure a healthy Airflow environment, including:

- Specifications for the database instance, including type and sizing considerations
- Important content stored in the database
- Key best practices for interacting with the metadata database
- Different methods for accessing data of interest

> **Note**: This guide provides an informative overview of the inner workings of the Airflow metadata database. We strongly advise against directly modifying the metadata database since this can cause dependency issues and corrupt your Airflow instance!

## Database Specifications

Airflow uses SQLAlchemy and Object Relational Mapping (ORM) in Python to connect and interact with the underlying metadata database from the application layer. Thus, any database supported by [SQLAlchemy](https://www.sqlalchemy.org/) can theoretically be configured to host Airflow's metadata. The most common databases used are:

- Postgres
- MySQL
- MSSQL
- SQLite

Postgres is by far the most common choice, and is generally recommended by the Airflow community. On Astronomer, each Astro Airflow deployment is equipped with a PostgreSQL database for this purpose. When configuring a custom database backend it is also advisable to make sure [your version is fully supported](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html#choosing-database-backend).

Sizing of the metadata database is an important consideration when setting up your Airflow environment for production. Typically, a managed database service will be used so that features like autoscaling and automatic backups can be leveraged. The size you need will depend heavily on the workloads running in your Airflow instance. For reference, when running Airflow locally a 2GB SQLite database will be spun up by default, which is intended for development purposes only. Astro CLI by default will start Airflow with a PostgresSQL database of 1GB.

## Content of the Metadata Database

> **Note**: For many use-cases you can access contents from the metadata database via the Airflow UI or the stable REST API. These points of access are always preferable to querying the metadata database directly!

There are several types of metadata stored in the metadata database.

- Tables related to users' login information and permissions for a specific airflow instance. The names of these tables all start with `ab_`.
- Tables storing information used in DAGs, like variables, connections and XComs.
- Tables storing information about DAG and task runs, which are written to by the scheduler
- Other tables for example storing DAG code in different formats or information about import errors.

Changes to the Airflow metadata database configuration and its schema are very common and happen with almost every minor update. For this reason, prior to Airflow 2.3 you could not downgrade your Airflow instance in place. With Airflow 2.3 the `db downgrade` command was added, providing an option to [downgrade Airflow](https://airflow.apache.org/docs/apache-airflow/2.3.0/usage-cli.html#downgrading-airflow).

> **Note**: Always backup your database before running any database operations!

### Security: Tables related to User Information

A set of tables starting with `ab_` bundles types of permissions for different sections of Airflow together to form roles which are assigned to individual users. As an admin user you can access some of the content of these tables in the Airflow UI under the **Security** tab. It is also possible the query and modify users, roles and permissions via the Airflow REST API.

### Admin: Tables storing Information used in DAGs

DAGs can retrieve and use a variety of information from the metadata database such as:

- [Variables](https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html)
- [Connections](https://www.astronomer.io/guides/connections)
- [XComs](https://www.astronomer.io/guides/airflow-passing-data-between-tasks)
- [Pools](https://www.astronomer.io/guides/airflow-pools/)

The information in these tables can be viewed and modified under the **Admin** tab in the Airflow UI or by using the Airflow REST API.  

### Browse: Tables storing Information about DAG and Task Runs

Besides storing the metadata mentioned in the previous section, the Airflow metadata database is heavily used by the scheduler to keep track of past and current events. The majority of this data can be found under the **Browse** tab in the Airflow UI or queried via the Airflow REST API.

- **DAG Runs** stores information on all past and current Dag Runs including if they were successful, scheduled or manually triggered and detailed timing information
- **Jobs** contains data used by the scheduler to store information about past and current jobs of different types (`SchedulerJob`, `TriggererJob`, `LocalTaskJob`)
- **Audit logs** shows events of various types that were logged to the metadata database (e.g. DAGs being paused or unpaused or tasks being run)
- **Task Instances** contains a record of every task instance (a task with a associated timestamp when it ran) with a variety of attributes such as the priority weight, duration or the URL to the task log
- **Task Reschedule** lists tasks that have been rescheduled
- **Triggers** shows all currently running [triggers](https://www.astronomer.io/guides/deferrable-operators)
- **SLA Misses** keeps track of tasks that missed their [SLA](https://www.astronomer.io/guides/error-notifications-in-airflow/#airflow-slas).

### Other Tables

There are additional tables in the metadata database storing data ranging from DAG tags over serialized DAG code, import errors to current states of sensors. Some of the information in these tables will be visible in the Airflow UI in various places:

- **Browse** -> **DAG Dependencies** shows a visual representation of DAG Dependencies
- The source code of DAGs can be found by clicking on a DAG name from the main view and then navigating to the **Code** view
- Import errors will show up on top of your list of dags if they occur
- DAG tags will show up underneath their respective DAG with a cyan background.

Most of the information in these tables is accessible via the Airflow REST API.

## Airflow Metadata Database Best Practices

1. When up- or downgrading Airflow, which commonly includes changes to your metadata database, make sure you always have a backup of your metadata database and follow the [recommended steps for changing Airflow versions](https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading.html?highlight=upgrade): backup the database, check for deprecated features, pause all DAGs, and make sure no tasks are running.

2. Use caution when [pruning old records](https://airflow.apache.org/docs/apache-airflow/stable/usage-cli.html#purge-history-from-metadata-database) from your database with `db clean`. The `db clean` command allows you to delete records older than `--clean-before-timestamp` from all metadata database tables or a list of tables specified.

3. Keep in mind that every time you access data from the metadata database from within a DAG (for example by fetching a variable, pulling from XCom or using a connection ID) you will make a connection to the metadata database which requires compute resources. It is therefore best practice to try to keep these actions within tasks, which will only create a connection to the database at run time. If they are written as top level code, connections will be created every time the scheduler parses the DAG file (every 30 seconds by default!).

4. Memory in the Airflow metadata database can be limited depending on your setup and running low on memory in your metadata database can cause performance issues in Airflow. This is one of the many reasons why we highly advise against moving large amounts of data via XCom, and recommend using a cleanup and archiving mechanism in any production deployments.

5. Since the metadata database is critical for the scalability and resiliency of your Airflow deployment, it is best practice at least for production Airflow deployments to use a managed database service, for example [AWS RDS](https://aws.amazon.com/rds/) or [Google Cloud SQL](https://cloud.google.com/sql).

## Example Queries

The preferred methods for retrieving data from the metadata database are using the Airflow UI or making a GET request to the [stable Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html). Between the UI and API large parts of the metadata database can be viewed without the risk of accidentally making harmful changes to the database that direct querying would pose. For use cases where neither the Airflow UI nor the REST API can provide sufficient data it is recommended to use SQLAlchemy to query the metadata database in order to have an additional layer of abstraction on top of the tables.







## Example: Retrieving Number of Successfully Completed Tasks

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


### Example: Retrieve all DAG dependencies

while there is a graphical interface the API does not offer this?
use models so the code wont break with every version! this is why it makes sense to use sqlalchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from airflow.models.serialized_dag import SerializedDagModel

conn_url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'

engine = create_engine(conn_url)

dag_id = "example_dag_advanced"

with Session(engine) as session:
    result = session.query(SerializedDagModel).filter(SerializedDagModel.dag_id == dag_id).first()
    print(result.get_dag_dependencies())
```


### Example: Retrieving Alembic Version

> **Note**: For many use-cases you can access contents from the metadata database via the Airflow UI or the stable REST API. These points of access are always preferable to querying the metadata database directly!

For use cases where neither the Airflow UI nor the REST API can provide sufficient data it is recommended to use SQLAlchemy to query the metadata database.

The query below retrieves the current [alembic version id](https://alembic.sqlalchemy.org/en/latest/).

No SQLAlchemy model available -> direct querying, might break with version changes

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
