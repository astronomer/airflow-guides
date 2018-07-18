---
title: "Astronomer Features"
description: "What are the components of the Astronomer platform"
date: 2018-05-21T00:00:00.000Z
slug: "astronomer-features"
heroImagePath: null
tags: ["astronomer"]
---

## Astronomer Installation

When you install the Astronomer platform, a number of components are deployed
including NGINX, Prometheus, Grafana, our GraphQL API (Houston), our React UI
(Orbit), and a Docker Registry (used by deployment process).

## Airflow Clusters

When you create a new Airflow deployment in Astronomer interface, Commander
will deploy pods for Airflow Webserver, Airflow Scheduler, pool of Celery
workers, a small Redis instance (that backs Celery), and a statsd pod that
streams metrics to Prometheus and Grafana. A script is automatically run
(db-bootstrapper) to setup Postgres databases and users to support the cluster.

## Astronomer CLI

The [Astronomer CLI](https://github.com/astronomerio/astro-cli) is
under very active development and you can do everything in our CLI
that you can do in our UI.

## DAG Deployment

Astronomer makes it easy to deploy these containers
to Kubernetes - but more importantly, to give Airflow developers a
CLI to deploy DAGs through a private Docker registry that interacts
with the Kubernetes API.

Remember to run `astro airflow init` after creating a new project directory.

Any Python packages can be added to `requirements.txt` and all OS level packages
can be added to `packages.txt` in the project directory.

Additional [RUN](https://docs.docker.com/engine/reference/builder/#run
) commands can be added to the `Dockerfile`. Environment variables can also be
added to [ENV](https://docs.docker.com/engine/reference/builder/#env).
