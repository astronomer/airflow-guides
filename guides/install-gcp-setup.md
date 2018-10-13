---
title: "Setting up GCP for Astronomer"
description: "Setting up GCP for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-gcp-setup"
heroImagePath: null
tags: ["admin-docs"]
---

## 1. Create a GCP project

If you don't alreasdy have a GCP project, `gcloud projects create astronomer-project`.
Note the resultant `Project ID`.

## 2. Create a GKE cluster

[Create a GKE cluster](https://console.cloud.google.com/kubernetes/add)
  if you don't already have one.

Note the name of it.

## 3. Create a static IP

Choose a name for your static IP, in this example we choose `astronomer-ip`.

```shell
$ gcloud compute addresses create astronomer-ip \
  --region us-east4 \
  --project astronomer-project-190903

$ gcloud compute addresses describe astronomer-ip \
  --region us-east4 \
  --project astronomer-project-190903 \
  --format 'value(address)'
```

Note the IP.

## 4. Create a Kubernetes namespace

* Create a namespace `kubectl create ns my-demo`
* View your pods `kubectl get all -n my-demo` and `kubectl get pods -n my-demo`

Note: you can proxy to the dashboard `kubectl proxy &` and you'll have to get your
token: `kubectl config view --minify | grep access-token | awk '{print $2}'`.
Then open [the dashboard](http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login).
