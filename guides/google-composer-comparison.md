---
title: "Astronomer vs. Google Cloud Composer"
description: "A high-level comparison of Astronomer and Google Cloud Composer"
date: 2018-08-30T00:00:00.000Z
slug: "google-composer-comparison"
heroImagePath: null
tags: ["Astronomer Platform", "Google Composer"]
---

It looks like 2018 may just be turning out to be the year of Apache Airflow. Since starting in its first incarnation back in 2014, the need for a reliable and scalable scheduler has become much more widely acknowledged while “competitors” -- there should be a different term for that when it comes to open-source projects -- such as Luigi and Azkaban have slowed in development and adoption.

As it happens, 2018 just so happens to be the year [we announced our Enterprise offering](https://www.astronomer.io/blog/announcing-astronomer-enterprise-edition/) for a self-hosted Airflow management solution and Google announced their entry into the market with the Cloud based “Composer”. We’re incredibly excited that wider commercialization of the project is occurring but for the sake of clarity as [both platforms continue to develop](https://www.astronomer.io/blog/astronomer-v0-4-1-release/), we wanted to answer some quick questions we’ve gotten on how Astronomer is different from Composer.

*NOTE: As you might expect, we’re not heavy users of Composer and this comparison is derived from customer feedback and what we could find in the public documentation and associated StackOverflow, etc. communities at the time of this writing. If anything appears incorrect, please let us know and we’ll address ASAP.*

## Key Differences
### Python Version
The first thing you’ll notice if you try to run the same dags in Astronomer and Composer is that some unexpected errors get thrown depending on what version of Python you’re using. This is because the version of Python that Astronomer ships with is Python 3.6 while Composer uses [Python 2.7](https://stackoverflow.com/questions/50122366/how-do-i-select-my-airflow-or-python-version-with-cloud-composer) (as of Aug 23, 2018). It’s reasonable to expect that there is still a hefty amount of Python 2 based code floating around out there but given Python 3 has seen wider adoption since coming out about 10 years ago and Python 2’s [“End of Life” date is Jan 1, 2020](https://pythonclock.org), Astronomer decided to go with Python 3.

### Python Packages
As soon as you `astro airflow init` a new project, a requirements.txt file with be created for you to add any package at any version that's needed to run your dags. If you want to pull in a distributed package on Github but not on PyPi, you can specify the repo and pull it in directly.

In Composer, you can add packages by either specifying the name and version in a requirements.txt or adding them via the Google Cloud CLI. Custom packages not distributed to PyPi can be added via a “dependencies” folder within the “dags” folder.

### System Packages
The base operating system running underneath the Astronomer platform is a distribution of [Linux called Alpine](https://alpinelinux.org/about/), chosen for it’s small size and resource efficiency. As opposed to Debian (123MB) or CentOS (193MB), Alpine comes in at just 3.98MB. For a more in-depth comparison (and how this translates to $$$ when deployed to a cloud that charges for transfer cost), check out this [great post](https://nickjanetakis.com/blog/the-3-biggest-wins-when-using-alpine-as-a-base-docker-image) by Nick Janetakis.

### Airflow Version
Starting with Airflow v1.8, Astronomer (as of v0.5.0) allows you to choose which version of Airflow you would like (1.9, 1.10, etc.). Composer automatically pulls the most recent version of Airflow, typically a [few weeks after it is released](https://stackoverflow.com/questions/50122366/how-do-i-select-my-airflow-or-python-version-with-cloud-composer). Composer does not allow you to modify the version of Airflow or Python that you are using.

### Development
Run Astronomer locally. In addition to the Astronomer Enterprise Edition, we offer a local install allowing you to easily spin up a local environment for testing before deploying to your Enterprise instance.

### Deployment
Both Astronomer and Composer currently use a fairly similar setup for executing tasks. Each component of Airflow (Web Server, Scheduler, and Workers) are deployed as pods on Kubernetes using the Celery Executor. The  largest difference, then, is where these pods run. While Composer is GCP only, Astronomer will run anywhere with a Kubernetes cluster. We recommend using a managed Kubernetes service from any of the large cloud providers ([Azure AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/), [AWS EKS](https://aws.amazon.com/eks/), [Digital Ocean](https://www.digitalocean.com/products/kubernetes/), [Pivotal PKS](https://pivotal.io/platform/pivotal-container-service), and, yes, even [GCP GKE](https://cloud.google.com/kubernetes-engine/), but you would be equally capable of running in an entirely on-prem Kubernetes cluster.

### Monitoring and Logging
Monitoring on Astronomer is handled via a Grafana dashboard (backed by Prometheus) that shows resource usage across all deployments. Composer uses [Google StackDriver](https://cloud.google.com/stackdriver/) for resource monitoring which can then be queried for specific metrics.

As of the [1.0.0 release](https://cloud.google.com/composer/docs/release-notes#july_19_2018_composer-100-airflow-190), logging in Composer is handled by Stackdriver and based on [fluentd](https://www.fluentd.org). In contrast, logging in Astronomer is handled by [Elasticsearch](https://www.elastic.co/products/elasticsearch).


### Cost
It’s hard to compare costs between the two services as Astronomer charges a fixed, annual license fee (although we do also have a SaaS offering that is billed monthly) that covers unlimited users and airflow instances while Composer bills at a per minute rate based on web core hours, database core hours, web and database storage, and network egress in addition to Cloud Storage and Compute Engine charges.

Based on the [estimates provided](https://cloud.google.com/composer/pricing), a single, full-time instance of Composer should cost ~$300/month (in addition to the Storage and Compute Engine costs) but that also assumes the three workers use the relatively low powered n1-standard-1 (1 vCPU; 3.75GB) machine type.

### Support and Training
Along with everything available through the Astronomer platform, you also have access to support, and a wealth of Airflow experts. We’ve been using Airflow internally for 2 years and have helped many companies improve their data processes using Airflow. We offer Airflow training on the Astronomer platform through our [SpaceCamp](www.astronomer.io/spacecamp) program to help supercharge your Airflow endeavors.
