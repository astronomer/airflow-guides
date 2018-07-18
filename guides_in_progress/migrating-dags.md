---
layout: page
title: Migrating DAGs
permalink: /guides/migrating-dags/
hide: true
---



## Install Astronomer CLI

> Note: we currently have two CLIs called `astro`, one for our Cloud Edition and
this new CLI for Enterprise Edition. We're working to merge them, but for the
time being, the Enterprise CLI is called `astro-cli`. If you're not using our
Cloud Edition CLI, you can alias `astro-cli` to `astro`.
>
> See the README in <https://github.com/astronomerio/astro-cli> for complete
installation instructions.

## Choose some DAGs + verify they run locally

* Choose some DAGs, preferably simple ones to start,
  that you want to deploy to Astronomer Enterprise Edition.
* Start with fresh build - `astro airflow init` - make sure you know what’s in your installation
* Copy a real DAG into the folder
* Check Airflow UI, see if code loaded (it probably didn’t)
* Fix your DAG or Airflow environment
  * Add supporting code/connections/variables/pool
  * Maybe just want to copy over all your DAGs vs. going one-by-one because it can be tedious
  * Maybe you have some issues w/ Python 2 to Python 3
  * Plugins might be failing under the hood. Check webserver logs.
* Verify everything is running locally before deploying.

## Deploy to production

* Pause current production DAG wherever it's currently running
* Install Astronomer Enterprise on Kubernetes on Google Cloud Platform,
  [following this guide](https://enterprise.astronomer.io/guides/google-cloud/){:target="_blank"}.
