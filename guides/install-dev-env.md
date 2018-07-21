---
title: "Install Dev Environment for Astronomer"
description: "Install Dev Environment for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-dev-env"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

* Install Google Cloud CLI `gcloud`
* Install Kubernetes CLI `kubectl` (On Mac: `brew install kubernetes-cli`)
* Install Helm CLI `helm` (On Mac: `brew install kubernetes-helm`)
  You may need to run `helm repo update` and/or `helm init --client-only`
* Login with `gcloud auth login`
* Download Astronomer helm charts locally `git clone git@github.com:astronomerio/helm.astronomer.io.git`
* `cd` into that directory

> Note: if you work with multiple Kubernetes clusters, `kubectx` is a nice utility
to switch context between clusters.
