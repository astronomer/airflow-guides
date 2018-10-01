---
title: "Setting Kubernetes Secrets for Astronomer"
description: "Setting Kubernetes Secrets for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-k8s-secrets"
heroImagePath: "https://assets.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

## 1. Postgres Secret

Depending on where your Postgres cluster is running, you may need to adjust the connection string in the next step to match your environment. If you installed via the helm chart, you can run the command that was output by helm to set the `${PGPASSWORD}` environment variable, which can be used in the next step. Once that variable is set, you can run this command directly to create the bootstrap secret.

```
helm list
```

find your postgres pod, and note the name...

```
PGPASSWORD=$(kubectl get secret --namespace astronomer pod-name-postgresql -o jsonpath="{.data.postgres-password}" | base64 --decode; echo)

echo $PGPASSWORD
```

To set the secret, run:

```shell
$ kubectl create secret generic astronomer-bootstrap /
  --from-literal connection="postgres://postgres:${PGPASSWORD}@astro-db-postgresql.astronomer.svc.cluster.local:5432" /
  --namespace astronomer
```

> Note: Change user from `postgres` if you're creating a user instead of using the default, it needs permission to create databases, schemas, and users.

## 2. TLS Secret

```shell
$ kubectl create secret tls astronomer-tls /
  --key /etc/letsencrypt/live/astro.mycompany.com/privkey.pem /
  --cert /etc/letsencrypt/live/astro.mycompany.com/fullchain.pem /
  --namespace astronomer
```
