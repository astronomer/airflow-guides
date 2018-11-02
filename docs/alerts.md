---
title: "Built-in Alerts"
date: 2018-10-12T00:00:00.000Z
slug: "alerts"
menu: ["root"]
position: [9]
---

Alerts are available in Astronomer v0.7 and higher.

## Airflow Alerts

* `AirflowDeploymentUnhealthy` — Release deployment is unhealthy, not completely available.
* `AirflowFailureRate` — Airflow tasks are failing at a higher rate than normal.
* `AirflowSchedulerUnhealthy` — Airflow scheduler is unhealthy, heartbeat has dropped below the acceptable rate.
* `AirflowPodQuota` — Deployment is near its pod quota, has been using over 95% of it's pod quota for over 10 minutes.
* `AirflowCPUQuota` — Deployment is near its CPU quota, has been using over 95% of it's CPU quota for over 10 minutes.
* `AirflowMemoryQuota` — Deployment is near its memory quota, has been using over 95% of it's memory quota for over 10 minutes.

## Platform Alerts

* `PrometheusDiskUsage` — Prometheus High Disk Usage — Prometheus has less than 10% disk space available.
* `RegistryDiskUsage` — Docker Registry High Disk Usage — Docker Registry has less than 10% disk space available.
* `ElasticsearchDiskUsage` — Elasticsearch High Disk Usage — Elasticsearch has less than 10% disk space available.
* `IngessCertificateExpiration` — TLS Certificate Expiring Soon — The TLS Certificate is expiring in less than a week.

View [full source code](https://github.com/astronomerio/helm.astronomer.io/blob/master/charts/prometheus/values.yaml#L41-L148) for alerts.
