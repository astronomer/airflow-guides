---
title: "Getting Started with Astronomer Cloud 2.0"
description: "Migrate over to our new cloud"
date: 2018-05-21T00:00:00.000Z
slug: "astronomer-cloud"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Astronomer Platform", "admin-docs", "Cloud"]
---

## Download the CLI

Download the new CLI here:
https://github.com/astronomerio/astro-cli

**Optional**

If you have the old CLI, you can alias the old CLI in your `.bashrc`.

Find the path to your cloud-cli binary. It usually looks like:
`~/.astro/astro/astro`

Open your `.bashrc` and add:

`alias astro-cld=PATH_TO_FILE/astro`

This will allow you to use the old CLI as `astro-cld`

## Get started with the new CLI

Run `astro airflow init` in a project directory. This will generate some skeleton files:

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

## Customizing your image
Our base image runs Alpine Linux, so it is very slim by default.


- Add DAGs in the `dags` directory,
- Add custom airflow plugins in the `plugins` directory
- Python packages and os-level packages in `requirements.txt` and `packages.txt`, respectively.
- Any envrionment variable overrides can go in `Dockerfile`

If you are unfaimiliar with Alpine Linux, look here for some examples of what
you will need to add based on your use-case:

- GCP
- Snowflake
- More coming soon!

Once you've added everything you need, runs

  `astro airflow start`

This will spin up a local Airflow for you to develop on.

## Migrate your DAGs

If you're a previous user of Astronomer Cloud or have a pre-existing Airflow instance, migrating your DAGs should be straight forward.

__Tips & Gotchas:__
- The old Astronomer Cloud ran on Python 3.4. New Cloud runs Python 3.6.3.
- Make sure your variables and connections made it over.
- Old Cloud was Airflow 1.8, while New Cloud is Airflow 1.9. Refer to the Airflow [updating guide](https://github.com/apache/incubator-airflow/blob/master/UPDATING.md#airflow-19) for differences between 1.8 and 1.9
- The Airflow UI doesn't always show the full stacktrace. To get some more errors when developing locally, you can run:

```
bash
docker logs $(docker ps | grep scheduler | awk '{print $1}')
```
Before you deploy a new DAG, verify that everything runs as expected locally.
As you add DAGs to your new project's `dags` directory, check the UI for any error messages that come up.


## DAG Deployment

Once you can get your DAGs working locally, you are ready to deploy them.

Run:

  `astro auth login -d cloud.astronomer.io`

Visit `app.cloud.astronomer.io` to view your workspace.

This will take you through the OAuth authorization flow. Once you are authorized, you can run:

  `astro deployment list`

This will show you the Airflow instances that you are currently authorized to deploy to.

When you are ready to deploy, run:

  `astro airflow deploy`

and deploy to your deployment of choice.
