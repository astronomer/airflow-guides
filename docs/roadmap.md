---
title: "Astronomer Roadmap"
date: 2018-11-02T00:00:00.000Z
slug: "roadmap"
menu: ["Resources"]
position: [2]
---

| Release | Features |
|---------------------------|------------|
| v0.7 | [Override environment variables on airflow deployments](https://github.com/astronomerio/astronomer-ee/issues/117) As a user, I need to configure my SMTP settings (email alerts), settings for parallelism, and other ENV level settings without exposing credentials in my dockerfile.<br />Worker scaling: [Control worker count](https://github.com/astronomerio/astronomer-ee/issues/119), [Control worker size](https://github.com/astronomerio/astronomer-ee/issues/120)<br />[Control worker termination grace period](https://github.com/astronomerio/astronomer-ee/issues/123) As a deployment.owner I should be able to set the grace period for my workers to restart during a code push.<br />Logging: Add elasticsearch and fluentd components w/ helm as part of the Astronomer Platform initial deployment |
| v0.8 | Logging: pipe Airflow task logs from Elasticsearch to Airflow UI, and scheduler and web-server logs from Elasticsearch to Astronomer UI<br />[Improve StatsD metrics](https://github.com/astronomerio/incubator-airflow/issues/29) Add counters for success and failed dag_runs, tracking dag_id and execution_date<br />[Container Status](https://github.com/astronomerio/astronomer-ee/issues/124) As a deployment.user, I want to see the status of my airflow cluster components in real time: Webserver, Scheduler, Workers. |
| v0.9 | [Support for multiple Airflow versions](https://github.com/astronomerio/astronomer/issues/131): Airflow 1.8, 1.9, 1.10<br />Kubernetes Executor: support for Kubernetes Executor, platform owner can set concurrency per Airflow Cluster, Cluster owner CRUD custom task pod sizes, user can change concurrency and worker size for an Airflow cluster |
|  Later | Other OAuth providers, as requested<br />Audit Logging. Collect audit logs, present in UI.<br />Airflow package manager. Provide command line interface to bring in plugins.<br />Improvements to Airflow UI (it should update in real time)<br />Platform usage metrics. Trends for daily DAGs, tasks, user engagement in UI. |
