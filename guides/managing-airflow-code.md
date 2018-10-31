---
title: "Managing Airflow Code"
description: "Guidelines for Working with multiple Airflow Projects"
date: 2018-05-21T00:00:00.000Z
slug: "managing-airflow-code"
heroImagePath: "https://assets.astronomer.io/website/img/guides/SchedulingTasksinAirflow_preview.png"
tags: ["Environments", "Managing", "Airflow"]
---

Astronomer makes it easy to spin up multiple Apache Airflow environments. However, as Airflow use scales up within your org, you might need new ways to manage the codebase.

Before you jump into this guide, make sure you are familiar with our [app's UI](https://www.astronomer.io/guides/app-ui/)

## One Directory per Project

The ideal set up is to keep one directory per project. This way your version control tool (e.g. Github, Gitlab) packages everything needed to run a set of workflows together (apart from credentials).

This could look like:

```bash
.
├── dags
│   ├── example-dag.py
│   ├── redshift_transforms.py
│   └── sql
│       └── transforms.sql
├── Dockerfile
├── include
├── packages.txt
├── plugins
│   └── example-plugin.py
└── requirements.txt
```

Depending on the use-case, it might be smart to have 2 deployments for each project, a dev and a prod, with each branch on your version control tool tied to a different registry (you can automate by integrating Astronomer with your [CI/CD](https://www.astronomer.io/guides/deploying-dags-with-cicd/) tool).


## Separate Projects.

If a certain set of DAGs can't live in the same directory, they should live in separate directories.

```bash
└── customer_workflows
    ├── customer_one
    │   ├── dags
    │   │   └── aws_workflows.py
    │   ├── Dockerfile
    │   ├── include
    │   ├── packages.txt
    │   ├── plugins
    │   │   └── example-plugin.py
    │   └── requirements.txt
    └── customer_two
        ├── dags
        │   └── snowflake_workflows.py
        ├── Dockerfile
        ├── include
        ├── packages.txt
        ├── plugins
        │   └── example-plugin.py
        └── requirements.txt
```

In this structure, `astro airflow start` can be called from either the `customer_one` or `customer_two` repository, with both of them spinning up a different local environment. Code from both of these repositories should also be deployed to separate Airflow deployments, each of which will store credentials and DAG history separately (each Airflow instance gets a separate Postgresdb on Astronomer).

If different user groups are required both of these projects, it may make sense to put each one in a different workspace.

## Reusing Code

All code that is re-used between projects (e.g. plugins, DAG templates, etc) should live in separate directories in your version control tool (e.g. Astronomer houses all airflow plugins in [our airflow plugins repo](https://github.com/airflow-plugins/) ). This way, changes made outside of the project can be easily roped in, while changes specific to the project (e.g. changes to a plugin, or a specific dag template) are always housed with the project.
