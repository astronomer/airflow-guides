---
title: "Get Started with Apache Airflow 2.0"
description: "Test Apache Airflow 2.0 on your local machine with the Astronomer CLI."
date: 2020-12-17T00:00:00.000Z
slug: "get-started-airflow-2"
heroImagePath: "https://assets2.astronomer.io/main/guides/getting-started-airflow-2.png"
tags: ["Resources", "Basics"]
---

[Apache Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0) is a momentous open-source release that many are eager to test and adopt.

If you'd like to test Airflow 2.0 on your local machine, Astronomer's [open-source CLI](https://github.com/astronomer/astro-cli) is the fastest and easiest way to do so.

Read below for guidelines.

> **Note:** If you're an Astronomer user looking to upgrade an Airflow Deployment on Astronomer to 2.0, refer to [Upgrade to Apache Airflow 2.0 on Astronomer](https://www.astronomer.io/docs/cloud/stable/customize-airflow/upgrade-to-airflow-2).

## Step 1: Install or Upgrade the Astronomer CLI

The [Astronomer CLI](https://github.com/astronomer/astro-cli) is the easiest way to run Apache Airflow on your machine. From the CLI, you can establish a local testing environment regardless of where you'll be deploying to from there.

There are two ways to install any version of the Astronomer CLI:

- cURL
- [Homebrew](https://brew.sh/)

> **Note:** If you already have the Astronomer CLI installed, make sure you're running `v0.23.2` or above. To check, run `$ astro version`.
>
> If you're running an earlier version, follow the install steps below to upgrade.

### Prerequisites

To use the Astronomer CLI, make sure you have [Docker](https://www.docker.com/) (v18.09 or higher) installed and running on your machine.

### Install or Upgrade the CLI via cURL

To install or upgrade to the latest version of the Astronomer CLI via cURL, run:

```bash
$ curl -ssl https://install.astronomer.io | sudo bash
```

> **Note:** If you're a macOS user using ZSH as your shell, you may encounter an error. [Learn more](https://forum.astronomer.io/t/astro-cli-install-error-on-mac-zsh/659).

### Install or Upgrade the CLI via Homebrew

To install or upgrade to the latest version of the Astronomer CLI via [Homebrew](https://brew.sh/), run:

```bash
$ brew install astronomer/tap/astro
```

For more information, refer to the [Astronomer CLI README](https://github.com/astronomer/astro-cli#latest-version).

## Step 2: Initialize an Airflow Project

First, create a new directory for your Airflow project and `cd` to it:

```
$ mkdir <directory-name> && cd <directory-name>
```

In the project directory, run:

```
$ astro dev init
```

This project directory is where you'll store all files necessary to build your Airflow 2.0.0 image. It will include a pre-populated Example DAG.

## Step 3: Add Airflow 2.0 to your Dockerfile

Your `Dockerfile` will include reference to a Debian-based, [Astronomer Certified](https://www.astronomer.io/downloads/) Docker Image.

In your Dockerfile, replace the existing FROM statement with:

```dockerfile
FROM quay.io/astronomer/ap-airflow:2.0.0-buster-onbuild
```

Feel free to refer to the [Astronomer Certified 2.0.0 image source](https://github.com/astronomer/ap-airflow/tree/master/2.0.0/buster).

## Step 4: Start Airflow

Now, run the following command:

```
$ astro dev start
```

This command spins up 3 Docker containers on your machine, 1 each for the Airflow Webserver, Scheduler, and Postgres components.

> **Note:** If you’re running the Astronomer CLI with the [buildkit](https://docs.docker.com/develop/develop-images/build_enhancements/) feature enabled in Docker, you may see an error (`buildkit not supported by daemon`). Check out [this forum post](https://forum.astronomer.io/t/buildkit-not-supported-by-daemon-error-command-docker-build-t-airflow-astro-bcb837-airflow-latest-failed-failed-to-execute-cmd-exit-status-1/857) for the suggested resolution.

## Step 5: Access the Airflow 2.0 UI

To check out the Airflow 2.0 UI:

1. Go to http://localhost:8080/
2. Log in with `admin` as both your username and password

The example DAG in your directory should be populated in the Airflow UI on your local machine.

With that, you're all set!

> **Note:** You will NOT be able to run multiple Airflow Scheduler replicas locally. If you’re interested in testing that feature, [reach out to us](https://astronomer.io/get-astronomer) and we’ll help you get set up with a docker-compose override file that you can test both locally and on Astronomer.

## Resources

Once you've tested Airflow 2.0 locally, refer to:

- Apache Airflow's [Upgrading to 2.0 Doc](https://airflow.apache.org/docs/apache-airflow/stable/upgrading-to-2)
- Apache Airflow's [Upgrade Check Script](
https://airflow.apache.org/docs/apache-airflow/stable/upgrade-check.html#upgrade-check)

The Apache Airflow Project strongly recommends that all users interested in running Airflow 2.0 first upgrade to [Airflow 1.10.14](https://github.com/apache/airflow/releases/tag/1.10.14), which was built to make the migration process as easy as possible.

If you find a bug or problem in Airflow, file a GitHub issue in the [Apache Airflow GitHub repo]((https://github.com/apache/airflow/issues)). We'll be working with open source contributors towards subsequent 2.0 releases and are committed to regularly triaging community-reported issues.