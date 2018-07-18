---
layout: page
title: Platform Dictionary
permalink: /guides/platform-dictionary/
hide: true
---

# Astronomer Platform dictionary

Familiarize yourself with basic platform terminology. Some content may be duplicated across other guides but will contain more detail and context around the terms.

* __Astronomer Platform__ — All of the Astronomer Core and Deployment-Specific components which live on a Kubernetes cluster.
* __Astronomer Core__ — The core applications that make up the Astronomer Platform. There is only one instance of each component with a single Astronomer install.
* __Deployment Components__ — The applications specific to a single Airflow deployment.
* __Platform Install__ — A single installation of the Astronomer Platform. Will include the core components as well as deployment components for each deployment created on your cluster.
* __Astronomer Project__ — An Airflow project directory containing dependency files. In most circumstances it is one to one with a production deployment.
* __Deployment__ — A named Airflow cluster. Mapped to only a single Astronomer project.
* __Workspace__ — Workspaces contain a group of Airflow Cluster Deployments.

## Platform Components

* __astro-cli__ — A command line tool giving the programmatic access to the Astronomer Platform.
* __houston-api__ — A GraphQL API responsible for handling request from the user or user-level platform components (astro-cli, orbit-ui).
* __commander__ — Handles gRPC requests from the houston-api in order to provision, update and delete Airflow deployments on the Astronomer Platform.
* __orbit-ui__ — A webUI built on React. Provides a clean visual experience for users who will be administrating and monitoring the platform.
* __db-bootstrapper__ - Utility to initialize databases and create Kubernetes secrets

## Airflow Components

* __Executor__ — [Executors](https://airflow.incubator.apache.org/code.html?highlight=executor#executors) are the mechanism by which task instances get run.
* __Webserver__ — The user interface for monitoring, administrating and developing Airflow.
* __Scheduler__ — The [Airflow scheduler](https://airflow.incubator.apache.org/scheduler.html?highlight=scheduler#scheduling-triggers) monitors all tasks and all DAGs, and triggers the task instances whose dependencies have been met.
