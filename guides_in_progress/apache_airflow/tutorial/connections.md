---
title: Apache Airflow Connections
sidebar: platform_sidebar
---

This document covers how to set up various connections in Airflow. Connections defined by this process are used by [Hooks](https://airflow.apache.org/concepts.html#hooks) in order to encapsulate authentication code and common functions that are used by [Operators](https://airflow.apache.org/concepts.html#operators).

Connections can be maintained in the Airflow Interface (Menu --> Admin --> Connections).

### Example Connection Configurations

##### Microsoft SQL Server
* `Host`: localhost
* `Schema`: n/a
* `Login`: _your username_
* `Password`: _blank_
* `Port`: 1433
* `Extras`: n/a

##### MongoDb
* `Host`:
* `Schema`: Authentication Database
* `Login`:
* `Password`:
* `Port`: 27017
* `Extras`: JSON Object of [connection options](https://docs.mongodb.com/manual/reference/connection-string/#connection-string-options)

##### MySQL
* `Host`: localhost
* `Schema`: _your database name_
* `Login`: _your username_
* `Password`: _blank_
* `Port`: 3306
* `Extras`: n/a

##### S3
* `Host`: n/a
* `Schema`: n/a
* `Login`: n/a
* `Password`: n/a
* `Port`: n/a
* `Extras`: {"aws_access_key_id":" ","aws_secret_access_key":" "}

##### Postgres
* `Host`: localhost
* `Schema`: _your database name_
* `Login`: _your username_
* `Password`: _blank_
* `Port`: 5432
* `Extras`: n/a

### A note about the Schema field
The `Schema` field in Airflow can potentially be a source of confusion as many databases have different meanings for the term.  In Airflow a schema refers to the database name to which a connection is being made.  For example, for a Postgres connection the name of the database should be entered into the `Schema` field and the Postgres idea of schemas should be ignored (or put into the `Extras` field) when defining a connection.
