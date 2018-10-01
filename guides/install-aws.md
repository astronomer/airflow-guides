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

2. **How is the DNS configured? If I wanted to chance or replace my base domain, could I?**

    Yes, you could! Currently, we have the domain setup with a wildcard CNAME record that points to the ELB DNS route. Swapping out domains would just require adding that CNAME record to your DNS, and recreating the `astronomer-tls` secret to use the updated wildcard certificate for your domain. 

3. **What about EKS?**

    You'll need to spin up a default EKS cluster (Amazon's managed Kubernetes Service), on top of which the Astronomer platform is deployed.
    
    As it’s a relatively new product, most of our resources are outlinked to EKS itself.
    
    Here’s our version of an EKS getting started guide: http://enterprise.astronomer.io/guides/aws/index.html (We’ll be porting over that guide to our official docs site soon)

4. **How does Astronomer command the cluster? (Add and remove pods, etc.)**

    You'll need a role for EKS to manage the cluster, which will be done through Kubectl. Kubectl is the command line interface that can manipulate the cluster as needed, and setup helm/tiller services to deploy the astronomer platform.
    
    For the IAM policy, we should only need the `AmazonEKSServicePolicy` and the `AmazonEKSServicePolicy`. 

    Once the kubernetes cluster is created, the IAM user will need to be added to the cluster configMap as described [here](https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html).

6. **Do I really need to give Astronomer that much access?**

    Yes and no. The above permissions are primiarly to help troubleshoot while you're getting setting up. There are some added dependencies which need to be configured, such as grabbing the DNS name from the provisioned ELB and creating a CNAME record in the DNS, but that can be done by someone on your side if broad access is a concern. 
    
    As long as we're able to authenticate an IAM user against the kubernetes cluster using those EKS policies, that should keep us moving.

5. **Does it matter if I run either RDS postgres, or stable postrgres to run in Kubernetes?**

    In the long-term, a RDS instance is probably the best approach, but stable postgres should be more than enough. Make sure to use the most explicit route to that RDS to ensure the Kubernetes cluster can connect to it.

6. **How do I get access to my Grafana dashboard?**

    Once you've registered, let us know and we'll add you as an administrator on our end.

7. **Anything I should know about running things locally?**

    The EC2 instance is what you’ll use to deploy the Astronomer platform into that cluster. The UI is hosted in an nginx pod, and you’ll use the EC3 to communicate to that cluster and deploy.
    
    To run a local version of Airflow, you’re free to download and use our CLI, which comes built with local testing functionality, and scale from there as needed.
    
    Here's a huide to our CLI: https://www.astronomer.io/guides/cli/
    
    Whatever machine you’re going to use, apply it to the kubectl CLI, and make sure to create a storage class.
8. **Does the size of my EC2 instance matter?**

    Not much, we just need as much power from a virtual machine as your standard laptop. You can stick to a standard or small machine type for the EC2.
    
    A low base machine type should be fine for that, and you’ll just need to be able to run : (1) Heptio authenticator (2) Astronomer CLI and (3) Kubectl. 

9. **How do I know when I'm ready with the install?**

    As soon as you've verified UI and CLI access and can create a test deployment, you're ready to start getting DAGs up :) 

10. **What authorization can I expect?**

    AuthO is included in the platform install, so no need for additional creds. 






    

