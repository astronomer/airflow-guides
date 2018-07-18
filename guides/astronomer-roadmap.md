---
title: "Astronomer Roadmap"
description: "Product Roadmap for the Astronomer Platform"
date: 2018-05-21T00:00:00.000Z
slug: "astronomer-roadmap"
heroImagePath: null
tags: ["user-docs", "admin-docs"]
---

## Release 0.4

* Logging
  * Add elasticsearch and fluentd components w/ helm as part of the Astronomer Platform initial deployment
  * Use fluentd and elasticsearch to pipe Airflow task logs to Airflow UI
  * Use fluentd and elasticsearch to pipe scheduler and web-server logs to Astronomer UI

* Worker scaling via UI
* Service tokens for CI/CD
* Platform usage metrics. Present trends for daily DAGs, tasks, user engagement in UI.

## Release 0.5

* Kubernetes Executor
  * Replace Celery, Flower, Redis for Kuberenetes Executor
  * Platform owner can set concurrency per Airflow Cluster
  * Cluster owner CRUD custom task pod sizes
  * User can change concurrency and worker size for an Airflow cluster

* UI
  * webserver/scheduler status
  * airflow cluster dashboard (routing prometheus queries through houston)
  * team dashboard (routing prometheus queries through houston)
  * account dashboard (routing prometheus queries through houston)
  * Improve astronomer platform grafana dashboard
  * all functionality of CLI

## Release 0.6

* Integration with Airflow Kubernetes Operator (under development)

## Future

* Other OAuth providers, as requested
* Audit Logging. Collect audit logs, present in UI.
* Airflow package manager. Provide command line interface to bring in plugins.
* Improvements to Airflow UI (it should update in real time)
