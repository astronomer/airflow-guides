---
title: "Using the Airflow CLI in Astronomer Enterprise"
description: "Access Airflow CLI commands via the kubectl CLI"
date: 2018-10-09T12:00:00.000Z
slug: "enterprise-using-airflow-cli"
heroImagePath: null
tags: ["Airflow", "admin-docs", "Astronomer Platform"]
---

# Using the Airflow CLI within Astronomer Enterprise

Although Airflow's UI supports the majority of the behavior you would need when setting up your environment and building DAGs, there are cases when you want to use the Airflow CLI.

## Configuring kubectl
Before interacting directly with the Kubernetes pods that are created for each Airflow deployment on the Astronomer platform, it is necessary to first configure the Kubernetes command line `kubetcl`. Instructions on how to install `kubectl` can be found: [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/). Connecting to your Kubernetes cluster will be different depending on where it is installed.
- [Configuring GKE (Google) Access for kubectl](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl)
- [Configuring EKS (Amazon) Access for kubectl](https://docs.aws.amazon.com/eks/latest/userguide/configure-kubectl.html)
- [Configuring AKS (Microsoft) Access for kubectl](https://docs.microsoft.com/en-us/azure/aks/tutorial-kubernetes-deploy-cluster#connect-to-cluster-using-kubectl)

### Switching to the correct context  
Once connected to your cluster, you will need to set the appropriate context.
```
$ kubectx
gke_astronomer-demo_us-west2-a_astronomer-demo-ltgzkozwnr

$ kubectx gke_astronomer-demo_us-west2-a_astronomer-demo-ltgzkozwnr
Switched to context "gke_astronomer-demo_us-west2-a_astronomer-demo-ltgzkozwnr".
```

### Switching to the correct namespace
After setting the context, you will want to switch into the appropriate namespace. Using the `kubens` command, you will see a separate namespace for each airflow instance you have created in Astronomer.

```
$ kubens
astronomer-demo-true-transit-3925
astronomer-demo-meteoric-meteorite-9699

$ kubens astronomer-demo-meteoric-meteorite-9699
Context "gke_astronomer-demo_us-west2-a_astronomer-demo-ltgzkozwnr" modified.
Active namespace is "astronomer-demo-meteoric-meteorite-9699".
```
### Retrieving pod names
Once in the desired namespace, you can list the pod names. For our purposes, we need to make sure that we take a pod that has Airflow installed on it. This means the scheduler, webserver, or workers.

```
$ kubectl get pods
NAME                                                 READY     STATUS    RESTARTS   AGE
meteoric-meteorite-9699-flower-67b5c956bb-d2k27      1/1       Running   0          7m
meteoric-meteorite-9699-pgbouncer-874d47799-2j74x    2/2       Running   0          7m
meteoric-meteorite-9699-redis-0                      1/1       Running   0          7m
meteoric-meteorite-9699-scheduler-7f5ccc7fdb-pfdq5   1/1       Running   0          7m
meteoric-meteorite-9699-statsd-69548ddcbc-n8cgv      1/1       Running   0          7m
meteoric-meteorite-9699-webserver-684b7b56d4-zr7ff   1/1       Running   0          7m
meteoric-meteorite-9699-worker-0                     2/2       Running   0          7m
```

## Examples
Once you have retrieved a pod name (remember, it needs to be one that has airflow installed!) your can `exec` into it and then execute the relevant airflow commands as below.
### Adding Connections
```
$ kubectl exec -it meteoric-meteorite-9699-scheduler-7f5ccc7fdb-pfdq5 -- airflow connections --add --conn_id a_new_connection  --conn_type ' ' --conn_login etl --conn_password my_password
	Successfully added `conn_id`=a_new_connection :  ://etl:my_password@:
```

### Adding Variables
```
$ kubectl exec -it meteoric-meteorite-9699-scheduler-7f5ccc7fdb-pfdq5 -- airflow variables --set my_key my_value
```
