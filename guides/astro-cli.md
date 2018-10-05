---
title: "The Astronomer CLI"
description: "Get your DAGs to run locally"
date: 2018-07-17T00:00:00.000Z
slug: "astro-cli"
heroImagePath: null
tags: ["admin-docs", "cli-docs", "debugging"]
---

The Astronomer CLI provides a local, dockerized version of Apache Airflow to
write your DAGs. It is an easy way to use Apache  Airflow on your local
machine even if you are not using Astronomer.

## Getting Started

To install, you'll need Docker and Go on your machine.

Follow the guide found here to install and learn the files that are generated:
https://github.com/astronomerio/astro-cli

If you are on Windows, check out our Windows guide:
https://www.astronomer.io/guides/install-cli-windows10-wsl/

Once you are installed, open a terminal and run `astro`.

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

## Building your image.
Once you've run `astro airflow init` and start developing your DAGs, you can
run `astro airflow start` to build your image.

- This will build a base image using Alpine Linux and from Astronomer's fork of Apache-Airflow.
- The build process will include [everything in your project directory](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/onbuild/Dockerfile#L32). This makes it easy to include any shell scripts, static files, or anything else you want to include in your code.

## Finding the right dependencies
If your image fails to build after running `astro airflow start`, usually indicated by an error message in your console or airflow not being accessible on `localhost:8080/admin`,  it is probably due to missing OS-level packages in `packages.txt` needed for any python packages specified in `requirements.txt`.

Check out these examples for an idea of what `packages` and `requirements` are needed for simple use cases:
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

**Note**: The image will take some time to build the first time. Right now, you have to rebuild the image each time you want to add an additional package or requirement.




## Debugging

By default, there won't be webserver or scheduler logs in the terminal since everything is hidden away in Docker containers. You can see these logs by running:

```
docker logs $(docker ps | grep scheduler | awk '{print $1}')

```

(You can switch out scheduler for webserver if you are more interested in those).

## Using Airflow CLI Commands
You can still use all native Airflow CLI commands with the astro cli when developing DAGs locally, they just need to be wrapped around docker commands.

Run `docker ps` after your image has been built to see a list of containers running. You should see one for the scheduler, webserver, and Postgres. 

For example, a connection can be added with:
```bash
docker exec -it SCHEDULER_CONTAINER bash -c "airflow connections -a --conn_id test_three  --conn_type ' ' --conn_login etl --conn_password pw --conn_extra {"account":"blah"}"
```

Refer to the native [airflow cli](https://airflow.apache.org/cli.html) for a list of all commands. 

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

**Note:** Be sure configurations are names match up with the version of Airflow used.

## Deploying to Astronomer EE

**Note:** If you're looking for steps on how to deploy to your Astronomer Cloud account, check out our [Getting Started with Cloud](https://www.astronomer.io/guides/getting-started-with-new-cloud/) guide.

You have created and tested your Airflow DAG locally via the [astro-cli](https://github.com/astronomerio/astro-cli). Now, we'll walk through how to deploy the DAG to your Astronomer EE cluster.

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

