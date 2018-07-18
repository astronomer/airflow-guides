---
layout: page
title: Features
permalink: /features.html
order: 1
---

## Architecture

We’ve build out pre-configured Docker containers w/ Celery and metrics/monitoring.
The Astronomer Airflow module consists of seven components, and you must bring
your own Postgres and Redis database.

![Airflow Module]({{ "/assets/img/airflow_module.png" | absolute_url }})

This kit is fully open-sourced (Apache 2.0) and you can experiment with it at
[https://open.astronomer.io/](https://open.astronomer.io/).

## Astronomer CLI

The [Astronomer CLI](https://github.com/astronomerio/astro-cli) is
under very active development to
[support Airflow-related commands](https://github.com/astronomerio/astro-cli/blob/master/cmd/airflow.go).

## Airflow CLI

We also make it easy to use the Airflow CLI remotely
(i.e. run commands from your local terminal that execute in the
cloud Airflow).

## DAG Deployment

Astronomer Enterprise makes it easy to deploy these containers
to Kubernetes - but more importantly, to give Airflow developers a
CLI to deploy DAGs through a private Docker registry that interacts
with the Kubernetes API.

[Commander](https://github.com/astronomerio/commander) glues this all together.

![Airflow Deployment]({{ "/assets/img/airflow_deployment.png" | absolute_url }})

Remember to run `astro airflow init` after creating a new project directory.

Any Python packages can be added to `requirements.txt` and all OS level packages can be added to `packages.txt` in the project directory.

Additional [RUN](https://docs.docker.com/engine/reference/builder/#run
) commands can be added to the `Dockerfile`. Environment variables can also be added to [ENV](https://docs.docker.com/engine/reference/builder/#env).
