---
title: "Getting started with Astronomer"
date: 2018-10-12T00:00:00.000Z
slug: "getting-started"
menu: ["root"]
position: [2]
---

This is your guide to Astronomer Cloud Edition. Whether you're at a Proof-of-Concept stage or are a well-versed Apache Airflow user itching to implement our managed solution, you're in the right place.

## Sign up for Astronomer

The first step is to create a workspace on our platform.

- If this is your first time on Astronomer, make sure you're signed up here: https://app.astronomer.cloud/ (_Note_: If you get an error the first time you click that link, try a refresh).

- You'll be able to create a workspace (*think: team*), and go straight to the CLI Install from there.

- If you're new to Astronomer but someone else on your team has an existing workspace you want to join, you still have to create your own account with a default workspace of your own.

- Once there, they can invite you as a user.

## Download the CLI

To download the CLI, you'll need the following installed on your machine:

- [Docker](https://www.docker.com/get-started)
- [Go](https://golang.org/)

### CLI Version Control 

If you're ready to install our CLI, you're most likely looking for our latest version. If for any reason you need to run an earlier version, you can find the command below.

#### Latest Version 

To download the latest version of our CLI, run the following command:

Via `curl`:
  ```
   curl -sSL https://install.astronomer.io | sudo bash
   ```

#### Previous Version 

If you'd like to install a previous version of our CLI, the following command should do the trick:

Via `curl`:
   ```
    curl -sSL https://install.astronomer.io | sudo bash -s -- [TAGNAME]
   ```

### Confirm CLI Install

To confirm the install worked, do two things:

1. **Run the following**:

```bash
astro
```

2. **Create a project**:

```bash
mkdir hello-astro && cd hello-astro
astro airflow init
```

### For WSL (Windows Subsystem for Linux) Users

- If you're running WSL, you might see the following error when trying to call `astro airflow start` on your newly created workspace.

```
Sending build context to Docker daemon  8.192kB
Step 1/1 : FROM astronomerinc/ap-airflow:latest-onbuild
# Executing 5 build triggers
 ---> Using cache
 ---> Using cache
 ---> Using cache
 ---> Using cache
 ---> Using cache
 ---> f28abf18b331
Successfully built f28abf18b331
Successfully tagged hello-astro/airflow:latest
INFO[0000] [0/3] [postgres]: Starting
Pulling postgres (postgres:10.1-alpine)...
panic: runtime error: index out of range
goroutine 52 [running]:
github.com/astronomerio/astro-cli/vendor/github.com/Nvveen/Gotty.readTermInfo(0xc4202e0760, 0x1e, 0x0, 0x0, 0x0)
....
```

This is an issue pulling Postgres. To fix it, you should be able to run the following:

```
Docker pull postgres:10.1-alpine
```

## Get started with the new CLI

For a breakdown of subcommands and corresponding descriptions, you can run: `$ astro help`

When you're ready, run the following in a project directory: `astro airflow init`

This will generate some skeleton files:

```py
.
├── dags #Where your DAGs go
│   ├── example-dag.py
├── Dockerfile #For runtime overrides
├── include #For any other files you'd like to include
├── packages.txt #For OS-level packages
├── plugins #For any custom or community Airflow plugins
└── requirements.txt #For any python packages
```

For more specific guidance on working with our CLI, go [here](https://github.com/astronomerio/airflow-guides/blob/master/guides/astro-cli.md) or [here](https://github.com/astronomerio/astro-cli/blob/master/README.md).

## Customizing your image

Our base image runs Alpine Linux, so it is very slim by default.

- Add DAGs in the `dags` directory,
- Add custom airflow plugins in the `plugins` directory
- Python packages can go in `requirements.txt`. By default, you get all the python packages required to run airflow.
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

- Astronomer Cloud runs Python 3.6.6. If you're running a different version, don't sweat it. Our CLI spins up a containerized environment, so you don't need to change anything on your machine if you don't want to.

- Old Cloud Edition runs Airflow 1.9. Refer to the Airflow [updating guide](https://github.com/apache/incubator-airflow/blob/master/UPDATING.md#airflow-19) for differences between 1.8 and 1.9

- For the sake of not over-exposing data and credentials, there's no current functionality that allows you to automatically port over connections and variables from a prior Apache Airflow instance. You'll have to do this manually as you complete the migration.

- The Airflow UI doesn't always show the full stacktrace. To get some more information while you're developing locally, you can run:

```bash
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

We're excited about Airflow 1.10, and we have it slated to go live in Astronomer v0.9 (check out our roadmap [here](https://www.astronomer.io/guides/astronomer-roadmap/)).

To be notified, sign up for our mailing list (for now, you can find it at the footer on our [blog](https://www.astronomer.io/blog/)).

### What are the specs of the workers?

Astronomer v0.7.0 (coming out soon!) will allow you to adjust these directly in the UI, but the default for workers is: `1GB RAM, .5 CPU`

To put in a request to change them for your use case in the meantime, reach out to paola@astronomer.io. 

### Can we SSO with Google or will I need to setup and maintain a list of users?

You can use Google right out of the box for auth. The only list of users you'll need to maintain is the users who have access to a workspace (or a set of Airflow instances).

### What part of the authorization process ties my deployment to my org?

The first time you authenticated (via our UI or directly through our CLI), you had to have created an initial workspace. Once that happened, you were associated to your organization.

If you set up an additional workspace, you'll effectively have to specify that you're "pointing" at it.

By default, you're authenticated against the last workspace you deployed to.

### How do I get rid of any `example_dag`'s that initially show up in my deployment's DAG list?

For now, this is unfortunately something someone on the Astronomer team has to do directly. If you'd like us to remove any `example_dag`'s, let us know and we'll be quick to remove them.

Airflow 1.10's functionality actually does allow users to do this directly, so you can expect to be able to do so in the future. Stay peeled!

### Can I have a NAT or single IP for each deployment?

Not at the moment.

### How is SSL handled?
We handle ssl termination at the ssl layer, and the proxy request back to the SSL server is HTTP - so you don't need to do any SSL stuff from your end!

You might be wondering whether or not we're able to dedicate an Internet gateway / NAT to your org and pin it to your Kubernetes workers so that other customers aren’t able to send traffic to you.

In cloud, we run a single NAT that all internet bound traffic flows through, but unfortunately not at a customer level. We pretty much run solely at the Kubernetes layer, and Kubernetes doesn't have a NAT resource of any nature. For now, this is something you'll have to run in your own cloud.

We're increasingly getting this request and are looking into solutions, so if you'd like to dive into this deeper with our engineers shoot us an email at support@astronomer.io
