---
title: "Astronomer vs. Google Cloud Composer"
description: "A high-level comparison of Astronomer and Google Cloud Composer"
date: 2018-08-30T00:00:00.000Z
slug: "google-composer-comparison"
heroImagePath: null
tags: []
---

|  | Google Cloud Composer | Astronomer Cloud | Astronomer Enterprise |
|--|-----------------------|------------------|-----------------------|
| Cost | ~$300 base | ~$110 base (via LocalExecutor) | Negotiated Annual subscription |
| Hosting | Managed service hosted in Google's cloud environment | Managed service hosted in Astronomer's cloud environment | Installed in your Kubernetes cluster |
| Monitoring and Logging | Deployment level metrics and logging in the Cloud Console | Deployment level metrics and logging in the Astronomer UI | Prometheus/Grafana + Elasticsearch, Fluentd, Kibana (EFK) stack to track resource usage across all Airflow deployments |
| Support | Community support via Stack Overflow, Slack. [Commercial support](https://cloud.google.com/support) with many plans including 15-min response time for P1 cases in Premium Support | [Commercial support](https://support.astronomer.io/) that includes access to Airflow PMC members, and a [community forum](https:/forum.astronomer.io) | 24x7 Business-Critical SLAs available |
| Services | [QwikiLabs training](https://www.qwiklabs.com/), [Google Certification](https://cloud.google.com/certification), [Google on-site training](https://cloud.google.com/training), and [Consulting services](https://cloud.google.com/consulting) | [Astronomer SpaceCamp](https://astronomer.io/spacecamp) for on-site Airflow training | [Astronomer SpaceCamp](https://astronomer.io/spacecamp) for on-site Airflow training |

## Cost

### Google Cloud Composer

Based on the [estimates provided](https://cloud.google.com/composer/pricing), a single, full-time instance of Composer:

- Costs ~$300/month
- Assumes 3 workers using `n1-standard-1` (1 vCPU; 3.75GB) machine types
- Does not include Storage and Compute Engine costs

### Astronomer

Astronomer Cloud is billed based on exact resources used per deployment. On Astronomer, you're free to adjust resource allocation to each Airflow component (Scheduler, Webserver and Celery Workers) to best fit your budget and use case.

Based on our default resource allocation, it breaks down to:

- $110/mo for a default deployment with Airflow's Local Executor
- $250/mo for a default deployment with the Celery Executor
- $290/mo for a default deployment with the Kubernetes Executor

Node limits for any single task (based on Google's standard-16 machine type) are:

- 58 GB of Memory/RAM
- 15 CPU

For more details, check out our [pricing doc](https://astronomer.io/docs/pricing).

Astronomer Enterprise is priced based on an annual subscription license. Please [contact us](https://astronomer.io/contact) if you'd like to get a quote.

## System Packages

### Astronomer

Astronomer's base Airflow images are based on Debian, which offers a nice package dependency compatibility experience. Our Docker Images are open-sourced and can be found [here](https://hub.docker.com/r/astronomerinc/ap-airflow/).

## Deployment

Both Astronomer and Composer currently use a fairly similar setup for executing tasks. Each Airflow component (Webserver, Scheduler, and Workers) are deployed as pods on Kubernetes using the Celery Executor. The largest difference in deployment between Astronomer and Cloud Composer is where these pods run.

Astronomer Enterprise is entirely cloud agnostic and can be installed on any Kubernetes Cluster. We recommend using a managed Kubernetes service from any of the large cloud providers ([Azure AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/), [AWS EKS](https://aws.amazon.com/eks/), [Digital Ocean](https://www.digitalocean.com/products/kubernetes/), [Pivotal PKS](https://pivotal.io/platform/pivotal-container-service), and [GCP GKE](https://cloud.google.com/kubernetes-engine/)), but you'd be equally able to run it on any flavor of on-prem Kubernetes.

## Monitoring and Logging

**Google Cloud Composer**

Logging in Composer is handled by Stackdriver and based on [fluentd](https://www.fluentd.org). Metrics availlable in [Cloud Monitoring](https://cloud.google.com/composer/docs/how-to/managing/monitoring-environments) and the [Composer monitoring dashboard](https://cloud.google.com/composer/docs/monitoring-dashboard).

**Astronomer**

Logging in Astronomer is handled by [Elasticsearch](https://www.elastic.co/products/elasticsearch).
Metrics are handled by [Prometheus](https://prometheus.io/).

### Real-time Scheduler, Webserver, Worker Logs

Astronomer pulls searchable, real-time logs from your Airflow Scheduler, Webserver, and Workers directly into the Astronomer UI.

### Deployment Level Metrics

We also pull a variety of deployment level metrics into the Astronomer UI, including:

- Container status
- Deployment health
- Task success and failure rates
- CPU and Memory usage
- Database connections

### Cluster Wide Metrics (*Enterprise only*)

Astronomer Enterprise offers the same logging and metrics features incorporated in Astronomer Cloud but also comes with access to a Grafana/Prometheus monitoring stack (the basis for the deployment level metrics above) to keep an eye on health and metadata *across* Airflow deployments.

## Airflow Executor Support

### Google Cloud Composer

Google Cloud Composer supports the CeleryExecutor only.

### Astronomer

Astronomer supports the LocalExecutor, the CeleryExecutor, and the Kubernetes Executor.

To read more, refer to [Airflow Executors: Explained](https://www.astronomer.io/guides/airflow-executors-explained/).

## Services

### Google Cloud Composer

Google Cloud offers different support packages to meet different needs, such as 24/7 coverage, phone support, and access to a technical support manager. For more information, see [Google Cloud Support](https://cloud.google.com/support).

Google Cloud offers Hands-on training via [QwikiLabs](https://www.qwiklabs.com/catalog?keywords=airflow) and [data engineering certification](https://cloud.google.com/certification/guides/data-engineer), and [Google Consulting Services](https://cloud.google.com/consulting).

Composer users can also post questions to [StackOverflow](http://stackoverflow.com/questions/tagged/google-cloud-composer) and [Google Cloud Slack community](https://googlecloud-community.slack.com/).

### Astronomer

Astronomer offers multiple support packages to meet different needs, including 24/7 coverage, phone support, and access to a technical support manager.

In addition, Astronomer's support automatically gives you access our team of Airflow PMC members and committers. We’ve been Airflow users since 2016, and have helped many companies improve their data processes using Airflow.

Our users can also post questions to our [support portal](https://support.astronomer.io/), our [community Airflow support forum](https://forum.astronomer.io/) and we even offer private Slack channels.
