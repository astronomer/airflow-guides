---
title: "Recovery Guide"
description: "How to recover a private installation of Astronomer"
date: 2018-08-24T00:00:00.000Z
slug: "ee-administration-recovery-guide"
menu: ["Administration"]
position: [1]
---

# Disaster Recovery Guide
In the event that the platform is taken down, there are a number of restoration points that need to occur, depending on the severity of the outage. This guide assumes the use of a managed Kubernetes service (Google GKE). If running Kubernetes and associated services privately, the disaster recovery procedure will be dictated by your company's internal DevOps plan and may differ from this plan.


## Relaunching the Platform
If the entire platform is taken down, you can restore service through the standard Helm charts provided in the original installation. This will take care of installing Airflow, Grafana, NGINX, Prometheus, and the Astronomer components (Commander Provisioning Service, Houston API, Orbit UI, and internal Docker registry). The exact process for this will depend on what hosting provider you are using (e.g. GCP, AWS)

More information can be found here:
- [Install Astronomer on GCP](https://www.astronomer.io/guides/install-gcp/)
- [Install Astronomer on AWS](https://www.astronomer.io/guides/install-aws/)

## Restoring Postgres
All operational data (DAG runs, task instances, variables, connections) underpinning Airflow on Astronomer is stored in Postgres. In the event that Postgres is made unavailable, this data can be restored as long as a backup is available.

If hosting Kubernetes on a managed service, Astronomer recommends also using a hosted database due to the ease-of-use, affordability, and included disaster recovery options. If using such a service, make sure to set the backup schedule to at least a daily, automated backup with retention set to the last week. With GCP, this is included by default.

Once restored, all DAG states will be set to the state they were at when this backup was made. If running DAGs at a greater frequency and it is critical to be able to restore with a finer granularity, simply set the Postgres backup to a more frequent back up schedule. More information regarding control and pricing of backups on GCP can be found here: https://cloud.google.com/sql/docs/postgres/backup-recovery/backups

![GCP Postgres Backup](https://assets.astronomer.io/website/img/guides/disaster-recovery-guide/gcp-postgres-backup.png)

Simply click on the three vertical dots of the most recent backup and click 'restore', choosing the appropriate Target Instance.

![GCP Postgres Backup](https://assets.astronomer.io/website/img/guides/disaster-recovery-guide/gcp-postgres-restore.png)

## Restoring Prometheus
Prometheus data is stored on the network volumes with the relevant Kubernetes cluster. Due to the reporting nature of Prometheus, Astronomer does not currently feel it necessary to back up Prometheus as any lost metrics will not affect overall recovery or future performance of the platform.  

However, if you would like to ensure that Prometheus be recoverable, it can be set to 2 replicas with a double scrape configuration. More information on this configuration can be found in Prometheus's official documentation: https://prometheus.io/docs/prometheus/latest/configuration/configuration/#scrape_config

## Restoring Redis
Due to the temporary nature of Redis's function, Astronomer does not currently feel it necessary or advisable to restore Redis from a backup.

## Restoring the Registry
The registry holds all previous docker images for deployments and is not recoverable if corrupted. For this reason, it is advisable to rely on git or another code versioning mechanism to retain prior states of your DAG and Plugin directories. To begin populating the registry again, simply `astro airflow deploy` again from your local directory and a new image will appear with the latest code.

If it is necessary to ensure all previous images are available, outside storage backends can be configured.

See below for more information on how:
[Google Cloud Storage Driver](https://docs.docker.com/registry/storage-drivers/gcs/)
[AWS S3 Storage Driver](https://docs.docker.com/registry/storage-drivers/s3/)
