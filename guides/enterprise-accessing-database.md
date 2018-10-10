---
title: "Accessing the Underlying Database within Astronomer Enterprise"
description: "A guide to accessing the database that backs Astronomer"
date: 2018-10-09T00:00:00.000Z
slug: "enterprise-accessing-database"
heroImagePath: null
tags: ["Astronomer Platform", "admin-docs"]
---

Sometimes it is necessary to access the database that backs the Astronomer platform. This guide will walk through the necessary steps to do so and assumes Postgres although the process is similar for MySQL.

### Retrieving "astronomer-bootstrap" secret
To get the connection information for the Postgres instance included in your Astronomer install, you will need to retrieve "astronomer-bootstrap" secret. The namespace here is the global namespace found at the beginning of all your pods.
```
$ kubectl get secret astronomer-bootstrap --namespace astronomer-demo -o yaml
apiVersion: v1
data:
  connection: cG9zdGdyZXM6Ly9leGFtcGxlLXVzZXI6UEBTU1dPUkRAZXhhbXBsZS1wb3N0Z3Jlcy5hc3Ryb25vbWVyLWRlbW86NTQzMg==
kind: Secret
metadata:
  creationTimestamp: 2018-10-09T12:00:00Z
  name: astronomer-bootstrap
  namespace: astronomer-demo
  resourceVersion: "1054144"
  selfLink: /api/v1/namespaces/astronomer-demo/secrets/astronomer-bootstrap
  uid: 6b99c4c4-b931-22i8-458e-04210a6713d7
type: Opaque
```

### Decode the connection string
Once retrieved, decode the resulting connection string to get the relevant connection information. This can be done using the base `echo` command, decoding as base64.
```
$ echo 'cG9zdGdyZXM6Ly9leGFtcGxlLXVzZXI6UEBTU1dPUkRAZXhhbXBsZS1wb3N0Z3Jlcy5hc3Ryb25vbWVyLWRlbW86NTQzMg==' | base64 --decode
postgres://example-user:P@SSWORD@example-postgres.astronomer-demo
```

If accessing the database often, it is recommended that you create a new user with scoped permissions so you are not logging in with superuser credentials.


## Examples
Additional useful queries can be found at the [Useful Airflow Queries Guide](https://www.astronomer.io/guides/airflow-queries/).

### Removing old DAG records
```
DELETE FROM meteoric_meteorite_9699_airflow.dag WHERE dag_id = '{DAG_ID}';
DELETE FROM meteoric_meteorite_9699_airflow.log WHERE dag_id = '{DAG_ID}';
DELETE FROM meteoric_meteorite_9699_airflow.xcom WHERE dag_id = '{DAG_ID}';
DELETE FROM meteoric_meteorite_9699_airflow.task_instance WHERE dag_id = '{DAG_ID}';
DELETE FROM meteoric_meteorite_9699_airflow.sla_miss WHERE dag_id = '{DAG_ID}';
DELETE FROM meteoric_meteorite_9699_airflow.job WHERE dag_id = '{DAG_ID}';
DELETE FROM meteoric_meteorite_9699_airflow.dag_run WHERE dag_id = '{DAG_ID}';
```
