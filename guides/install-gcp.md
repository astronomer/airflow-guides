---
title: "Install Astronomer to Google Cloud Platform"
description: "Install Astronomer to Google Cloud Platform"
date: 2018-07-17T00:00:00.000Z
slug: "install-gcp"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

This guide describes the process to install Astronomer on Google Cloud Platform
(GCP).

## Are you admin-y enough to do this alone?

You will need to be able to:

* Obtain a wildcard SSL certificate
* Edit your DNS records
* Create resources on Google Cloud Platform
* Install/run Kubernetes command line tools to your machine

## Pre-requisites

Before running the Astronomer install command you must:

1. [Select a base domain](/guides/install-base-domain)
1. [Get your machine setup with needed dev tools](/guides/dev-env)
1. [Setup GCP](/guides/gcp-setup)
1. [Get a Postgres server running](/guides/install-postgres)
1. [Obtain SSL](/guides/install-ssl)
1. [Setup DNS](/guides/install-dns)
1. [Set a few Kubernetes secrets](/guides/install-k8s-secrets)
1. [Create Google OAuth Creds ](/guides/install-google-oauth)
1. [Build your config.yaml](/guides/install-config)

## Install Astronomer

```shell
$ helm install -f config.yaml . --namespace astronomer
```

Click the link in the output notes to log in to the Astronomer app.
