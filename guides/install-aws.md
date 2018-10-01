---
title: "Install Astronomer to Amazon Web Services (AWS)"
description: "Install Astronomer to Amazon Web Services (AWS)"
date: 2018-07-17T00:00:00.000Z
slug: "install-aws"
heroImagePath: "https://assets.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Astronomer Platform", "Getting Started"]
---

This guide describes the prerequisite steps to install Astronomer on Amazon Web Services (AWS).

## Are you devops-y enough to do this alone?

You will need to be able to:

* Obtain a wildcard SSL certificate
* Edit your DNS records
* Create resources on AWS
* Install/run Kubernetes command line tools to your machine

## Prerequisites

Before running the Astronomer install command you must:

1. [Select a base domain](/guides/install-base-domain)
1. [Get your machine setup with needed dev tools](/guides/install-dev-env)
1. [Create a stateful storage set](/guides/install-aws-stateful-set)
1. [Get a Postgres server running](/guides/install-postgres)
1. [Obtain SSL](/guides/install-ssl)
1. [Set a few Kubernetes secrets](/guides/install-k8s-secrets)
1. [Build your config.yaml](/guides/install-config)


## Install Astronomer

You're ready to go!

```shell
helm install -f config.yaml . --namespace astronomer
```

## DNS routing

Your final step is to setup your DNS to route traffic to your airflow resources following [these steps](/guides/install-aws-dns).

Click the link in the output notes to log in to the Astronomer app.

## FAQ's

1. **Do I absolutely need a base domain?**

    Yes. There is unfortunately no work-around to the base domain requirement. In order to properly install each part of our platform, we absolutely need a base domain as a foundation.
    
    For example, if companyx.com was your base domain, we’d create houston.companyx.com (our API), or astronomer.companyx.cloud.io etc, and there’s unfortunately no way to abstract that.


    Once you have a base domain set up, you can use a cert manager to generate a short-lived wildcard, which should be relatively easy.

2. **What about EKS?**

    You'll need to spin up a default EKS cluster (Amazon's managed Kubernetes Service), on top of which the Astronomer platform is deployed.
    
    As it’s a relatively new product, most of our resources are outlinked to EKS itself.
    
    Here’s our version of an EKS getting started guide: http://enterprise.astronomer.io/guides/aws/index.html (We’ll be porting over that guide to our official docs site soon)



    

