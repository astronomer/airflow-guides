---
title: "GCP GKE"
description: "Installing Astronomer on GCP GKE."
date: 2018-10-12T00:00:00.000Z
slug: "ee-installation-gke"
menu: ["Installation"]
position: [3]
---

This guide describes the process to install Astronomer on Google Cloud Platform (GCP).

## Are you admin-y enough to do this alone?

You will need to be able to:

* Obtain a wildcard SSL certificate
* Edit your DNS records
* Create resources on Google Cloud Platform
  (GKE admin permission)
* Install/run Kubernetes command line tools to your machine

## Pre-requisites

Before running the Astronomer install command you must:

1. [Select a base domain](/guides/ee-installation-base-domain)
2. [Get your machine setup with needed dev tools](/docs/ee-installation-dev-env)
3. [Setup GCP](/docs/ee-installation-gcp-setup)
4. [Get a Postgres server running](/docs/ee-installation-postgres)
5. [Obtain SSL](/docs/ee-installation-ssl)
6. [Setup DNS](/docs/ee-installation-dns)
7. [Install Helm and Tiller](/docs/ee-installation-helm)
8. [Set a few Kubernetes secrets](/docs/installation-k8s-secrets)
9. [Create Google OAuth Creds ](/docs/ee-installation-google-oauth)
10.[Build your config.yaml](/docs/ee-installation-config)

## Install Astronomer

You're ready to go!

```shell
$ helm install -f config.yaml . --namespace astronomer
```

Click the link in the output notes to log in to the Astronomer app.

Feel free to check out our video walkthrough of the Install below:

[![Install](https://img.youtube.com/vi/IoeesuFNG9Q/0.jpg)](https://www.youtube.com/watch?v=IoeesuFNG9Q "Install Video")
