---
title: "Metrics"
description: "Metrics in Astronomer Enterprise."
date: 2018-10-12T00:00:00.000Z
slug: "ee-metrics"
menu: ["Enterprise Edition"]
position: [6]
---

We've built out a robust monitoring stack for Airflow that helps you keep track of your Airflow deployments.

On Enterprise Edition, go to `grafana.{your namespace here}.astronomer.io` to access the monitoring overview.

- All of our dashboards provide live, up-to-date information on the status of Airflow, from the Kubernetes level right to the container level.

- Queries  for dashboards are written in PromQL

- Dashboards are dynamic, so you can pick and choose what specific Airflow deployments you want to track.

## Grafana dashboards

- **Airflow Containers**: Monitor every running container's CPU and memory usage, alongside network I/O.

- **Airflow Database Activity**: High level status overview of Airflow's database.

- **Airflow Deployments**: Drill down into the overall status of every deployment.

- **Airflow Scheduler**: Displays Airflow's core metrics, from the scheduler's perspective.

- **Airflow State**: Monitor all of your deployments from the Kubernetes level, including a birds-eye view of resource usage and system stress levels.

- **Platform Overview**: Overall platform memory and disk usage.
- **Prometheus**: Status and resource usage of the Prometheus database backend.
