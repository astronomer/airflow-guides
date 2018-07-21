---
title: "Install Dev Environment for Astronomer"
description: "Install Dev Environment for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-dev-env"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

* Ensure you have `gcloud` command line utility installed
* Login with `gcloud auth login`
* Ensure you have `kubectl` command `brew install kubernetes-cli`
* Ensure you have `helm` installed and updated. On mac it's `brew install kubernetes-helm`.
  You may need to run `helm repo update` and/or `helm init --client-only`.
* Get `kubernetes admin` permission on your Google Cloud account
* Download Astronomer helm charts locally `git clone git@github.com:astronomerio/helm.astronomer.io.git`

> Note: Kubectl cheatsheet https://kubernetes.io/docs/reference/kubectl/cheatsheet/
  Useful aliases https://gist.github.com/tamas-molnar/32a07c0eb83e95484e3cdb4b7fada32b

Note: if you work with multiple Kubernetes clusters, `kubectx` is a nice utility
to switch context between clusters.
