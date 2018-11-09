---
title: "Enterprise Edition Overview"
date: 2018-10-12T00:00:00.000Z
slug: "ee-overview"
menu: ["Enterprise Edition"]
position: [1]
---

![Astronomer Overview](https://cdn-images-1.medium.com/max/2000/1*NOdESVh32nq5mbs_Nj46pA.png)

## Airflow Clusters

When you create a new Airflow deployment on Astronomer, the
platform will deploy Kubernetes pods for an Airflow Webserver,
Airflow Scheduler, pool of Celery workers, a small Redis instance
(that backs Celery), and a statsd pod that streams metrics to a
centralized Prometheus and Grafana.

## Easy Installation

You can self-install Asstronomer onto Kubernetes by following our
[install guides](https://www.astronomer.io/docs/ee-getting-started/).

When you install the Astronomer platform, a number of components
are deployed including NGINX, Prometheus, Grafana, a GraphQL API
(Houston), a React UI (Orbit), and a private Docker Registry (used
in the DAG deployment process).

Helm charts here: https://github.com/astronomerio/helm.astronomer.io

## Easy DAG Deployment

Astronomer makes it easy to deploy these containers
to Kubernetes - but more importantly, to give Airflow developers a
CLI to deploy DAGs through a private Docker registry that interacts
with the Kubernetes API.

Remember to run `astro airflow init` after creating a new project directory.

Any Python packages can be added to `requirements.txt` and all OS level packages
can be added to `packages.txt` in the project directory.

Additional [RUN](https://docs.docker.com/engine/reference/builder/#run)
commands can be added to the `Dockerfile`. Environment variables can also be
added to [ENV](https://docs.docker.com/engine/reference/builder/#env).

## Authentication Options

* Local (username/password)
* Auth0 (supports SAML, Active Directory, other SSO)
* Google
* Github

## Astro CLI

The [Astro CLI](https://github.com/astronomerio/astro-cli)
helps you develop and deploy Airflow projects.

## Houston

[Houston](https://github.com/astronomerio/houston-api) is a GraphQL
API that serves as the source of truth for the Astronomer Platform.

## Commander

[Commander](https://github.com/astronomerio/commander) is a  GRPC
provisioning component of the Astronomer Platform. It is
responsible for interacting with the underlying Kubernetes
infrastructure layer.

## Orbit

[Orbit](https://github.com/astronomerio/orbit-ui) is a GraphQL UI
that provides easy access to the capabilities of the Astronomer
platform.

## dbBootstrapper

[dbBootstrapper](https://github.com/astronomerio/db-bootstrapper)
is a utility that initializes databases and create Kubernetes
secrets, and runs automatically when an Airflow cluster is created.
