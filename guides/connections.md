---
title: "Managing your Connections in Apache Airflow"
description: "An overview of how connections work in the Airflow UI."
date: 2018-05-21T00:00:00.000Z
slug: "connections"
heroImagePath: null
tags: ["Connections", "Basics", "Hooks", "Operators"]
---

This document covers how to set up various connections in Airflow. Connections defined by this process are used by [Hooks](https://airflow.apache.org/concepts.html#hooks) in order to encapsulate authentication code and common functions that are used by [Operators](https://airflow.apache.org/concepts.html#operators).

Connections can be maintained in the Airflow Interface (Menu --> Admin --> Connections).

> **Note:** In Airflow 2.0, Provider packages are separate from the core of Airflow, and the Connection Types available are dependent on the provider packages you have installed. For example, in order to see the Snowflake ConnType in the Airflow UI, you'll need the [Snowflake Provider](https://registry.astronomer.io/providers/snowflake) package. If you are running Airflow 2.0 on Astronomer, you can install Provider packages by adding them to your `requirements.txt` file. To learn more, read [Airflow Docs on Provider Packages](https://airflow.apache.org/docs/apache-airflow-providers/index.html) and also browse all available Providers and modules in the [Astronomer Registry](https://registry.astronomer.io/).

### Example Connection Configurations

#### Microsoft SQL Server

* `Host`: localhost
* `Schema`: n/a
* `Login`: _your username_
* `Password`: _blank_
* `Port`: 1433
* `Extras`: n/a

#### MongoDb

* `Host`:
* `Schema`: Authentication Database
* `Login`:
* `Password`:
* `Port`: 27017
* `Extras`: JSON Object of [connection options](https://docs.mongodb.com/manual/reference/connection-string/#connection-string-options)

#### MySQL

* `Host`: localhost
* `Schema`: _your database name_
* `Login`: _your username_
* `Password`: _blank_
* `Port`: 3306
* `Extras`: n/a

#### S3

* `Host`: n/a
* `Schema`: n/a
* `Login`: n/a
* `Password`: n/a
* `Port`: n/a
* `Extras`: {"aws_access_key_id":" ","aws_secret_access_key":" "}

#### Postgres

* `Host`: localhost
* `Schema`: _your database name_
* `Login`: _your username_
* `Password`: _blank_
* `Port`: 5432
* `Extras`: n/a

#### Snowflake

* `Host`: `https://youraccount.yourregion.snowflakecomputing.com/`
* `Schema`: _your schema name_
* `Login`: _your username_
* `Password`: _your password_
* `Port`: n/a
* `Extras`: {"account":" ","role":" ", "warehouse":" ", "database":" ", "region":" "}

#### Azure Data Factory

* `Host`: n/a
* `Schema`: n/a
* `Login`: _your ClientId_
* `Password`: _your Client Secret_
* `Port`: n/a
* `Extras`: {"tenantId":" ","subscriptionId":" ", "resourceGroup":" ", "factory":" "}

#### Azure Blob Storage

* `Host`: n/a
* `Schema`: n/a
* `Login`: _your Storage Account name_
* `Password`: _your Storage Account key_
* `Port`: n/a
* `Extras`: n/a

#### Azure Container Instances

* `Host`: n/a
* `Schema`: n/a
* `Login`: _your ClientId_
* `Password`: _your Client Secret_
* `Port`: n/a
* `Extras`: {"tenantId":" ","subscriptionId":" "}

Depending on the Hook or Operator used, Connections can be called directly in the code:

```python

postgres_query = PostgresOperator(
    task_id="query_one",
    postgres_conn_id=<my_postgres_conn_id>,
    sql=<my_sql_statement>,
    autocommit=True,
)
```


**Note**: The `Schema` field in Airflow can potentially be a source of confusion as many databases have different meanings for the term.  In Airflow a schema refers to the database name to which a connection is being made.  For example, for a Postgres connection the name of the database should be entered into the `Schema` field and the Postgres idea of schemas should be ignored (or put into the `Extras` field) when defining a connection.

### Programmatically Modifying Connections

The Airflow Connections class can be modified programmatically to sync with an external secrets manager:

```python
@provide_session
def create_connections(session=None):
    sources = {"This could come from secrets manager"}
​
    for source in sources:
        try:
            int(source['port'])
        except:
            logger.info("Port is not numeric for source")
            continue

        host = source.get("host", "")
        port = source.get("port", "5439")
        db = source.get("db", "")
        user = source.get("user", "")
        password = source.get("pw", "")
​
        try:
            connection_query = session.query(Connection).filter(Connection.conn_id == source['name'],)
            connection_query_result = connection_query.one_or_none()
            if not connection_query_result:                    
                connection = Connection(conn_id=source['name'], conn_type='postgres', host=host, port=port,
                                        login=user, password=password, schema=db)
                session.add(connection)
                session.commit()
            else:
                connection_query_result.host = host
                connection_query_result.login = user
                connection_query_result.schema = db
                connection_query_result.port = port
                connection_query_result.set_password(password)
                session.add(connection_query_result)
                session.commit()
        except Exception as e:
            logger.info(
                "Failed creating connection"
            logger.info(e)

```

**Note:** The `conn_id` does not have a uniqueness constraint within Airflow, so be sure to delete exist connections before programmatically creating new ones. If two `Connections` have the same name, Airflow will randomly pick which one to use.
