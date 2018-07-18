---
layout: page
title: Databases
permalink: /guides/databases/
hide: true
---



## Preparing

Before installing Astronomer Enterprise's Airflow module,
you'll need to bring Postgres and Redis that will serve as back-ends
to the platform. You can bring these databases with you or run them
in Kubernetes via helm package(s). This guide will assume
that you want to run via the helm packages, which can be useful for local
development at least.

## Redis Deploy

[Redis][8]{:target="_blank"} is an in-memory data structure store that we will be using as a message broker for [Celery][3]{:target="_blank"}.

1. run `helm install stable/redis`
1. Capture the resource URL from successful deployment out
    - The output contains a header titled "NOTES:"
    - In a new text doc save this URL
1. Follow the output instructions to capture your REDIS_PASSWORD
    - `echo $REDIS_PASSWORD`
    - Save this in a text doc with the Redis URL
1. Verify by running `helm ls` to see the status of your deployment

## PostgreSQL Deploy

[PostgreSQL][9]{:target="_blank"} is an open-source relational DB that will serve as the back-end to Apache Airflow, Celery and Grafana. There is currently a minor bug in the stable helm chart, so for this install we will be using the Astronomer fork.

1. `git clone https://github.com/astronomerio/charts.git`
1. `cd charts/stable`
1. run `helm install postgresql`
1. Capture the resource URL from successful deployment output
    - The output contains a header titled "NOTES:"
    - In a new text doc save this URL
1. Follow the output instructions to capture your PGPASSWORD
    - `echo $PGPASSWORD`
    - Save this in a text doc with the PostgreSQL URL
1. Verify by running `helm ls` to see the status of your deployment

## Astronomer Deployment
Use the password that is output by the previous installs to construct connection strings needed to deploy the platform.

Note: If deploying a database in a separate Kubernetes namespace, you'll need to use fully qualified URLs for the PostgreSQL and/or Redis host. For example, `intentional-marmot-postgresql` would become `intentional-marmot-postgresql.default.svc.cluster.local` where `default` is the database's Kubernetes namespace. Make sure you use the master URL for your Redis database connection, `clever-puma-redis` would be `clever-puma-redis-master` and if deploying in another namespace the full url would be `clever-puma-redis-master.default.svc.cluster.local`

## Verification

1. Navigate to your Kubernetes Dashboard
    - <http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/>
1. Change your namespace on the left-side panel from `default` to `astronomer-system`
1. Verify that all your pods are all-green

[1]: /create-local-k8-dev.md                                            "Kubernetes On Docker Installation Guide"
[2]: https://airflow.apache.org/                                        "Apache Airflow"
[3]: http://www.celeryproject.org/                                      "Celery: Distributed Task Queue"
[4]: http://flower.readthedocs.io/en/latest/                            "Flower: A Celery Monitoring Tool"
[5]: https://grafana.com/                                               "Grafana Monitoring"
[6]: https://prometheus.io/                                             "Prometheus Time Series Monitoring"
[7]: https://kubernetes.io/docs/concepts/services-networking/ingress/   "Ingress: DNS"
[8]: https://redis.io/                                                  "Redis Homepage"
[9]: https://www.postgresql.org/                                        "PostgreSQL Database"
