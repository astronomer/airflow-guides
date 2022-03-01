---
title: "Airflow's Components"
description: "The core components of Apache Airflow's infrastructure."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-components"
heroImagePath: null
tags: ["Components", "Executors", "Database", "Basics"]
---

## Overview

When working with Airflow, it is important to understand the underlying components: these are the pieces of Airflow infrastructure that power Airflow's orchestration capabilities "under the hood". Even if you mostly interact with Airflow as a DAG author, knowing what the components are and why they are needed can be helpful for getting Airflow running in a local or test environment, debugging, and designing your DAGs appropriately for your Airflow setup.

In this guide, we'll define Airflow's components, discuss the different available executors, and touch on managing Airflow infrastructure and high availability. Note that this guide is focused on the components and features of Airflow 2+. Some of the components and features mentioned here are not available in earlier versions of Airflow.

## Core Components

Apache Airflow has three core components that are running at all times: 

- **Webserver:** A Flask server running with Gunicorn that serves the Airflow UI. It provides an interface to interact with your DAGs, tasks, and database.
- **[Scheduler:](https://airflow.apache.org/docs/apache-airflow/stable/concepts/scheduler.html)** The Daemon responsible for scheduling jobs. This is a multi-threaded Python process that uses the DAG object with the state of tasks in the database to decide what tasks need to be run, when they need to be run, and where they are run.
- **[Database:](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html)** A database where all DAG and task metadata are stored. This is typically a Postgres database, but MySQL, MsSQL, and SQLite are also supported.

If you run Airflow locally using the [Astro CLI](https://docs.astronomer.io/astro/install-cli), you'll notice that when you start Airflow using `astrocloud dev start`, it will spin up three containers, one for each of the components listed above.

Additionally, there are a couple of other components that not considered part of the "core" of Airflow, but are required to run your tasks or make use of certain features:

- **[Executor:](https://airflow.apache.org/docs/apache-airflow/stable/executor/index.html)** The mechanism by which tasks are run. An executor is running at all times Airflow is up (it runs within the Scheduler process). In the section below, we walk through the different executors available and how to choose between them.
- **Worker:** The process that executes tasks, as defined by the executor. Depending on which executor you choose, you may or may not have workers as part of your Airflow infrastructure.
- **[Triggerer:](https://airflow.apache.org/docs/apache-airflow/stable/concepts/deferring.html)** A separate process in addition to the Scheduler running `asyncio` to support deferrable operators. This component is optional and must be run separately. It is only needed if you plan to use deferrable (or "asynchronous") operators. 

All of these components work together to schedule your DAGs and run your tasks:

![title](https://assets2.astronomer.io/main/guides/airflow_component_relationship_fixed.png)

## Executors

Airflow users can choose from multiple available executors or [write their own custom one](https://airflow.apache.org/docs/apache-airflow/stable/executor/index.html). Each executor is good for different situations:

- **[SequentialExecutor:](https://airflow.apache.org/docs/apache-airflow/stable/executor/sequential.html)** Executes tasks sequentially inside the Scheduler process, with no parallelism or concurrency. This executor is rarely used in practice, but it is the default in Airflow's configuration.
- **[LocalExecutor:](https://airflow.apache.org/docs/apache-airflow/stable/executor/local.html)** Executes tasks locally inside the Scheduler process, but supports parallelism and hyperthreading. This executor is a good fit for Airflow running on local machine or a single node, like for local testing.
- **[CeleryExecutor:](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery.html)** Uses a Celery backend (such as Redis, RabbitMq, or another message queue system) to coordinate tasks between preconfigured workers. This executor is ideal if you have a high volume of shorter running tasks, or a more consistent task load.
- **[KubernetesExecutor:](https://airflow.apache.org/docs/apache-airflow/stable/executor/kubernetes.html)** Calls the Kubernetes API to create a separate pod for each task to run, enabling users to pass in custom configurations for each of their tasks and use resources efficiently. This executor is great if you have long running tasks that you don't want to be interrupted by code deploys or Airflow updates, if you have tasks that require very specific resource configurations, or if your tasks run infrequently and you don't want to incur worker resource costs when they aren't running.

Note, there are also a couple of other executors that we don't cover here, including the [CeleryKubernetes Executor](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery_kubernetes.html) and the [Dask Executor](https://airflow.apache.org/docs/apache-airflow/stable/executor/dask.html). These are considered more experimental and are not as widely adopted as the other executors covered here.

## Managing Airflow Infrastructure

All of the components discussed above should be run on supporting infrastructure appropriate for your scale and use case. Running Airflow on a local computer (e.g. using the [Astro CLI](https://docs.astronomer.io/astro/install-cli)) can be great for testing and DAG development, but is likely not sufficient to support DAGs running in production. 

There are many resources out there to help with managing Airflow's components, including:

- OSS [Production Docker Images](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html#using-production-docker-images)
- OSS [Official Helm Chart](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html#using-official-airflow-helm-chart)
- [Astro Cloud](https://www.astronomer.io/product/) managed Airflow

Scalability is also important to consider when setting up your production Airflow. For more on this, check out our [Scaling Out Airflow guide](https://www.astronomer.io/guides/airflow-scaling-workers/).

## High Availability

Airflow can be made highly available, which helps make it suitable for large organizations with critical production workloads. Airflow 2 introduced a highly available Scheduler, meaning you can run multiple Scheduler replicas in an active-active model. This makes the Scheduler more performant and resilient, eliminating a single point of failure within your Airflow environment. 

Note that running multiple Schedulers does come with some extra requirements for the database. For more on how to make use of the HA Scheduler, check out the [Apache Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/concepts/scheduler.html#running-more-than-one-scheduler).
