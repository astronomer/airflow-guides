---
title: "Install Astronomer to Amazon Web Services (AWS)"
description: "Install Astronomer to Amazon Web Services (AWS)"
date: 2018-07-17T00:00:00.000Z
slug: "install-aws"
heroImagePath: null
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

---

## Frequently Asked Questions

### Do I absolutely need a base domain?

Yes. There is unfortunately no work-around to the base domain requirement. In order to properly install each part of our platform, we absolutely need a base domain as a foundation.

For example, if companyx.com was your base domain, we’d create houston.companyx.com (our API), or astronomer.companyx.cloud.io etc. for you to access all parts of your deployment, and there’s unfortunately no way to abstract that.

Once you have a base domain set up, you can use a cert manager to generate a short-lived wildcard, which should be relatively easy. (Check out a blog from LetsEncrypt that might help [here](https://www.bennadel.com/blog/3420-obtaining-a-wildcard-ssl-certificate-from-letsencrypt-using-the-dns-challenge.htm])). 

### What about EKS?

You'll need to spin up a default EKS cluster (Amazon's managed Kubernetes Service), on top of which the Astronomer platform is deployed.

As it’s a relatively new product, most of our resources are outlinked to EKS itself.

Here’s our version of an EKS getting started guide: http://enterprise.astronomer.io/guides/aws/index.html (We’ll be porting over that guide to this page soon)

### How is the DNS configured? If I wanted to change or replace my base domain, could I?

Yes, you could! Currently, we have the domain setup with a wildcard CNAME record that points to the ELB DNS route. Swapping out domains would just require adding that CNAME record to your DNS, and recreating the `astronomer-tls` secret to use the updated wildcard certificate for your domain.


### How does Astronomer command the cluster? (Add and remove pods, etc.)

You'll need a role for EKS to manage the cluster, which will be done through Kubectl. Kubectl is the command line interface that can manipulate the cluster as needed, and setup helm/tiller services to deploy the astronomer platform. [Our Kubectl guide](https://www.astronomer.io/guides/kubectl/) might help.

For the IAM policy, we should only need the `AmazonEKSServicePolicy` and the `AmazonEKSServicePolicy`.

Once the kubernetes cluster is created, the IAM user will need to be added to the cluster configMap as described [here](https://docs.aws.amazon.com/eks/latest/userguide/add-user-role.html).

### Do I really need to give Astronomer that much access?

Yes and no. The above permissions are primiarly to help troubleshoot while you're getting setting up. There are a few added dependencies that need to be configured, such as grabbing the DNS name from the provisioned ELB and creating a CNAME record in the DNS. If broad access is a coner, that can be done by someone on your end.

As long as we're able to authenticate an IAM user against the kubernetes cluster using those EKS policies, that should keep us moving.

### Does it matter if I run RDS postgres or stable postgres to run in Kubernetes?

In the long-term, a RDS instance is probably the best approach, but stable postgres should be more than enough. Make sure to use the most explicit route to that RDS to ensure the Kubernetes cluster can connect to it.

### How do I get access to my Grafana dashboard?

Once you've registered, let us know and we'll add you as an administrator on our end.

### Anything I should know about running things locally?

The EC2 instance is what you’ll use to deploy the Astronomer platform into that cluster. The UI is hosted in an nginx pod, and you’ll use the EC3 to communicate to that cluster and deploy.

To run a local version of Airflow, you’re free to download and use our CLI, which comes built with local testing functionality. You can scale from there as needed.

Here's a guide to our CLI: https://www.astronomer.io/guides/cli/

Whatever machine you’re going to use, apply it to the kubectl CLI, and make sure to create a storage class.

### Does the size of my EC2 instance matter?

Not much, we just need as much power from a virtual machine as your standard laptop. You can stick to a standard or small machine type for the EC2.

A low base machine type should be fine for that, and you’ll just need to be able to run : (1) Heptio authenticator (2) Astronomer CLI and (3) Kubectl.

### How do I know when I'm ready with the install?

As soon as you've verified UI and CLI access and can create a test deployment, you're ready to start getting DAGs up :)

### What authorization can I expect?

AuthO is included in the platform install, so no need for additional creds.

### Do you support MFA Authentication?

Yes, Multi-factor Authentication is pluggable with auth0 - you'll just have to enable it on your end. 

Check out these docs: https://auth0.com/docs/multifactor-authentication

### What limits and quotas do you default to on our instance?

Here's a breakdown of the specs you'll see in your instance by default. For troubleshooting purposes, we might talk to your team about adjusting these one way or another depending on your use case, but this is what you can expect to start with.


```
{
        "workers": {
          "resources": {
            "limits": {
              "cpu": "2",
              "memory": "6Gi"
            },
            "requests": {
              "cpu": "500m",
              "memory": "1024Mi"
            }
          },
          "replicas": 1,
          "terminationGracePeriodSeconds": 600
        },
        "scheduler": {
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "1024Mi"
            },
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            }
          }
        },
        "webserver": {
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "1024Mi"
            },
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            }
          }
        },
        "flower": {
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "1024Mi"
            },
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            }
          }
        },
        "statsd": {
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "1024Mi"
            },
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            }
          }
        },
        "pgbouncer": {
          "metadataPoolSize": 5,
          "resultBackendPoolSize": 2,
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "1024Mi"
            },
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            }
          }
        },
        "redis": {
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "1024Mi"
            },
            "requests": {
              "cpu": "100m",
              "memory": "256Mi"
            }
          }
        },
        "quotas": {
          "pods": 100,
          "requests.cpu": "4000m",
          "requests.memory": "16Gi",
          "limits.cpu": "16000m",
          "limits.memory": "64Gi"
        },
        "limits": [{
          "type": "Pod",
          "max": {
            "cpu": "4",
            "memory": "8Gi"
          }
        }, {
          "type": "Container",
          "default": {
            "cpu": "100m",
            "memory": "256Mi"
          },
          "defaultRequest": {
            "cpu": "100m",
            "memory": "256Mi"
          },
          "min": {
            "cpu": "100m",
            "memory": "128Mi"
          }
        }]
      }),
      ```
