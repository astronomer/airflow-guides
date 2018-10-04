---
title: "Getting Started with Astronomer Cloud"
description: "Your guide to Astronomer Cloud Edition"
date: 2018-08-01T00:00:00.000Z
slug: "getting-started-with-new-cloud"
heroImagePath: null
tags: ["Astronomer Platform", "admin-docs", "Cloud"]
---

This is your guide to Astronomer Cloud Edition. Whether you're at a Proof-of-Concept stage or are a well-versed Apache Airflow user itching to implement our managed solution, you're in the right place.

## Sign up for Astronomer

The first step is to create a workspace on our platform.

- If this is your first time on Astronomer, make sure you're signed up here: https://app.astronomer.cloud/ (_Note_: If you get an error the first time you click that link, try a refresh).

- You'll be able to create a workspace (*think: team*), and go straight to the CLI Install from there.

- If you're new to Astronomer but someone else on your team has an existing workspace you want to join, you still have to create your own account with a default workspace of your own.

- Once there, they can invite you as a user. 

## Download the CLI

To download the CLI, run the following command:

```
curl -sL https://install.astronomer.io | sudo bash -s -- v0.5.1
```

To confirm the install worked, do two things:

1. **Run the following**:

```
$astro
```

2. **Create a project**:

```
$ mkdir hello-astro && cd hello-astro
$ astro airflow init
```

_Note_: To install the CLI, you'll need to have both Docker and GO on your machine.

## Get started with the new CLI

For a breakdown of subcommands and corresponding descriptions, you can run: `$ astro help`


When you're ready, run the following in a project directory: `astro airflow init`

This will generate some skeleton files:

```
.
├── dags
│   └── example-dag.py
├── Dockerfile
├── include
├── packages.txt
├── plugins
└── requirements.txt
```

For more specific guidance on working with our CLI, go [here](https://github.com/astronomerio/airflow-guides/blob/master/guides/astro-cli.md) or [here](https://github.com/astronomerio/astro-cli/blob/master/README.md).

## Customizing your image

Our base image runs Alpine Linux, so it is very slim by default.

- Add DAGs in the `dags` directory,
- Add custom airflow plugins in the `plugins` directory
- Python packages can go in `requirements.txt`
- OS level packages  can go in `packages.txt` 
- Any envrionment variable overrides can go in `Dockerfile`

If you are unfamiliar with Alpine Linux, look here for some examples of what
you will need to add based on your use-case:

- [GCP](https://github.com/astronomerio/airflow-guides/tree/master/example_code/gcp/example_code)
- [Snowflake](https://github.com/astronomerio/airflow-guides/tree/master/example_code/snowflake/example_code)
- More coming soon!

## Run Apache Airflow Locally

Once you've added everything you need, run: `astro airflow start`

This will spin up a local Airflow for you to develop on that includes locally running docker containers - one for the Airflow Scheduler, one for the Webserver, and one for postgres (Airflow's underlying database).

To verify that you're set, you can run: `docker ps`

## Migrate your DAGs

If you're a previous user of Astronomer Cloud or have a pre-existing Airflow instance, migrating your DAGs should be straightforward. 

__Tips & Gotchas:__

- Astronomer Cloud runs Python 3.6.3. If you're running a different version, don't sweat it. Our CLI spins up a containerized environment, so you don't need to change anything on your machine if you don't want to.

- Old Cloud Edition runs Airflow 1.9. Refer to the Airflow [updating guide](https://github.com/apache/incubator-airflow/blob/master/UPDATING.md#airflow-19) for differences between 1.8 and 1.9

- For the sake of not over-exposing data and credentials, there's no current functionality that allows you to automatically port over connections and variables from a prior Apache Airflow instance. You'll have to do this manually as you complete the migration.

- The Airflow UI doesn't always show the full stacktrace. To get some more information while you're developing locally, you can run:

```
bash
docker logs $(docker ps | grep scheduler | awk '{print $1}')
```
- Before you deploy a new DAG, verify that everything runs as expected locally.

- As you add DAGs to your new project's `dags` directory, check the UI for any error messages that come up.


## DAG Deployment

Once you can get your DAGs working locally, you are ready to deploy them.

### **Step 1: CLI Login + Auth**

To log in and pass our authorization flow via the CLI, you'll have to run the following command:

  ```
  astro auth login astronomer.cloud
  ```

  Two notes: 

  1. If you don't already have an account on our platform, running this command will automatically create one for you (and a default workspace as well) based on the name associated with your Google email address.

  2. You _can_ login via app.cloud.astronomer directly but our UI currently does not display the workspace ID you'll need to complete a deployment.


### **Step 2: Pull your list of workspaces**

In order to deploy, you'll first need to verify your default workspace by pulling a list of all workspaces associated with your account.

To do so, run:

  `astro workspace list`

### **Step 3: Create a new deployment**
  
  If you're a new user, you can create a new deployment by running:

  `astro deployment create <deployment name>`

### **Step 4: View Deployments**
  
  Once you've run your first deploy and you've made sure you're in the right workspace, all you'll have to do moving forward is list your active deployments by running:

  `astro deployment list`

  This commnand will return a list of Airflow instances you're authorized to deploy to. 
  
### **Step 5: Deploy!**

When you're ready to deploy, run:

  `astro airflow deploy`

This command will return a list of deployments available in that workspace, and prompt you to pick one. 

## Frequently Asked Questions

### How do I know when there's a new version of the CLI I have to download?

We're constantly building more functionality to our CLI and will shoot you an email for major releases (think 0.5.0 to 0.6.0). 

We don't have an automated way to do so for minor relases, so we'd recommend running `astro version` on a bi-weekly basis to see what the latest is just in case.

If you do happen to be behind, you can run `astro upgrade` or the curl command listed above to install the latest.

### When will Astronomer run Airflow 1.10?

We're excited about Airflow 1.10, but we don't consider it stable enough just yet for us to adopt it.

In the meantime, we're keeping a close eye on the master branch of the project, and will let you know when we're ready to move towards it.

### What are the specs of the workers?

Our team may be able to change these one way or the other depending on your use case, but the default is: `1GB RAM, 1.5 CPU`

### Can we SSO with Google or will I need to setup and maintain a list of users?

You can use Google right out of the box for auth. The only list of users you'll need to maintain is the users who have access to a workspace (or a set of Airflow instances).

### What part of the authorization process ties my deployment to my org?

The first time you authenticated (via our UI or directly through our CLI), you had to have created an initial workspace. Once that happened, you were associated to your organization.

If you set up an additional workspace, you'll effectively have to specify that you're "pointing" at it. 

By default, you're authenticated against the last workspace you deployed to. 

### Can I have a NAT or single IP for each deployment?

You might be wondering whether or not we're able to dedicate an Internet gateway / NAT to your org and pin it to your Kubernetes workers so that other customers aren’t able to send traffic to you.

In cloud, we run a single NAT that all internet bound traffic flows through, but unfortunately not at a customer level. We pretty much run solely at the Kubernetes layer, and Kubernetes doesn't have a NAT resource of any nature. For now, this is something you'll have to run in your own cloud.

We're increasingly getting this request and are looking into solutions, so if you'd like to dive into this deeper with our engineers shoot us an email at support@astronomer.io
