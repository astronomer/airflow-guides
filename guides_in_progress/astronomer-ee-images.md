---
layout: page
title: Astronomer EE Images
permalink: /guides/astronomer-ee-images/
hide: true
---

# Objective

This guide will give you an overview of the Astronomer Platform Docker images with a focus on customizing your Airflow images to your specific needs.

## Astronomer Images

We have opened up our platform and made all of the [Astronomer images](https://github.com/astronomerio/astronomer/tree/master/docker/platform) available to the community. This has the advantage of being highly transparent and customizable for our users.

First, this guide details the three key Docker image layers and then goes on to explain how you can begin customizing these images to best suit your needs.

### ap-base

There are three layers to our images. The [ap-base](https://github.com/astronomerio/astronomer/blob/master/docker/platform/base/Dockerfile) is built upon [Alpine 3.7](https://github.com/gliderlabs/docker-alpine/blob/61c3181ad3127c5bedd098271ac05f49119c9915/versions/library-3.7/x86_64/Dockerfile). This base layer has a small footprint and is the foundation for all other images.

### ap-airflow

The next layer is different depending on which piece of the platform we are discussing. Because this guide focuses on the ability to customize your Airflow image, we will only be discussing the __specifics__ of the Airflow related Dockerfiles.

The [airflow-base](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/Dockerfile) image contains the specifics of the standard Astronomer Enterprise Airflow installation. At a high-level it handles the installation of a lightweight Airflow installation anchored to a specific Airflow version (defined by `ARG VERSION`). It should also be noted that it is tied to the Astronomer soft-fork of Airflow (defined by `ENV AIRFLOW_REPOSITORY`).

### on-build

With a standard project directory created by the [astro-cli](https://github.com/astronomerio/astro-cli) (via the `astro airflow init` command) a `Dockerfile` is created with the default image setting of

```docker
FROM astronomerinc/ap-airflow:latest-onbuild
```

The [on-build](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/onbuild/Dockerfile) Docker image is a light wrapper around [ap-airflow](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/Dockerfile) with two notable features. There are two commands in the `Dockerfile` which tell Docker to ingest any Alpine OS level and Python level dependencies you specify.

ie

```docker
ONBUILD RUN cat packages.txt | xargs apk add
ONBUILD RUN pip install --no-cache-dir -q -r requirements.txt
```

## Customizing Your Images

It is important that a user is able to customize their Airflow instance as needed. There are several entry points for doing so depending on specific needs and familiarity with Docker. Here we will discuss these options in order of least difficult and least flexible to most difficult and most flexible.

### Customizing Basic Project Dependencies

Discussed briefly above, this is the easiest (and default) way to begin customizing your images to fit your needs. Inheriting from on-build allows a user to inject any combination of [apk packages](https://pkgs.alpinelinux.org/packages) or [python libs](https://pypi.org/search/). Doing so is as simple as modifying `packages.txt` and/or `requirements.txt` in your projects root directory.

For example, let's suppose you have a DAG which [curls](https://pkgs.alpinelinux.org/packages?name=curl&branch=edge) `.csv`'s from an SFTP server, extracts the data using [pandas](https://pypi.org/project/pandas/), builds a ML model using [scipy](https://pypi.org/project/scipy/) and finally loads the results to [postgresql](https://pypi.org/project/psycopg2/), you may have dependency files that look like this

`packages.txt` containing Alpine apk dependencies

```bash
curl
```

`requirements.txt` containing Python pip dependencies

```python
pandas==0.23.0
scipy==1.1.0
psycopg2==2.7.4
```

### Customizing Your Dockerfile

A user may require fine-grained control that can not be provided by modifying dependency files alone. This could include wanting to modify an ENV which maps to an [Airflow config value](https://airflow.incubator.apache.org/configuration.html#setting-configuration-options). A user who finds themselves in this situation can modify the `Dockerfile` in their project root directory.

### Custom Base Images

There may be some circumstances that require you to build your own images entirely from scratch. Most users deciding to go this route have an advanced use case and will have a very specific reason for needing to do so. At a high-level this could occur when there are corporate level restrictions on which OS and OS level packages that an organization has whitelisted for development.

The Astronomer Platform does not require that a user use our base images at all. You are free to use our images at a template to build your custom requirements from scratch. We only require that your image runs Airflows and creates `${AIRFLOW_HOME}/logs` for mounting log volumes.

If you have any questions, or just want to discuss customizing your Astronomer EE images, reach out to humans@astronomer.io.
