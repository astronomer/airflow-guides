---
title: "DAG Deployment"
description: "How to deploy your DAGs to your Airflow cluster using the Astronomer CLI."
date: 2018-10-12T00:00:00.000Z
slug: "cli-dag-deployment"
menu: ["Astro CLI"]
position: [3]
---

## Deploying to Astronomer Enterprise

**Note:** If you're looking for steps on how to deploy to your Astronomer Cloud account, check out our [Getting Started with Cloud](https://www.astronomer.io/guides/getting-started-with-new-cloud/) guide.

If you're here, you've created and tested your Airflow DAG locally via the [astro-cli](https://github.com/astronomerio/astro-cli). Now, we'll walk through how to deploy the DAG to your Astronomer EE cluster.

### Authenticating With Your Registry

The first setting we need to configure is the location of your private Docker registry. This houses all Docker images pushed to your Astronomer EE deploy. By default it is located at `registry.[baseDomain]`. If you are unsure about which domain you deployed Astronomer EE to, you can refer back to the `baseDomain` in your [`config.yaml`](http://enterprise.astronomer.io/guides/google-cloud/index.html#configuration-file).

Run the following command from your project root directory:

```bash
astro auth login [baseDomain]
```

Depending on the type of authentication you are using, the process will be a little different. If you are using the default Google OAuth, leave the Username field blank and continue follow the instructions on the terminal.

Run `astro workspace list` to see a list of all the workspaces you have access to. You can switch between workspaces with `astro workspace switch [UUID]`. 

### Deployment

We have now configured the astro-cli to point at your Astronomer EE deploy and are ready to push your first DAG. You will need the release name of your Astronomer EE deployment. This release name was created by the Helm package manager during your Astronomer EE deploy. If you are unsure of what release
name was created for your deploy, you can run `helm ls` to get a list of all Helm releases and find the one that has an "Updated" timestamp corresponding to the time at which you deployed Astronomer EE. If it is still unclear which Helm release you should deploy to, it is best to contact your cluster Administrator.

```bash
astro airflow deploy [release-name]
```

If you do not include a release name, you will be prompted to choose from a deployment in the workspace you are pointing to. After deploying, you will see some stdout as the CLI builds and pushes images to your private registry. After a deploy, you can view your updated instance. Go to `app.[baseDomain]` to view a list of deployments and your workspace. 