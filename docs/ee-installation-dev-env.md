---
title: "Installing a Dev Environment for Astronomer"
description: "Install Dev Environment for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "ee-installation-dev-env"
---

## GCP

* Install Google Cloud CLI [Google Cloud SDK](https://cloud.google.com/sdk/install)
* Initialize gcloud to use your Google Cloud Project [gcloud init](https://cloud.google.com/sdk/gcloud/reference/init)'
* Ensure you have `gcloud` command line utility installed
* Login with `gcloud auth login`
* Ensure you have `kubectl` command `brew install kubernetes-cli`
* Ensure you have `helm` installed and updated. On mac it's `brew install kubernetes-helm`.
  You may need to run `helm repo update` and/or `helm init --client-only`.
* Get `kubernetes admin` permission on your Google Cloud account
* Download Astronomer helm charts locally `git clone git@github.com:astronomerio/helm.astronomer.io.git`

> Note: if you work with multiple Kubernetes clusters, `kubectx` is a nice utility
to switch context between clusters.


## AWS

* Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/installing.html) and [AWS IAM Authenticator for Kubernetes](https://docs.aws.amazon.com/eks/latest/userguide/configure-kubectl.html)

## General

* [Install Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/install-kubectl/), `kubectl` (On Mac: `brew install kubernetes-cli`)
* [Install Helm CLI](https://docs.helm.sh/using_helm/#installing-helm), `helm` (On Mac: `brew install kubernetes-helm`)
  You may need to run `helm repo update` and/or `helm init --client-only`
  
  * Note: follow these instructions: https://docs.helm.sh/using_helm/#tiller-and-role-based-access-control if you run into this error: `User "system:serviceaccount:kube-system:default" cannot get namespaces in the namespace "<your-namespace>"`
  
* Download Astronomer helm charts locally

	```shell
	git clone git@github.com:astronomerio/helm.astronomer.io.git
	cd helm.astronomer.io
	git checkout <latest tag>
	```

> Note: if you work with multiple Kubernetes clusters, `kubectx` is a nice utility
to switch context between clusters.
