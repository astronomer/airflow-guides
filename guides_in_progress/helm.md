---
layout: page
title: Helm
permalink: /guides/helm/
hide: true
---



# Helm

To install the Astronomer Platform, you will need to also have `helm` and it's deployment service `tiller` installed. If you are already using `helm`, you can skip this step.
To install Helm and Tiller, see the [Kubernetes Helm Install Guide](https://github.com/kubernetes/helm/blob/master/docs/install.md)

## Intialize Helm

### Preparing for Helm with RBAC

If your cluster has RBAC enabled (usually by default in modern clusters), you'll need to take a few extra steps to give `tiller` the ability to talk to the Kubernetes API.

First, create a `ServiceAccount` and `ClusterRole` for `tiller` to use. Save the following to a file called `rbac-config.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: tiller
    namespace: kube-system
```

Then, run `kubectl create -f rbac-config.yaml` to create the resources in your cluster. After that, run `helm init --service-account tiller` to install `tiller` with the new service account. `tiller` should now have permissions to deploy charts.
