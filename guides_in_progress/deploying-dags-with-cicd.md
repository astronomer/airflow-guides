---
layout: page
title: Deploying DAGs with CI/CD
permalink: /guides/deploying-dags-with-cicd/
hide: true
---

# Deploying DAGS with CI/CD

With the introduction of service accounts in v0.6.0 you can now deploy DAGs with your continuous integration/continuous deployment (CI/CD) tool of choice. This guide will walk you through configuring your CI/CD tool to use a Astronomer EE service accounts in order to build and push your Airflow project Docker images to the private Docker registry that is installed with Astronomer EE.

This guide will focuse on DroneCI, but the principles can be applied to CircleCI, Travis CI, Jenkins, Codeship, TeamCity, GitLab CI/CD, or any other CI/CD system.

For background information and best practices on CI/CD, we recommend reading the article [An Introduction to CI/CD Best Practices][0] from DigitalOcean.

## Steps for Setting up CI/CD with Your Astronomer EE Airflow Project
Before we get started, this guide assumed you have installed Astronomer Enterprise Edition or are using Astronomer Cloud Edition, have the [astro-cli](https://github.com/astronomerio/astro-cli) v0.6.0 or newer installed locally and are familiar with your CI/CD tool of choice. You can check your astro-cli version with the `astro version` command.

### Create a Service Account

In order to authenticate your CI/CD pipeline to the private Docker registry you will need to create a service account. This service account access can be revoked at any time by deleting the service account through the astro-cli or orbit-ui.

Here are a few examples of creating service accounts with various permission levels via the astro-cli

__Deployment Level Service Account__

```sa
astro service-account create -d [DEPLOYMENTUUID] --label [SERVICEACCOUNTLABEL]
```

__Workspace Level Service Account__
```sa
astro service-account create -w [WORKSPACEUUID] -l [SERVICEACCOUNTLABEL]
```

__System Level Service Account__
```sa
astro service-account create -s --label [SERVICEACCOUNTLABEL]
```

If you prefer to provision a service account through the orbit-ui you can create a service account on the project configuration page at the following link (replacing [BaseDomain] for your configured base domain).

https://app.[BaseDomain]/login

### Configuring Your CI/CD Pipeline

Depending on your CI/CD tool, configuration will be slightly different. This section will focus on outlining what needs to be accomplished, not the specifics of how. At the end you can find an example to a drone-ci project which demonstrates a properly configured Astronomer EE Airflow Project CI/CD.

At it's core, your CI/CD pipeline will be authenticating to the private registry installed with the platform, then building, tagging and pushing an image to that registry.

#### Authenticating to Docker
After you have created a service account, you will want to store the generated API key in an environment variable, or your secret management tool of choice.

ex
```bash
docker login registry.$${BASE_DOMAIN} -u _ -p $${API_KEY_SECRET}
```

#### Building and Pushing an Image
Once you are authenticated you can build, tag and push your Airflow image to the private registry, where a webhook will trigger an update of your Airflow deployment on the platform.

There are a couple key variables you will need to pay attention to when building and pushing your image.


__Registry Address__
The registry address tells Docker where to push images to. In this case it will be the private registry installed with Astronomer EE, which will be located at registry.${BASE_DOMAIN}.

__Release Name__
Release name refers to the release name of your Airflow Deployment. It will follow the pattern of [SPACE THEMED ADJ.]-[SPACE THEMED NOUN]-[4-DIGITS]. For example, lunar-asteroid-1234 or parabolic-moonshot-6789. This release name is used as the repository name for your Airflow deployment. This means all image tags for that deployment will live under the respository name.

__Tag Name__
Tag name allows you to track all Airflow deployments made for that cluster over time. While the tag name can be whatever you want, we recommend denoting the source and the build number in the name.

In the below example we use the prefix `ci-` and the ENV `${DRONE_BUILD_NUMBER}`. This guarentees that we always know which CI/CD build triggered the build and push.

Example

```bash
docker build -t registry.${BASE_DOMAIN}/${RELEASE_NAME}/airflow:ci-${DRONE_BUILD_NUMBER} .
```


If you would like to see a more complete working example please visit our [full example using Drone-CI](https://github.com/astronomerio/example-dags/blob/master/.drone.yml).
