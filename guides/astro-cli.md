---
title: "The Astronomer CLI"
description: "Get your DAGs to run locally"
date: 2018-07-17T00:00:00.000Z
slug: "astro-cli"
heroImagePath: null
tags: ["admin-docs", "cli-docs", "debugging"]
---

The Astronomer CLI provides a local and dockerized version of Apache Airflow to use while writing your DAGs. Even if you're not using Astronomer, our CLI is an easy way to use Apache Airflow on your local machine.

*Note*: This guide will walk you through the rest, but feel free to check out these supplementary guides below:

 - [Astro CLI README](https://github.com/astronomerio/astro-cli)
 - [Our Windows Guide](https://www.astronomer.io/guides/install-cli-windows10-wsl/) for WSL (Windows Subsystem for Linux)


## Pre-Requisites

To install the CLI, make sure you have the following on your machine:

- [Docker](https://www.docker.com/)
- [Go](https://golang.org/)

## Installing the CLI

To install the most recent version of our CLI on your machine, run the following command.

Via `curl`:
  ```
   curl -sSL https://install.astronomer.io | sudo bash
   ```

### Previous Versions

If you'd like to install a previous version of our CLI, the following command should do the trick.

Via `curl`:
   ```
    curl -sSL https://install.astronomer.io | sudo bash -s -- [TAGNAME]
   ```
   
For example:
   ```
curl -sSL https://install.astronomer.io | sudo bash -s -- v0.3.1
   ```


**Note:** If you get mkdir error while trying to run the install, download and run [godownloader](https://raw.githubusercontent.com/astronomerio/astro-cli/master/godownloader.sh) script locally. 

    $ cat godownloader.sh | bash -s -- -b /usr/local/bin

## Getting Started with the CLI

**1. Confirm the install worked.** 

To confirm it's successfully installed, open a terminal and run:

 ```
  $ astro
  ```

You should see something like this:

```
astro is a command line interface for working with the Astronomer Platform.

Usage:
  astro [command]

Available Commands:
  airflow     Manage airflow projects and deployments
  auth        Mangage astronomer identity
  cluster     Manage Astronomer EE clusters
  config      Manage astro project configurations
  deployment  Manage airflow deployments
  help        Help about any command
  upgrade     Check for newer version of Astronomer CLI
  user        Manage astronomer user
  version     Astronomer CLI version
  workspace   Manage Astronomer workspaces

Flags:
  -h, --help   help for astro
```

**2. Create a project:**

 ```
$ mkdir hello-astro && cd hello-astro
$ astro airflow init
 ```
    
This will generate a skeleton project directory:
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

**3. Start Airflow**

Once you've run `astro airflow init` and started developing your DAGs, you can run `astro airflow start` to build your image.

- This will build a base image using Alpine Linux and from Astronomer's fork of Apache-Airflow.

- The build process will include [everything in your project directory](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/onbuild/Dockerfile#L32). This makes it easy to include any shell scripts, static files, or anything else you want to include in your code.

### Debugging

Is your image failing to build after running `astro airflow start`?

 - You might be getting an error message in your console, or finding that Airflow is not accessible on `localhost:8080/admin`)
 - If so, you're likely missing OS-level packages in `packages.txt` that are needed for any python packages specified in `requirements.text`


Not sure what `packages` and `requirements` you need for your use case? Check out these examples.

- [Snowflake](https://github.com/astronomerio/airflow-guides/tree/master/example_code/snowflake)
- [Google Cloud](https://github.com/astronomerio/airflow-guides/tree/master/example_code/gcp)

If image size isn't a concern, feel free to "throw the kitchen sink at it" with this list of packages:

```
libc-dev
musl
libc6-compat
gcc
python3-dev
build-base
gfortran
freetype-dev
libpng-dev
openblas-dev
gfortran
build-base
g++
make
musl-dev
```

**Notes to consider**:
- The image will take some time to build the first time. Right now, you have to rebuild the image each time you want to add an additional package or requirement.
- By default, there won't be webserver or scheduler logs in the terminal since everything is hidden away in Docker containers. You can see these logs by running: `docker logs $(docker ps | grep scheduler | awk '{print $1}')`


### CLI Help

The CLI includes a help command and descriptions, as well as usage info for subcommands.

To see the help overview:

```
$ astro help
```

Or for subcommands:

```
$ astro airflow --help
```

```
$ astro airflow deploy --help
```

## Using Airflow CLI Commands

You can still use all native Airflow CLI commands with the Astro CLI when developing DAGs locally - but they'll need to be wrapped around docker commands. For a list of all commands, refer to the native [Airflow CLI](https://airflow.apache.org/cli.html).

To see a list of containers running, run:

```
 docker ps
 ```
 
 You should see a container for the scheduler, webserver, and Postgres. 

For example, a connection can be added with:
```bash
docker exec -it SCHEDULER_CONTAINER bash -c "airflow connections -a --conn_id test_three  --conn_type ' ' --conn_login etl --conn_password pw --conn_extra {"account":"blah"}"
```

**Note**: This will only work for the local dev environment. 

## Overriding Environment Variables

Future releases of the Astronomer CLI will have cleaner ways of overwriting environment variables. Until then, any overrides can go in the `Dockerfile`.

- Any bash scripts you want to run as `sudo` when the image builds can be added as such:
`RUN COMMAND_HERE`

- Airflow configuration variables found in [`airflow.cfg`](https://github.com/apache/incubator-airflow/blob/master/airflow/config_templates/default_airflow.cfg) can be overwritten with the following format:

```
 ENV AIRFLOW__SECTION__PARAMETER VALUE
```
For example, setting `max_active_runs` to 3 would look like:

```
AIRFLOW__CORE__MAX_ACTIVE_RUNS 3
```

These commands should go after the `FROM` line that pulls down the Airflow image.

**Note:** Be sure configuration names match up with the version of Airflow you're using.

## Deploying to Astronomer Enterprise

Once you've created and tested your Airflow DAG locally via the [astro-cli](https://github.com/astronomerio/astro-cli), you're ready to deploy that DAG to your Astronomer EE cluster.

(**Note:** If you're looking for steps on how to deploy to your Astronomer Cloud account, check out our [Getting Started with Cloud](https://www.astronomer.io/guides/getting-started-with-new-cloud/) guide).

### Authenticating With Your Registry

**1) Configure the location of your Private Docker Registry**

The first setting we need to configure is the location of your private Docker registry. 

This houses all Docker images pushed to your Astronomer EE deploy. By default, it's located at `registry.[baseDomain]`. 

- If you're not sure which domain you deployed Astronomer EE to, you can refer back to the `baseDomain` in your [`config.yaml`](http://enterprise.astronomer.io/guides/google-cloud/index.html#configuration-file).

### Authenticate

Run the following command from your project root directory:

```bash
astro auth login [baseDomain]
```

*Note:* Depending on the type of authentication you're using, the process will be a little different. If you are using the default Google OAuth, leave the Username field blank and continue follow the instructions on the terminal.

### List your Workspaces

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

