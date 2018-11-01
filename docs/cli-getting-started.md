---
title: "Getting started with the Astronomer CLI"
link: "Getting started"
date: 2018-10-12T00:00:00.000Z
slug: "cli-getting-started"
menu: ["Astro CLI"]
position: [2]
---

**1. Confirm the install worked. Open an terminal and run:**

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

Once you've run `astro airflow init` and start developing your DAGs, you can run `astro airflow start` to build your image.

- This will build a base image using Alpine Linux and from Astronomer's fork of Apache-Airflow.
- The build process will include [everything in your project directory](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/onbuild/Dockerfile#L32). This makes it easy to include any shell scripts, static files, or anything else you want to include in your code.

### Debugging

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

**Notes to consider**:
- The image will take some time to build the first time. Right now, you have to rebuild the image each time you want to add an additional package or requirement.
- By default, there won't be webserver or scheduler logs in the terminal since everything is hidden away in Docker containers. You can see these logs by running: `docker logs $(docker ps | grep scheduler | awk '{print $1}')`

### CLI Help

The CLI includes a help command, descriptions, as well as usage info for subcommands.

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
