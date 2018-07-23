---
title: "Install Dev Environment for Astronomer"
description: "Install Dev Environment for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-dev-env"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---
## GCP
* Install Google Cloud CLI [Google Cloud SDK](https://cloud.google.com/sdk/install)
* Initialize gcloud to use your Google Cloud Project [gclouf init](https://cloud.google.com/sdk/gcloud/reference/init)

## AWS
* Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/installing.html) and [Heptio Authenticator](https://docs.aws.amazon.com/eks/latest/userguide/configure-kubectl.html)


## General

* [Install Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/install-kubectl/), `kubectl` (On Mac: `brew install kubernetes-cli`)
* [Install Helm CLI](https://docs.helm.sh/using_helm/#installing-helm), `helm` (On Mac: `brew install kubernetes-helm`)
  You may need to run `helm repo update` and/or `helm init --client-only`
* Download Astronomer helm charts locally `git clone git@github.com:astronomerio/helm.astronomer.io.git`
* `cd` into that directory

> Note: if you work with multiple Kubernetes clusters, `kubectx` is a nice utility
to switch context between clusters.
