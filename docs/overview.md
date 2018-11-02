---
title: "Overview of Astronomer"
date: 2018-10-12T00:00:00.000Z
slug: "overview"
menu: ["root"]
position: [1]
---

## Astronomer: Cloud Edition

Astronomer Cloud is a managed instance of Apache Airflow on an Astronomer-hosted cluster for ultimate abstraction from all-things infrastructure. It includes:

- A custom CLI for easy DAG deployment and management

- Access to our Astronomer UI with secure authentication for easy deployment, user, and workspace management. You can read more about the components of our UI below.

- Resource Controls from the UI

- Multiple [support options](https://astronomer.io/pricing) pending your team's needs


## Astronomer: Enterprise Edition

Astronomer Enterprise allows you to run a private version of our platform on your own Kubernetes cluster It includes:

- Astronomer Command Center that includes an Astronomer-built UI, CLI, and a GraphQL API for easy cluster and deployment management on Kubernetes

- Access to a Prometheus and Grafana monitoring stack for metrics on your Airflow activity

- Enterprise Authentication that supports Google Suite, SAML, Office 365, Active Directory, and more

- Enterprise-grade business day or business critical support

# The Astronomer UI

To help achieve Astronomer's goal of improving Airflow's usability, we have built a custom UI that makes user access and deployment management dead simple. In this guide, we'll walk through the specific components of the Astronomer UI and discuss the design principles that led to their creation.

## Getting Started

Before we dive in, here are some quick definitions for terms that we'll use when discussing the Astronomer UI:

 - *Workspace*: A set of Airflow deployments that specific users have access to.
 - *Deployment*: An instance of Airflow with dedicated and isolated resources.

[Once you've created an account and authenticated in](https://astronomer.io/guides/getting-started-with-new-cloud/), you'll land on a dashboard that gives you an  overview of your Workspaces. We'll call this the `Account Dashboard`:

![Account Dashboard](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/account_dashboard.png)

You can think of your Workspaces the same way you'd think of teams- they're just collections of Airflow clusters that specific user groups have access to. From this dashboard, you can spin up new Workspaces and get a high-level overview of active Airflow deployments in your current workspaces.

Once you click into a workspace, you'll land on another dashboard that we'll call the `Workspace Dashboard`:

![Workspace Dashboard](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/workspace_dashboard.png)

Here, you have a high-level overview of all of the active Airflow deployments you have running in that given workspace. In this case, we only have one cluster spun up. From this screen, you can create new Airflow deployments, manage user access to the workspace, and generate tokens for CI/CD systems via service accounts. Note that, since all of our app activity is routed through a GraphQL API, you can also create deployments, switch workspaces, and add users via our [CLI](https://www.astronomer.io/guides/astro-cli/) if you prefer staying in your terminal.

## Deployments

If you click into one of your Airflow deployments, you'll land on a page that looks like this:

![Depoloyments](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/deployment_dashboard.png)

From here, you'll be able to access the Airflow and Flower dashboards for that specific deployment. In Astronomer's 0.7 release, you will be able to scale up Celery workers directly from the UI here as well.

## User Management

If you navigate over to the `Users` tab of your Workspace Dashboard, you'll be able to see who has access to the Workspace and invite other members of your organization to access the Airflow instances in that Workspace.

![Users](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/user_dashboard.png)

Note that, in an upcoming release, you'll be able to designate DAG-level permissions for each of the users who has access to the Workspace.

## Service Accounts

If you're interested in integrating your deployment process into your CI/CD system, [check out this guide](https://astronomer.io/guides/deploying-dags-with-cicd/). Through the `Services Account` tab in your Workspace Dashboard, you can generate API keys that you can plug into your CI/CD secrets manager.

Note that you're able to create Service Accounts at both the Workspace and Deployment level. Creating them at the Workspace level allows you to customize how your deployment pipeline works and allows you to deploy to multiple Airflow instances with one push, while creating them at the Deployment level ensures that your CI/CD pipeline will only deploy to that specific cluster. Check out [this video](https://www.youtube.com/watch?time_continue=2&v=8h9lXzGa4sQ) for a more detailed walkthrough of Service Accounts and CI/CD with Astronomer.


# Astronomer Features
## Airflow Clusters

When you create a new Airflow deployment on Astronomer, the
platform will deploy Kubernetes pods for an Airflow Webserver,
Airflow Scheduler, pool of Celery workers, a small Redis instance
(that backs Celery), and a statsd pod that streams metrics to a
centralized Prometheus and Grafana.

## Easy Installation

You can self-install Asstronomer onto Kubernetes by following our
[install guides](https://www.astronomer.io/guides/install/).

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
