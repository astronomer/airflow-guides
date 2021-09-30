---
title: "Managing Airflow Code"
description: "Guidelines for Working with Multiple Airflow Projects"
date: 2018-05-21T00:00:00.000Z
slug: "managing-airflow-code"
heroImagePath: "https://assets.astronomer.io/website/img/guides/SchedulingTasksinAirflow_preview.png"
tags: ["DAGs", "Best Practices", "Basics"]
---

One of the tenets of Apache Airflow that pipelines are defined as code. This allows you to treat your pipelines as you would any other piece of software and make use of best practices like version control and CI/CD. As you scale the use of Airflow within your organization, it becomes important to manage your Airflow code in a way that is organized and sustainable.

In this guide, we'll cover how to organize your Airflow projects, when to separate out your DAGs into multiple projects, how to manage code that is used across different projects, and what a typical development flow might look like.

Note that throughout this guide, we use the term "project" to denote any set of DAGs and supporting files that are deployed to a single Airflow "deployment" (an instance of Airflow). For example, your organization might have a finance team and a data science team each with their own separate Airflow deployment, and they would each have a separate Airflow project that contained all of their code.

## Project Structure

When working with Airflow, it is helpful to have a consistent project structure. This keeps all DAGs and supporting code organized and easy to understand, and it makes it easier to scale Airflow horizontally within your organization. 

The ideal setup is to keep one directory and repository per project. This means that you can use a version control tool (e.g. Github, Bitbucket) to package everything together. 

At Astronomer, we use the following project structure (note that this example assumes you are running Airflow using Docker):

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

The most common setup for Airflow projects is to keep all code for a given deployment in the same repository. However, there are some circumstances where it makes sense to separate DAGs into multiple projects. In these scenarios, it's best practice to have a separate Airflow deployment for each project. You might implement this project structure for the following reasons:

- Controlling access: RBAC should be managed at the Airflow deployment level rather than at the DAG level. If Team A and Team B should only have access to their own team's DAGs, it would make sense to split them up into two projects/ deployments.
- Infrastructure considerations: For example, if you have a set of DAGs that are well suited to the Kubernetes executor and another set that are well suited to the Celery executor, you may wish to break them up into two different projects that feed Airflow deployments with different infrastructure (note the [Astronomer platform](https://www.astronomer.io/docs/cloud/stable/deploy/configure-deployment) makes this trivial to set up).
- Dependency management: If DAGs have conflicting Python or OS dependencies, one way of managing this can be breaking them up into separate projects so they are isolated from one another.

Occasionally, some use cases require DAGs from multiple projects to be deployed to the _same_ Airflow deployment. This is a less common pattern and is not recommended for project organization unless it is specifically required. In this case, deploying the files from different repositories together into one Airflow deployment should be managed by your CI/CD tool. Note that if you are implementing this use case on Astronomer, you will need to use the [NFS deployment method](https://www.astronomer.io/docs/enterprise/v0.25/deploy/deploy-nfs).  

## Reusing Code

Any code that is reused between projects (e.g. custom hooks or operators, DAG templates, etc.) should live in a repository that's separate from your individual project repositories. This ensures that any changes to the re-used code (e.g. updates to a custom operator) only need to be made once and apply across all projects where that code is used.

You can then pull in code from that separate repository into one of your Airflow projects. If you are working with Astronomer, check out our documentation on [building from a private repository](https://www.astronomer.io/docs/enterprise/v0.25/develop/customize-image#build-from-a-private-repository). Depending on your repository setup, it may also be possible to manage this with your CI/CD tool.

## Development Flow

You can extend the project structure described above to work for developing DAGs and promoting code through `dev`, `QA`, and `production` environments. The most common method for managing code promotion with this project structure is to use branching. You still maintain one project/repository, and create `dev` and `qa` branches for any code in development or testing. Your `main` branch should correspond to code that is deployed to production. You can then use your CI/CD tool to manage promotion between these three branches. For more on this, check out Astronomer's docs on [implementing CI/CD](https://www.astronomer.io/docs/enterprise/v0.25/deploy/ci-cd).

Note that there are many ways of implementing a development flow for your Airflow code. For example, you may work with feature branches instead of a specific `dev` branch. How you choose to implement this will depend on the needs of your team, but the method described here is a good place to start if you aren't currently using CI/CD with Airflow.
