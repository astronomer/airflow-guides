---
layout: page
title: Deploying DAGs with Astro CLI
permalink: /guides/deploying-dags-with-astro-cli/
hide: true
---

# Objective

You have created and tested your Airflow DAG locally via the [astro-cli](https://github.com/astronomerio/astro-cli).
This guide will show you how to deploy a DAG to your Astronomer EE cluster.

## Requirements

- [Astronomer EE](http://enterprise.astronomer.io/) deployed
- [astro-cli](https://github.com/astronomerio/astro-cli) installed
- [An Astronomer EE Airflow Project](http://enterprise.astronomer.io/guides/creating-an-airflow-project/index.html) you want to push to your cluster

## Authenticating With Your Registry

The first setting we need to configure is the location of your private Docker
registry. This houses all Docker images pushed to your Astronomer EE deploy.
By default it is located at `registry.[baseDomain]`. If you are unsure about
which domain you deployed Astronomer EE to, you can refer back to the
`baseDomain` in your [`config.yaml`](http://enterprise.astronomer.io/guides/google-cloud/index.html#configuration-file).

Run the following command from your project root directory:

```
bash
astro auth login -d [baseDomain]
```

At this point you will be prompted for your registry username and password.
These credentials are the same as what you supplied to the `registry-auth` [secret](http://enterprise.astronomer.io/guides/google-cloud/index.html#secrets)
during your Astronomer EE install.

## Deployment

We have now configured the astro-cli to point at your Astronomer EE deploy and
are ready to push your first DAG. You will need the release name of your
Astronomer EE deployment. This release name was created by the Helm package
manager during your Astronomer EE deploy. If you are unsure of what release
name was created for your deploy, you can run `helm ls` to get a list of all
Helm releases and find the one that has an "Updated" timestamp corresponding
to the time at which you deployed Astronomer EE. If it is still unclear which
Helm release you should deploy to, it is best to contact your cluster
Administrator.

```
bash
astro airflow deploy [release-name]
```

After running this command you will see some stdout as the CLI builds and pushes
images to your private registry. After a deploy, you can view your updated
instance. If using the default install this will be located at
`airflow.[baseDomain]`.
