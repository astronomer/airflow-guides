---
title: "Deploying Kedro Pipelines to Apache Airflow"
description: "How to use the kedro-airflow plugin to smoothly change your Kedro pipelines into Apache Airflow DAGs and deploy them to a production environment."
date: 2021-01-28T00:00:00.000Z
slug: "airflow-kedro"
heroImagePath: null
tags: ["Plugins", "Integrations"]
---

## Overview

[Kedro](https://github.com/quantumblacklabs/kedro) is an open-source Python framework for creating reproducible, maintainable, and modular data science code. It borrows concepts from software engineering and applies them to machine learning code.

While Kedro is an excellent option for data engineers and data scientists looking to author their data pipelines and projects with software engineering practices, it can extend even further to integrate with [Apache Airflow](https://airflow.apache.org) for distributed scheduling and execution of the resultant pipelines.

## The Plugin

Our team at Astronomer has teamed up with the Kedro team to extend the [`kedro-airflow`](https://github.com/quantumblacklabs/kedro-airflow) plugin to accommodate a significantly improved developer experience. With this plugin, you can translate your Kedro pipeline into a clean, legible, and well-structured Apache Airflow DAG with one simple command:

```bash
kedro airflow create
```

This makes for a super clean experience for anyone looking to deploy their Kedro pipelines to a distributed scheduler for workflow orchestration.

### Prerequisites

To use the plugin, you'll need the following running on your machine or a fresh virtual environment:

- [The Astronomer CLI](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart#step-1-install-the-astronomer-cli)
- [Kedro](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart#step-1-install-the-astronomer-cli)
- [The `kedro-airflow` Plugin](https://github.com/quantumblacklabs/kedro-airflow)
- [Docker](https://docs.docker.com/docker-for-mac/install/)

## Try it Out

We've added some additional functionality to the plugin that makes for a great experience if you use Astronomer. The steps below walk through creating a fresh Astronomer environment with our CLI tool, generating a Kedro project, packaging it up as an Airflow DAG, and building that DAG into your Docker image to be deployed to an Astronomer Airflow environment.

### Create an Astro project

1. `mkdir <astro-project-directory> && cd <astro-project-directory>`
2. Run `astro dev init` to initialize the project.

### Create a Kedro Project

> Note: Your Kedro project directory should be separate from your Astro project directory

1. Run `kedro new --starter pandas-iris` to create a new Kedro project. The Kedro CLI will walk you through setup.
2. `cd <kedro-project-directory>`
3. `kedro install && kedro package`

### Run the DAG

1. `cd <kedro-project-directory>`
2. `kedro airflow create -t <astro-project-directory>/dags`
3. `cp src/dist/*.whl <astro-project-directory>/`
4. `rsync -avp conf <astro-project-directory>/` note: are we fixing this?
5. `rsync -avp data <astro-project-directory>/`
6. Change your Astronomer project's `Dockerfile` to the following:

    ```docker
    FROM quay.io/astronomer/ap-airflow:2.0.0-buster-onbuild

    RUN pip install --user <kedro-project-python-package>-0.1-py3-none-any.whl
    ```

7. Make sure Docker is running then run `astro dev start` to spin up a local Airflow environment with your shiny new Airflow DAG.

We're proud to partner with the Kedro team on bringing this plugin experience into the world and look forward to extending it to improve the developer experience even more. Please [get in touch](https://astronomer.io/contact) if you'd like to talk to us about how you use Kedro and Airflow together!
