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
* [Improve Grafana dashboard](https://github.com/astronomerio/astronomer/issues/150) (more charts, better data)
* [`KubernetesPodOperator` support](https://github.com/astronomerio/astronomer-ee/issues/116)
* [Override environment variables on airflow deployments](https://github.com/astronomerio/astronomer-ee/issues/117)
* Worker scaling [#119](https://github.com/astronomerio/astronomer-ee/issues/119) [#120](https://github.com/astronomerio/astronomer-ee/issues/120)
* [Improve StatsD metrics](https://github.com/astronomerio/incubator-airflow/issues/29)
* [Service tokens for CI/CD](https://github.com/astronomerio/houston-api/issues/41)
* [Container Status](https://github.com/astronomerio/astronomer-ee/issues/124)
* [Control worker termination grace period](https://github.com/astronomerio/astronomer-ee/issues/123)
* UI
  * webserver/scheduler status
  * [airflow cluster dashboard](https://github.com/astronomerio/astronomer-ee/issues/124)
* Kubernetes Executor
  * Replace Celery, Flower, Redis for Kuberenetes Executor
  * Platform owner can set concurrency per Airflow Cluster
  * Cluster owner CRUD custom task pod sizes
  * User can change concurrency and worker size for an Airflow cluster
* Logging
  * Add elasticsearch and fluentd components w/ helm as part of the Astronomer Platform initial deployment
  * Use fluentd and elasticsearch to pipe Airflow task logs to Airflow UI
  * Use fluentd and elasticsearch to pipe scheduler and web-server logs to Astronomer UI
* Integration with Airflow Kubernetes Operator (under development)
* Other OAuth providers, as requested
* Audit Logging. Collect audit logs, present in UI.
* Airflow package manager. Provide command line interface to bring in plugins.
* Improvements to Airflow UI (it should update in real time)
* Platform usage metrics. Trends for daily DAGs, tasks, user engagement in UI.
