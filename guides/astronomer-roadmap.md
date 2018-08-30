---
title: "Astronomer Roadmap"
description: "Product Roadmap for the Astronomer Platform"
date: 2018-05-21T00:00:00.000Z
slug: "astronomer-roadmap"
heroImagePath: null
tags: ["user-docs", "admin-docs"]
---

Upcoming features:

* [Support for multiple Airflow versions](https://github.com/astronomerio/astronomer/issues/131)
  * Airflow 1.8, 1.9, 1.10
* [Improve Grafana dashboard](https://github.com/astronomerio/astronomer/issues/150)
  * Improve the Grafana dashboard for monitoring a system with multiple airflows deployed
* [KubernetesPodOperator support](https://github.com/astronomerio/astronomer-ee/issues/116)
  * Better alternative to DockerOperator for Kubernetes environment
* [Override environment variables on airflow deployments](https://github.com/astronomerio/astronomer-ee/issues/117)
  * As a user, I need to configure my SMTP settings (email alerts), settings for parallelism, and other ENV level settings without exposing credentials in my dockerfile.
* Worker scaling
  * [Control worker count](https://github.com/astronomerio/astronomer-ee/issues/119)
  * [Control worker size](https://github.com/astronomerio/astronomer-ee/issues/120)
* [Improve StatsD metrics](https://github.com/astronomerio/incubator-airflow/issues/29)
  * Add counters for success and failed dag_runs, tracking dag_id and execution_date
* [Service tokens for CI/CD](https://github.com/astronomerio/houston-api/issues/41)
  * As a workspace.owner, I can add a “service token” to a deployment, and assign it a role, so that I can set up any CD/CI setup I choose.
* [Container Status](https://github.com/astronomerio/astronomer-ee/issues/124)
  * As a deployment.user, I want to see the status of my airflow cluster components in real time: Webserver, Scheduler, Workers.  
* [Control worker termination grace period](https://github.com/astronomerio/astronomer-ee/issues/123)
  * As a deployment.owner I should be able to set the grace period for my workers to restart during a code push.
* Kubernetes Executor
  * Replace Celery, Flower, Redis for Kuberenetes Executor
  * Platform owner can set concurrency per Airflow Cluster
  * Cluster owner CRUD custom task pod sizes
  * User can change concurrency and worker size for an Airflow cluster
* Logging
  * Add elasticsearch and fluentd components w/ helm as part of the Astronomer Platform initial deployment
  * Use fluentd and elasticsearch to pipe Airflow task logs to Airflow UI
  * Use fluentd and elasticsearch to pipe scheduler and web-server logs to Astronomer UI
* Other
  * Integration with Airflow Kubernetes Operator (under development)
  * Other OAuth providers, as requested
  * Audit Logging. Collect audit logs, present in UI.
  * Airflow package manager. Provide command line interface to bring in plugins.
  * Improvements to Airflow UI (it should update in real time)
  * Platform usage metrics. Trends for daily DAGs, tasks, user engagement in UI.
