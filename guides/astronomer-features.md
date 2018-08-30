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

Helm charts here: https://github.com/astronomerio/helm.astronomer.io

## Commander GRPC

Commander is the provisioning component of the Astronomer Platform. It is
responsible for interacting with the underlying Kubernetes infrastructure layer.

Link: https://github.com/astronomerio/commander

## Houston API

Houston API is the source of truth for the Astronomer Platform.

Link: https://github.com/astronomerio/houston-api

## Orbit UI

Open-source UI for Astronomer's managed Apache Airflow platform. For Enterprise Edition - a production-ready Airflow stack deployable to any Kubernetes cluster. For Cloud Edition - a fully managed service hosted on our infrastructure.

Link: https://github.com/astronomerio/orbit-ui

## dbBootstrapper

Utility to initialize databases and create Kubernetes secrets for Astronomer EE.

Link: https://github.com/astronomerio/db-bootstrapper

## CLI

The Astronomer CLI is the recommended way to get started developing and deploying on Astronomer Enterprise Edition.

Link: https://github.com/astronomerio/astro-cli

## Authentication

* Local (username/password)
* Auth0
* Google
* Github

## Airflow Clusters

When you create a new Airflow deployment in Astronomer interface, Commander
will deploy pods for Airflow Webserver, Airflow Scheduler, pool of Celery
workers, a small Redis instance (that backs Celery), and a statsd pod that
streams metrics to Prometheus and Grafana. A script is automatically run
(db-bootstrapper) to setup Postgres databases and users to support the cluster.


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
