---
title: "Astronomer EE DevOps"
description: "Logging in Astronomer Enterprise."
date: 2018-10-12T00:00:00.000Z
slug: "ee-operator"
menu: ["Enterprise Edition"]
position: [5]
---


*Note*: This doc assumes `kubectl` access to the dedicated cluster that is running Astronomer Enterprise edition.

## Astronomer Pods.

Running `kubectl get pods --all-namepsaces` will return the Astronomer core platform pods, along with pods specific to each Airflow deployment.


```bash
kubectl get pods --all-namespaces

NAMESPACE                NAME                                                                    READY     STATUS    RESTARTS    AGE
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-flower-64fdbf57cf-8d522                     1/1       Running   0          53d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-pgbouncer-5bcf8bb75f-b2jm2                  2/2       Running   0          9d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-redis-0                                     1/1       Running   0          53d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-scheduler-7854bbffb9-9zb9h                  1/1       Running   2          2d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-statsd-86c569cc94-f7nz2                     1/1       Running   0          53d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-webserver-7c58b7ccdf-4r6z5                  1/1       Running   0          2d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-worker-0                                    2/2       Running   0          2d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-worker-1                                    2/2       Running   0          2d
astronomer-ee-lunar-nuclear-3725   lunar-nuclear-3725-worker-2                                    2/2       Running   0          2d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-flower-868d5c5cd5-ggfcx                      1/1       Running   0          53d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-pgbouncer-5c4d4fb74-6tlxq                    2/2       Running   0          53d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-redis-0                                      1/1       Running   0          53d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-scheduler-5bf6db96c4-f5c2z                   1/1       Running   2          2d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-statsd-67cc6954cd-fhxmh                      1/1       Running   0          53d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-webserver-846d8b9f97-crklb                   1/1       Running   0          2d
astronomer-ee-zodiac-cosmo-1172    zodiac-cosmo-1172-worker-0                                     2/2       Running   0          2d
astronomer-ee                      jaundiced-joey-postgresql-7c5448c84f-wr7kh                     1/1       Running   0          64d
astronomer-ee                      pg-sqlproxy-gcloud-sqlproxy-6bc5f645db-8bblz                   1/1       Running   1          91d
astronomer-ee                      solitary-lightningbug-cli-install-658db798c7-dg5tn             1/1       Running   0          53d
astronomer-ee                      solitary-lightningbug-commander-b74b5f6df-88mx2                1/1       Running   0          53d
astronomer-ee                      solitary-lightningbug-grafana-6cb476584f-fcwz7                 1/1       Running   0          53d
astronomer-ee                      solitary-lightningbug-houston-6db6f8b876-xf9rw                 1/1       Running   0          8d
astronomer-ee                      solitary-lightningbug-nginx-5bf88f555c-xfw67                   1/1       Running   0          9d
astronomer-ee                      solitary-lightningbug-nginx-default-backend-84c84ccd79-2g7sh   1/1       Running   0          23d
astronomer-ee                      solitary-lightningbug-orbit-79d966946f-d825x                   1/1       Running   0          53d
astronomer-ee                      solitary-lightningbug-prometheus-0                             1/1       Running   0          53d
astronomer-ee                      solitary-lightningbug-registry-0                               1/1       Running   0          21d
```

There will only be 1 set of platform pods (the pods in the `astronomer-ee` namespace), and then a set of Airflow pods (in the `astronomer-ee-zodiac-cosmo-1172` and `astronomer-ee-lunar-nuclear-3725`) per Airflow deployment.
The `STATUS` of each pod generally indicates whether or not the pod is performing as expected. The core Astronomer pods are responsible for making sure the platform is communicating correctly with each of the Airflow deployments (e.g. making sure deploys go through, collecting stats for Grafana, etc.), while the pods for each Airflow deployment are only responsible for that Airflow deployment. For example, in the output above, the `lunar-nuclear-3725-scheduler-7854bbffb9-9zb9h ` is completely unaware of the `zodiac-cosmo-1172-webserver-846d8b9f97-crklb` pod.

### Restarting Pods

When something isn't functioning as expected, the first thing to try is to delete the pod. Deleting the pod will restart it and usually fix sporadic errors (e.g. scheduler stuck, inaccurate Flower dashboard, etc).

To delete the scheduler pod:

```
kubectl delete po/zodiac-cosmo-1172-scheduler-5bf6db96c4-f5c2z -n astronomer-ee-zodiac-cosmo-1172
```

Most pods will restart within 2 minutes of being deleted. However, worker pods will wait until they finish all tasks that are being run are complete or until the configured `flush period`. In general, since Celery workers have to attached to a stateful set to push logs, they will take the longest to restart.

Restarts can be forced by adding additional flags
```
kubectl delete po/lunar-nuclear-3725-worker-0 --force --grace-period=0 -n astronomer-ee-lunar-nuclear-3725
```

### Deleting Volumes

Data that persists across deploys (e.g. logs, grafana metrics, etc.) are stored in persistent volumes. If pods that push data to those volumes are stuck in a `CrashLoopBackff` state, deleting the volumes might fix them.
```
kubectl get pvc --all-namespaces


NAMESPACE                NAME                                                        STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
astronomer-ee--lunar-nuclear-3725   logs-lunar-nuclear-3725-worker-0                            Bound     pvc-33b6a4a1-dea2-11e8-a761-42010a8001e7   100Gi      RWO            standard       8d
astronomer-ee--lunar-nuclear-3725   logs-lunar-nuclear-3725-worker-1                            Bound     pvc-4d316d67-dc80-11e8-a761-42010a8001e7   100Gi      RWO            standard       10d
astronomer-ee--lunar-nuclear-3725   logs-lunar-nuclear-3725-worker-2                            Bound     pvc-a5e035dc-dea0-11e8-a761-42010a8001e7   100Gi      RWO            standard       8d
astronomer-ee--lunar-nuclear-3725   redis-db-lunar-nuclear-3725-redis-0                         Bound     pvc-d40e0872-bb60-11e8-89f0-42010a800044   1Gi        RWO            standard       53d
astronomer-ee--zodiac-cosmo-1172    logs-zodiac-cosmo-1172-worker-0                             Bound     pvc-99a67235-bb5f-11e8-89f0-42010a800044   100Gi      RWO            standard       53d
astronomer-ee--zodiac-cosmo-1172    logs-zodiac-cosmo-1172-worker-1                             Bound     pvc-e40c9908-bb83-11e8-89f0-42010a800044   100Gi      RWO            standard       52d
astronomer-ee--zodiac-cosmo-1172    logs-zodiac-cosmo-1172-worker-2                             Bound     pvc-e411d3d1-bb83-11e8-89f0-42010a800044   100Gi      RWO            standard       52d
astronomer-ee--zodiac-cosmo-1172    redis-db-zodiac-cosmo-1172-redis-0                          Bound     pvc-998a0023-bb5f-11e8-89f0-42010a800044   1Gi        RWO            standard       53d
astronomer-ee-                      jaundiced-joey-postgresql                                   Bound     pvc-9214694a-8c41-11e8-920f-42010a8000c8   8Gi        RWO            standard       113d
astronomer-ee-                      prometheus-data-volume-fun-abalone-prometheus-0             Bound     pvc-85827034-8c28-11e8-920f-42010a8000c8   50Gi       RWO            standard       113d
astronomer-ee-                      prometheus-data-volume-solitary-lightningbug-prometheus-0   Bound     pvc-7308237a-8ea7-11e8-920f-42010a8000c8   50Gi       RWO            standard       110d
astronomer-ee-                      redis-data-tufted-rat-redis-master-0                        Bound     pvc-3b84ea18-8064-11e8-920f-42010a8000c8   8Gi        RWO            standard       128d
astronomer-ee-                      registry-data-volume-solitary-lightningbug-registry-0       Bound     pvc-34f0f858-941b-11e8-920f-42010a8000c8   50Gi       RWO            standard       103d

```

Similarly to pods, volumes can be deleted with:

```
kubectl delete pvc prometheus-data-volume-fun-abalone-prometheus-0 -n astronomer-ee-
```

Deleting the pods will lose all data that they hold. Once the pvc is deleted, the pod that is writing to it should also be restarted.

Generally, if the Prometheus pod is in a `CrashLoopBackff`, deleting the volume will fix it.
If it does not, try (in this order):
1) Scale it to 0
2) Bump the resources
3) Delete the volume
4) Scale it back to 1
5) Delete the pod

### Dealing with "Unscheduleable Pods"

When a pod's status is `Unscheduleable` it means Kubernetes is having trouble allocating resources for it.

Resource quotas determine how many resources (CPU and RAM) are reserved for a particular namespace on a Kubernetes cluster. Since each airflow deployment runs in its own namespace, quotas can be modified for _each_ Airflow instance.

The first thing to try when a pod is unscheduleable is to make sure the resource quoata for that namespace lines up with what is being requested.

```
`kubectl get resourcequotas`
```
```
kubectl edit resourcequotas/<quota_name>
```

It is important to note that even if a cluster has excess capacity, it will not delegate more resources to a namespace than what its quota asks for.

If the resourcequota looks okay relative to the resource requested by the pod and the size of the cluster, it could be related to the node pool.

Suppose you have 3 nodes in your node pool with 2 CPUs and 2GB of memory, and 3 nodes with 10 CPUs and 10 GBs of RAM. You could run into a case where you are requesting 3 CPUs for a particular pod, but it is trying to be scheduled on one of the pods with only 2 CPUs.
Even though the cluster has more than enough resources to fulfill this request, the pod could be "unscheduleable" for a while until it tries to get scheduled on one of the bigger nodes.

To check and see which nodes are running which pods, run:

```
kubectl describe nodes
```

This will show which pods are on which nodes and how much resources they are taking up. Try deleting the pod until it tries to schedule on the correct node.

## Grafana

Astronomer Enterprise Admins will have access to Grafana for monitoring the cluster performance. By default the person who set up the platform will be the only one with access to Grafana.

Users can be added via graphql:

1) Log in and navigate to app.BASEDOMAIN/token and grab the auth token

2) Navigate to houston.BASEDOMAIN/playground

3) Under `HTTP HEADERS` on the bottom, enter the token as `{"authorization": "TOKEN"}`

4) Once the user as signed up, they can be added to the admin group for Grafana access:
```
# Returns user UUID

query GetUser {
  users(email: "viraj@astronomer.io") {
    uuid
  }
```
```
# Returns default-admin UUID

query GetAdminGroup {
  groups(entityType: "system") {
    uuid
    label
  }
}
```
```
# Gives user Grafana access
mutation AddAdmin {
  groupAddUser(
    groupUuid: "c975c787-6d47-4db2-b2e8-b5c4e030fea6"
    userUuid: "ae7f5c3e-2ffa-487f-ba8f-6c6e0cbe5940"
  ) {
    label
    users {
      emails {
        address
      }
    }
  }
}

```

The default Grafana user/password is `admin/admin`. It can be modified by jumping into the Grafana pod and then using the Grafana CLI.

```
kubectl exec -it solitary-lightningbug-grafana-6cb476584f-fcwz7 /bin/bash -n astronomer-ee
```
To reset the password to `admin321`:
```
cd /usr/share/grafana && grafana-cli admin reset-admin-password admin321 --config=/etc/grafana/grafana.ini
```
