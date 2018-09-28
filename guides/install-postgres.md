---
title: "Install Postgres for Astronomer"
description: "Install Postgres for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-postgres"
heroImagePath: "https://assets.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

## Create a Kubernetes secret with your PostgreSQL connection

If you do not already have a PostgreSQL cluster, we recommend using a service
like Compose, Amazon RDS, or Google Cloud SQL.

The PostgreSQL user needs permissions to create users, schemas, databases, and tables.

For testing purposes, you can quickly get started using the PostgreSQL helm chart.

Run:

```shell
helm install --name astro-db stable/postgresql --namespace astronomer
```
