---
layout: page
title: Roadmap
permalink: /roadmap.html
order: 3
---

## Release 0.3 (~July 2018)

* CLI
  * Delete Airflow clusters
  * Replace our current simple user system with OAuth
    * Start by supporting Google auth only first
    * `astro auth login` will present a link to oauth login form
    * First user who logs in becomes the owner of the deployed astronomer platform
    * Eliminate “basic auth” hack and allow users to log into a UI that authenticates with Houston (our GraphQL API).

* Teams API
  * Users can create a team
  * Team members can invite others to their team
  * Team admins can create an Airflow cluster for their team
  * I can set one role for each user for the Astronomer Platform — Platform Owner (first person), Platform Admin (e.g., K8s cluster, Grafana access), User
  * I can set roles for an Airflow cluster — Owner (first person), Admin, Deploy

* Astronomer UI
  * Login/logout w/ Google Oauth (using bitly oauth service)
  * CRUD Airflow Clusters
  * CRUD Teams
  * CRUD User Groups
  * CRUD Invitations
  * CRUD Roles

* Monitoring (Telemetry)
  * Monitoring API endpoint to receive data, which allows us to proactively monitor (EE) customer Airflow instances
  * Kube job that queries Prometheus and pushes Airflow task success/failure count metrics to the Astronomer Monitoring API, with config option to the charts for this feature, as some customers Kubernetes environment may block direct communication w/ internet

## Release 0.4

* RBAC
  * Investigate mapping our permissions to Airflow’s new RBAC UI

* Service Accounts
  * Generate token for CI/CD pipeline
  * Integrate w/ UI

## Release 0.5

* Logging
  * Add elasticsearch and fluentd components w/ helm as part of the Astronomer Platform initial deployment
  * Use fluentd and elasticsearch to pipe Airflow task logs to Airflow UI
  * Use fluentd and elasticsearch to pipe scheduler and web-server logs to Astronomer UI

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

* Astronomer Operator
  * Could make upgrade process of Astronomer Platform even easier

## Future

* Other Oauth providers, as requested
* Audit Logging. Collect audit logs, present in UI.
* Platform usage metrics. Present trends for daily DAGs, tasks, user engagement in UI.
* Airflow package manager. Provide command line interface to bring in plugins.
* Astronomer Kubernetes Operator
* Improvements to Airflow UI (it should update in real time)
