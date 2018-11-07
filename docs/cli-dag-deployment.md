---
title: "DAG Deployment"
description: "How to deploy your DAGs to your Airflow cluster using the Astronomer CLI."
date: 2018-10-12T00:00:00.000Z
slug: "cli-dag-deployment"
menu: ["Astro CLI"]
position: [3]
---

# Deploying to Astronomer Enterprise

If you've created and tested your Airflow DAG locally via the [astro-cli](https://github.com/astronomerio/astro-cli), you're ready to deploy that DAG to your Astronomer EE cluster.

(**Note:** If you're looking for steps on how to deploy to your Astronomer Cloud account, check out our [Getting Started with Cloud](https://www.astronomer.io/guides/getting-started-with-new-cloud/) guide).

## Authenticating With Your Registry

#### 1) Configure the location of your Private Docker Registry

The first setting we need to configure is the location of your private Docker registry. 

This houses all Docker images pushed to your Astronomer EE deploy. By default, it's located at `registry.[baseDomain]`. 

- If you're not sure which domain you deployed Astronomer EE to, you can refer back to the `baseDomain` in your [`config.yaml`](http://enterprise.astronomer.io/guides/google-cloud/index.html#configuration-file).

#### 2) Authenticate

Run the following command from your project root directory:

```bash
astro auth login [baseDomain]
```

*Note:* Depending on the type of authentication you're using, the process will be a little different. If you are using the default Google OAuth, leave the Username field blank and continue follow the instructions on the terminal.

#### 3) List your Workspaces

Run `astro workspace list` to see a list of all the workspaces you have access to. 

To switch between workspaces, run: `astro workspace switch [UUID]`

## DAG Deployment

Now that you've configured the astro-cli to point at your Astronomer EE deployment, you're ready to push your first DAG. 

#### 1. Find your Release Name

To push your DAG, you'll need the release name of your Astronomer EE deployment. A few notes:

- This release name was created by the Helm package manager during your Astronomer EE deploy

- If you are unsure of what release
name was created for your deploy, you can run `helm ls` to get a list of all Helm releases and find the one that has an "Updated" timestamp corresponding to the time at which you deployed Astronomer EE. 

- If you're still not sure which Helm release you should deploy to, reach out to your cluster Administrator.

#### 2. Run our deploy command

```bash
astro airflow deploy [release-name]
```

If you do NOT include a release name, you will be prompted to choose from a deployment in the workspace you are pointing to. 

After deploying, you'll see some stdout as the CLI builds and pushes images to your private registry. 

### Check your Instance

After a deploy, you should see your updated instance.

If you're running our Enterprise Edition, go to `app.[baseDomain]` to view your list of deployments and workspace. 

If you're running our Cloud Edition, go to: https://app.astronomer.cloud/deployments