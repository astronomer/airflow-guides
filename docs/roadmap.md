---
title: "Astronomer Roadmap"
date: 2018-11-02T00:00:00.000Z
slug: "roadmap"
menu: ["Resources"]
position: [2]
---

| Release                   | Airflow Core | Airflow Enterprise |
|---------------------------|:------------:|:------------------:|
| Airflow scheduler         | x            | x                  |
| Airflow webserver         | x            | x                  |
| PostgreSQL                | x            | x                  |
| [Redis][redis]            |              | x                  |
| [Celery][celery]          |              | x                  |
| [Flower][flower]          |              | x                  |
| [Prometheus][prometheus]  |              | x                  |
| [Grafana][grafana]        |              | x                  |
| [StatsD exporter][statsd] |              | x                  |
| [cAdvisor][cadvisor]      |              | x                  |

+---------------+---------------+--------------------+
| Fruit         | Price         | Advantages         |
+===============+===============+====================+
| Bananas       | $1.34         | - built-in wrapper |
|               |               | - bright color     |
+---------------+---------------+--------------------+
| Oranges       | $2.10         | - cures scurvy     |
|               |               | - tasty            |
+---------------+---------------+--------------------+

## v0.7

* [Override environment variables on airflow deployments](https://github.com/astronomerio/astronomer-ee/issues/117)
  * As a user, I need to configure my SMTP settings (email alerts), settings for parallelism, and other ENV level settings without exposing credentials in my dockerfile.
* Worker scaling
  * [Control worker count](https://github.com/astronomerio/astronomer-ee/issues/119)
  * [Control worker size](https://github.com/astronomerio/astronomer-ee/issues/120)
* [Control worker termination grace period](https://github.com/astronomerio/astronomer-ee/issues/123)
  * As a deployment.owner I should be able to set the grace period for my workers to restart during a code push.
* Logging
  * Add elasticsearch and fluentd components w/ helm as part of the Astronomer Platform initial deployment

## v0.8 (subject to change)

* Logging
  * Pipe Airflow task logs to Airflow UI
  * Pipe scheduler and web-server logs to Astronomer UI
* [Improve StatsD metrics](https://github.com/astronomerio/incubator-airflow/issues/29)
  * Add counters for success and failed dag_runs, tracking dag_id and execution_date
* [Container Status](https://github.com/astronomerio/astronomer-ee/issues/124)
  * As a deployment.user, I want to see the status of my airflow cluster components in real time: Webserver, Scheduler, Workers.

## v0.9 (subject to change)

* [Support for multiple Airflow versions](https://github.com/astronomerio/astronomer/issues/131)
  * Airflow 1.8, 1.9, 1.10
* Kubernetes Executor
  * Replace Celery, Flower, Redis for Kubernetes Executor
  * Platform owner can set concurrency per Airflow Cluster
  * Cluster owner CRUD custom task pod sizes
  * User can change concurrency and worker size for an Airflow cluster

## Later

* Other OAuth providers, as requested
* Audit Logging. Collect audit logs, present in UI.
* Airflow package manager. Provide command line interface to bring in plugins.
* Improvements to Airflow UI (it should update in real time)
* Platform usage metrics. Trends for daily DAGs, tasks, user engagement in UI.
