---
title: "Setting up CloudSQL for GCO"
description: "Setting up CloudSQL for GCP"
date: 2018-07-24T00:00:00.000Z
slug: "install-gcp-cloudsql"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---


## CloudSQL

CloudSQL may be used in place of stable postgres in your Astronomer EE instance. In order to use the CloudSQL database, we'll need to configure the SQLProxy service to ensure the Kubernetes cluster can communicate with the CloudSQL database. 

### Step 1. Enable the CloudSQL service

You can enable the CloudSQL service through the UI, or by using the Gcloud SDK through your terminal. 

Follow the [Google CloudSQL getting started guide](https://cloud.google.com/sql/docs/postgres/quickstart) to enable you postgres database.

### Step 2. Setup the SQLProxy service

To ensure the kubernetes cluster can communicate with your postgres database, we'll use SQLProxy to bring the two.

Head over to the [SQLProxy helm chart](https://github.com/helm/charts/tree/master/stable/gcloud-sqlproxy) and review the requirements.

You'll need to follow steps 1-4 of the Connection to Kubernets engine guide [here](https://cloud.google.com/sql/docs/postgres/connect-kubernetes-engine) as well. The remaining steps are not necessary as these involve configuring individual pods to communicate with the postgres database which is not sufficient for our use. 

After following these steps you should have:

1. A Postgres database hosted in CloudSQL
1. A google service account with role access to the CloudSQL service
1. The service account private key as a JSON file
1. A new `proxyuser` user in your postgres database
1. Your instance connection name

You're now ready to install the SQLProxy helm chart, providing the necessary parameters you retrieved in the previous step. 

### Step 3. Create your bootstrap secret

This part of the installation process will replace the secret creation step when using stable postgres. 

```
$ kubectl create secret generic astronomer-bootstrap --from-literal connection="postgres://proxyuser:${PGPASSWORD}@${CONNECTIONNAME}:5432" --namespace astronomer
```

In the postgres connection string ensure the `proxyuser` created during the SQLProxy setup process is used, including the password created for the `proxyuser`. 

You can now resume the [installation process](/guides/install-gcp/) as normal.