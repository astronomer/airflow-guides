---
title: "Managing Airflow Code"
description: "Guidelines for Working with Multiple Airflow Projects"
date: 2018-05-21T00:00:00.000Z
slug: "managing-airflow-code"
heroImagePath: "https://assets.astronomer.io/website/img/guides/SchedulingTasksinAirflow_preview.png"
tags: ["DAGs", "Best Practices", "Basics"]
---

One of the tenets of Apache Airflow is that your pipelines are defined as code. This allows you to treat your pipelines as you would any other piece of software and make use of best practices like version control and CI/CD. Especially as you scale the use of Airflow within your organization, it becomes incredibly important to manage your Airflow code in a way that is organized and sustainable.

In this guide, we'll cover a recommended project structure to keep your Airflow projects organized, when to separate out your DAGs into multiple projects, how to manage code that is used across different projects, and what a typical development flow might look like.

Note that throughout this guide, we use the term "project" to denote any set of DAGs and supporting files that will be deployed to the same Airflow instance. For example, your organization might have a finance team and a data science team each with their own separate Airflow deployment, and they would each have a separate Airflow project that contained all of their code.

## Project Structure

When working with Airflow it is helpful to have a consistent project structure. This keeps all DAGs and supporting code organized and easy to understand, and makes it easier to scale Airflow horizontally within your organization. 

Ideally you keep one directory and repository per project, and your version control tool (e.g. Github, Bitbucket) packages everything needed to run a set of DAGs together. Note that this example assumes you are running Airflow using Docker.

At Astronomer, we use the following project structure:

```bash
.
├── dags                        # Folder where all your DAGs go
│   ├── example-dag.py
│   ├── redshift_transforms.py
├── Dockerfile                  # For Astronomer's Docker image and runtime overrides
├── include                     # For any scripts that your DAGs might need to access
│   └── sql
│       └── transforms.sql
├── packages.txt                # For OS-level packages
├── plugins                     # For any custom or community Airflow plugins
│   └── example-plugin.py
└── requirements.txt            # For any Python packages
```

To create a project with this structure automatically, you can install the [Astronomer CLI](https://www.astronomer.io/docs/enterprise/v0.25/develop/cli-quickstart#step-3-initialize-an-airflow-project) and initialize a project with `astro dev init`.

If you are not running Airflow with Docker or have different requirements for your organization, your project structure may look slightly different. The most important part is choosing a structure that works for your team and keeping it consistent so that anyone working with Airflow can easily transition between projects without having to re-learn a new structure.


## When to Separate Projects

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

## Development Flow


