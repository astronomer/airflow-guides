---
title: "Astronomer Docker Images"
description: "How Airflow differs from Oozie."
date: 2018-10-12T00:00:00.000Z
slug: "astronomer-docker-images"
tags: ["Docker"]
---

## Overview

You can use our Docker images however you'd like (subject to standard Apache 2.0
restrictions).

You may also be interested to look at
[Astronomer Enterprise Edition](https://www.astronomer.io/enterprise) which
makes it easy to deploy Apache Airflow clusters and Airflow DAGs
in a multi-team, multi-user environment via Kubernetes.

## Requirements

The only requirement to get up and running is Docker Engine
and Docker Compose. If you don't have these installed already,
visit these links for more information.

* [Docker Engine](https://docs.docker.com/engine/installation/)
* [Docker Compose](https://docs.docker.com/compose/install/)

## Quickstart

To get up and running quickly, we have provided a several
docker-compose files for quickly spinning up different
components of the platform. Simply `cd` into
`examples/${component}` and run `docker-compose up`. Some
directories will have additional scripts to wrap some useful
functionality around `docker-compose up`. These are documented on
their respective pages.

Running `docker-compose up` will download our prebuild images (see
Makefile for details) from our
[DockerHub Repository](https://hub.docker.com/u/astronomerinc/)
and spin up containers running the various platform systems.

## Building the Images

All platform images are built from a minimal
[Alpine Linux](https://alpinelinux.org/) base image to keep our
footprint minimal and secure.

To build the images from scratch run `make build` in your
terminal. If you've already downloaded the images from DockerHub,
this will replace them. These images will be used when running the
platform locally.

## Building the Documentation

Documentation is built on Jekyll and hosted on Google Cloud Storage.

Build the docs site locally:

```
cd docs
bundle install
```

Run it:

```
bundle exec jekyll serve
```

## Architecture

The Astronomer Airflow module consists of seven components, and you must bring
your own Postgres and Redis database, as well as a container deployment strategy
for your cloud.

![Airflow Module]({{ "/assets/img/airflow_module.png" | absolute_url }})

## Quickstart

Clone Astronomer Open:

```
git clone https://github.com/astronomerio/astronomer.git
cd astronomer
```

We provide two examples for Apache Airflow.  Each will spin up a handful of containers to mimic a live Astronomer environment.

### Airflow Core vs Airflow Enterprise

Here's a comparison of the components included in the Airflow Core vs Airflow Enterprise examples:

{:.table.table-striped.table-bordered.table-hover}
| Component                 | Airflow Core | Airflow Enterprise |
|---------------------------|:------------:|:------------------:|
| Airflow scheduler         | x            | x                  |
| Airflow webserver         | x            | x                  |
| PostgreSQL                | x            | x                  |
| [Redis][redis]            |              | x                  |
| [Celery][celery]          |              | x                  |
| [Flower][flower]          |              | x                  |
| [Prometheus][prometheus]  |              | x                  |
| [Grafana][grafana]        |              | x                  |
| [StatsD exporter][statsd] |              | x                  |
| [cAdvisor][cadvisor]      |              | x                  |

[redis]: https://redis.io/
[celery]: http://www.celeryproject.org/
[flower]: http://flower.readthedocs.io/en/latest/
[grafana]: https://grafana.com
[prometheus]: https://prometheus.io
[cadvisor]: https://github.com/google/cadvisor
[statsd]: https://github.com/prometheus/statsd_exporter

### Airflow Core

To start the simple Airflow example:

```
cd examples/airflow-core
docker-compose up
```

### Airflow Enterprise

To start the more sophisticated Airflow example:

```
cd examples/airflow-enterprise
docker-compose up
```

Once everything is up and running, open a browser and visit <http://localhost:8080> for Airflow and <http://localhost:5555> for Celery.

Sweet! You're up and running with Apache Airflow and well on your way to
automating all your data pipelines! The following sections will help you get
started with your first pipelines, or get your existing pipelines running on
the Astronomer Platform.

## Start from Scratch

You need to write your first DAG. Review:

* [Core Airflow Concepts](https://docs.astronomer.io/v2/apache_airflow/tutorial/core-airflow-concepts.html)
* [Simple Sample DAG](https://docs.astronomer.io/v2/apache_airflow/tutorial/sample-dag.html)

We recommend managing your DAGs in a Git repo, but for the purposes of getting
rolling, just make a directory on your machine with a `dags` directory, and you
can copy the sample dag from the link above into the folder inside a file
`test_dag.py`. We typically advise first testing locally on your machine, before
pushing changes to your staging environment. Once fully tested you can deploy
to your production instance.

When ready to commit new source or destination hooks/operators, our best
practice is to commit these into separate repositories for each plugin.

## Start from Existing Code

If you already have an Airflow project (Airflow home directory), getting things
running on Astronomer is straightforward. Within `examples/airflow`, we provide
a `start` script that can wire up a few things to help you develop on Airflow
quickly.

You'll also notice a small `.env` file next to the `docker-compose.yml` file.
This file is automatically sourced by `docker-compose` and it's variables are
interpolated into the service definitions in the `docker-compose.yml` file. If
you run `docker-compose up`, like we did above, we mount volumes into your host
machine's `/tmp` directory for Postgres and Redis. This will automatically be
cleaned up for you.

This will also be the behavior if you run `./start` with no arguments. If you
want to load your own Airflow project into this system, just provide the
project's path as an argument to run, like this:
`./start ~/repos/airflow-project`.

Under the hood, a few things make this work. `Dockerfile.astro` and
`.dockerignore` files are written into your project directory. And an `.astro`
directory is created.

* `Dockerfile.astro` just links to a special `onbuild` version of our Airflow
  image that will automatically add certain files, within the `.astro` directory
  to the image.
* The `.astro` file will contain a `data` directory which will be used for
  mapping docker volumes into for Postgres and Redis. This lets you persist
  your current Airflow state between shutdowns. These files are automatically
  ignored by `git`.
* The `.astro` directory will also contain a `requirements.txt` file that you
  can add python packages to be installed using `pip`. We will automatically build
  and install them when the containers are restarted.
* In some cases, python modules will need to compile native modules and/or rely
  on other package that exist outside of the python ecosystem. In this case, we
  also provide a `packages.txt` file in the `.astro` directory, where you can add
  [Alpine packages](https://pkgs.alpinelinux.org/packages). The format is similar
  to `requirements.txt`, with a package on each line.

With this configuration, you can point the `./start` script at any Airflow home
directory and maintain distinct and separate environments for each, allowing you
to easily test different Airflow projects in isolation.
