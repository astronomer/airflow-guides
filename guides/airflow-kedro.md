---
title: "Deploying Kedro Pipelines to Apache Airflow"
description: "How to use the kedro-airflow plugin to change your Kedro pipelines into Apache Airflow DAGs and deploy them to a production environment."
date: 2021-03-09T00:00:00.000Z
slug: "airflow-kedro"
heroImagePath: null
tags: ["Plugins", "Integrations"]
---

## Overview

[Kedro](https://github.com/quantumblacklabs/kedro) is an open-source Python framework for creating reproducible, maintainable, and modular data science code. It borrows concepts from software engineering and applies them to machine learning code.

While Kedro is an excellent option for data engineers and data scientists looking to author their data pipelines and projects with software engineering practices, it can extend even further to integrate with [Apache Airflow](https://airflow.apache.org) for distributed scheduling and execution of the resultant pipelines.

## The Plugin

In close partnership with the team at Kedro, we've recently extended the [`kedro-airflow`](https://github.com/quantumblacklabs/kedro-airflow) plugin to accommodate a significantly improved developer experience. With this plugin, you can translate your Kedro pipeline into a clean, legible, and well-structured Apache Airflow DAG with one simple command:

```bash
kedro airflow create
```

This makes for a super clean experience for anyone looking to deploy their Kedro pipelines to a distributed scheduler for workflow orchestration.

### Prerequisites

To use the plugin, you'll need the following running on your machine or a fresh virtual environment:

- [The Astronomer CLI](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart#step-1-install-the-astronomer-cli)
- [Kedro](https://github.com/quantumblacklabs/kedro)
- [The `kedro-airflow` Plugin](https://github.com/quantumblacklabs/kedro-airflow)
- [Docker](https://docs.docker.com/docker-for-mac/install/)

## Try it Out

We've added some additional functionality to the plugin that makes for a great integration with Astronomer. To give it a try, we'll use the `astro-iris` starter that's included in the Kedro project; The steps below walk through spinning up a fresh Kedro project and running your pipelines as DAGs on a local Airflow environment.

### Create an Astro-Kedro project

1. `kedro new --starter astro-iris` to build your starter directory.
2. `cd <kedro-project-directory>`
3. `kedro install`
4. `kedro package`
   
### Prepare and run the project in Astro

1. `cp src/dist/*.whl ./`
2. `kedro catalog create --pipeline=__default__`
3. Edit your `conf/base/catalog/__default__.yml` and configure datasets to be persisted, e.g.

    ```yaml
    example_train_x:
        type: pickle.PickleDataSet
        filepath: data/05_model_input/example_train_x.pkl
    example_train_y:
        type: pickle.PickleDataSet
        filepath: data/05_model_input/example_train_y.pkl
    example_test_x:
        type: pickle.PickleDataSet
        filepath: data/05_model_input/example_test_x.pkl
    example_test_y:
        type: pickle.PickleDataSet
        filepath: data/05_model_input/example_test_y.pkl
    example_model:
        type: pickle.PickleDataSet
        filepath: data/06_models/example_model.pkl
    example_predictions:
        type: pickle.PickleDataSet
        filepath: data/07_model_output/example_predictions.pkl`
    ```

4. Make sure you have the `kedro-airflow` plugin installed, then run `pip install kedro-airflow`
5. `kedro airflow create -t dags/`
6. Make sure you have the Astro CLI installed and have Docker running on your machine, then run `astro dev start` to fire up a local Airflow instance and visualize your DAGs.

We're proud to partner with the Kedro team on bringing this plugin experience into the world and look forward to extending it to improve the developer experience even more. Please [get in touch](https://astronomer.io/contact) if you'd like to talk to us about how you use Kedro and Airflow together!
