---
title: "Getting Started"
description: "Getting started with Astronomer Enterprise."
date: 2018-10-12T00:00:00.000Z
slug: "ee-getting-started"
menu: ["Enterprise Edition"]
position: [3]
---

Astronomer Enterprise Edition allows you to run a private version of Astronomer
on your own Kubernetes.

It includes:

* Astronomer Command Center that includes an Astronomer-built UI, CLI, and a
  GraphQL API for easy cluster and deployment management on Kubernetes
* Access to our Prometheus and Grafana monitoring stack
* Enterprise Authentication that supports Google Suite, SAML, Office 365, Active Directory, and more
* Enterprise-grade business day or business critical support

Read [here](/docs/ee-overview) for more details on
each of these components.

## Installing

We've written installation docs for various Kubernetes distributions:

* [Astronomer on Kubernetes](/docs/ee-installation-general-kubernetes)
* [Amazon Web Services - EKS](/docs/ee-installation-eks)
* [Google Cloud Platform - GKE](/docs/installation-ee-gke)

Coming Soon: Guides for Azure AKS, Pivotal PKE, Redhat OpenShift, and
Digital Ocean Kubernetes.

## Prerequisites

The Astronomer platform is Kubernetes agnostic. This means that any Kubernetes
management solution should support the installation, and management of the
Astronomer platform. To ensure the platform can be effectively installed and
managed, ensure your team can meet the following requirements.

* A Kubernetes cluster managed by one of these solutions:
  https://kubernetes.io/docs/setup/pick-right-solution/
* Admin level access to the Kubernetes cluster
* Ability to provision a Tiller service account for use with Helm
* A base domain
* A CA signed wildcard for your base domain. This cannot be a self-signed certificate
* A postgres database
* A wildcard DNS A record

Need help installing the Astronomer platform?
[Reach out](https://www.astronomer.io/contact/?from=/) to discuss install solutions.
