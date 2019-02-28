---
title: "Astronomer vs. Google Cloud Composer"
description: "A high-level comparison of Astronomer and Google Cloud Composer"
date: 2018-08-30T00:00:00.000Z
slug: "google-composer-comparison"
heroImagePath: null
tags: ["Astronomer Platform", "Google Composer"]
---

It looks like 2019 may just be turning out to be the year of Apache Airflow. Since the project started at Airbbnb in 2014, the need for a reliable and scalable scheduler has become much more widely acknowledged while “competitors” -- there should be a different term for that when it comes to open-source projects -- such as Luigi and Azkaban have slowed in development and adoption.

As it happens, in 2018, [we announced our Enterprise offering](https://www.astronomer.io/blog/announcing-astronomer-enterprise-edition/) for a self-hosted Airflow management solution and Google announced their entry into the market with the Cloud based “Composer”. We’re incredibly excited that wider commercialization of the project is occurring but for the sake of clarity as both platforms continue to develop, we wanted to answer some quick questions we’ve gotten on how Astronomer is different from Composer.

We've since developed [Astronomer Cloud](https://astronomer.io/cloud), a fully-managed Airflow service that's a direct competitor to Google Composer.

*NOTE: As you might expect, we’re not heavy users of Composer and this comparison is derived from customer feedback and what we could find in the public documentation and associated StackOverflow, etc. communities at the time of this writing. If anything appears incorrect, please let us know and we’ll address ASAP.*

## At a Glance

|---|Google Composer|Astronomer Cloud|Astronomer Enterprise|
|-----------|-----------------|------------------|-----------------------|
|Cost|~$300 base (based on user feedback)|$110 base running local executor|Annual license pending cluster CPU|
|Hosting|Managed service hosted in Google's cloud environment|Managed service hosted in Astronomer's Cloud environment|Self-hosted service hosted on customer's Kubernetes cluster|
|Python Version|2.7|3.6|Whatever you choose|
|Monitoring and Logging|Google Stackdriver|Elasticsearch, Fluentd, Kibana (EFK) stack for log text search and filtering|EFK Stack for logs and Prometheus/Grafana stack to track resource usage across all Airflow deployments|
|Support|Community support via Stack Overflow|Standard support ticketing system, [our community forum](https:/forum.astronomer.io), and premium support option for real-time support via a shared slack channel |24x7 Business-Critical SLAs available|
|Training|None|[Astronomer SpaceCamp](https://astronomer.io/spacecamp) for on-site Airflow training.|[Astronomer SpaceCamp](https://astronomer.io/spacecamp) for on-site Airflow training|


### Cost
It's hard to nail down a specific cost for Cloud Composer, as they measure the resources your deployments use and tack it onto your standard GCP bill. Based on the [estimates provided](https://cloud.google.com/composer/pricing), a single, full-time instance of Composer should cost ~$300/month (in addition to the Storage and Compute Engine costs) but that also assumes the three workers use the relatively low powered n1-standard-1 (1 vCPU; 3.75GB) machine type.

Astronomer Cloud is billed based on pure resource utilization. You can find our [standard pricing here](https://astronomer.io/pricing), but it costs $110/mo for a deployment with the local executor and $250/mo for a deployment with the Celery executor. You can also toggle resource allocation to your Airflow deployment's scheduler, webserver, and workers to make it run as efficiently as possible and save costs.

Astronomer Enterprise is priced based on an annual subscription license. Please [contact us](https://astronomer.io/contact) if you'd like to see a pricing sheet.

### Python Version
The first thing you’ll notice if you try to run the same dags in Astronomer and Composer is that some unexpected errors get thrown depending on what version of Python you’re using. This is because the version of Python that Astronomer ships with is Python 3.6 while Composer uses [Python 2.7](https://stackoverflow.com/questions/50122366/how-do-i-select-my-airflow-or-python-version-with-cloud-composer) (as of Aug 23, 2018). It’s reasonable to expect that there is still a hefty amount of Python 2 based code floating around out there but given Python 3 has seen wider adoption since coming out about 10 years ago and Python 2’s [“End of Life” date is Jan 1, 2020](https://pythonclock.org), Astronomer decided to go with Python 3. Note that we can also run Python 2 for you if you'd like, it just takes some tweaking under the hood that our team can handle.

### Python Packages
As soon as you `astro airflow init` a new project, a requirements.txt file with be created for you to add any package at any version that's needed to run your dags. If you want to pull in a distributed package on Github but not on PyPi, you can specify the repo and pull it in directly.

In Composer, you can add packages by either specifying the name and version in a requirements.txt or adding them via the Google Cloud CLI. Custom packages not distributed to PyPi can be added via a “dependencies” folder within the “dags” folder.

### System Packages
The base operating system running underneath the Astronomer platform is a distribution of [Linux called Alpine](https://alpinelinux.org/about/), chosen for it’s small size and resource efficiency. As opposed to Debian (123MB) or CentOS (193MB), Alpine comes in at just 3.98MB. For a more in-depth comparison (and how this translates to $$$ when deployed to a cloud that charges for transfer cost), check out this [great post](https://nickjanetakis.com/blog/the-3-biggest-wins-when-using-alpine-as-a-base-docker-image) by Nick Janetakis.


### Deployment
Both Astronomer and Composer currently use a fairly similar setup for executing tasks. Each component of Airflow (Web Server, Scheduler, and Workers) are deployed as pods on Kubernetes using the Celery Executor. The largest difference in deployment between Astronomer and Cloud Composer is where these pods run. While Composer is GCP only, Astronomer will run anywhere with a Kubernetes cluster. We recommend using a managed Kubernetes service from any of the large cloud providers ([Azure AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/), [AWS EKS](https://aws.amazon.com/eks/), [Digital Ocean](https://www.digitalocean.com/products/kubernetes/), [Pivotal PKS](https://pivotal.io/platform/pivotal-container-service), and, yes, even [GCP GKE](https://cloud.google.com/kubernetes-engine/), but you would be equally capable of running in an entirely on-prem Kubernetes cluster.

### Monitoring and Logging

As of the [1.0.0 release](https://cloud.google.com/composer/docs/release-notes#july_19_2018_composer-100-airflow-190), logging in Composer is handled by Stackdriver and based on [fluentd](https://www.fluentd.org). In contrast, logging in Astronomer is handled by [Elasticsearch](https://www.elastic.co/products/elasticsearch).

Astronomer Cloud pulls all of the Airflow scheduler, webserver, and worker logs directly into the application UI using an ElasticSearch, Fluentd, Kibana (EFK) stack.

![logging](https://assets2.astronomer.io/main/guides/logging.png)

Astronomer Enterprise offers the same logging features that we provide in Cloud, but also comes with a separate Grafana/Prometheus monitoring stack to keep an eye on the health and metadata of each of your Airflow deployments.

![grafana](https://assets2.astronomer.io/main/blog/grafana-dashboard.png)

### Support and Training

Composer's support is largely community-based. Users can post questions to forums like [StackOverflow](https://stackoverflow.com) or use the generic [Airflow support system established via Slack](https://apache-airflow-slack.herokuapp.com/).

Astronomer comes out-of-the-box with support plans that give you access to a wealth of Airflow experts. We’ve been using Airflow internally for 2 years and have helped many companies improve their data processes using Airflow- we also have multiple committers on our team that are constantly working to improve the core project. We offer Airflow training on the Astronomer 

You can check out our [support plans here](https://astronomer.io/pricing). If you're interested, you can also [read more about our Airflow training program called SpaceCamp](https://astronomer.io/spacecamp) that is designed to help you learn core Airflow concepts quickly and effectively.