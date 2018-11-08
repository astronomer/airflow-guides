---
title: "Installing AWS Stateful Set"
description: "Creating your stateful storage"
date: 2018-07-23T00:00:00.000Z
slug: "ee-installation-aws-stateful-set"
---

Create a new `.yaml` file you can call it `storageclass.yaml` and add the following:

```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: gp2
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
reclaimPolicy: Retain
mountOptions:
  - debug
```

You can now run `kubectl apply -f storageclass.yaml` to apply this to your kubernetes cluster.
