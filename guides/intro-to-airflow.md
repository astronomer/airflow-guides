---
title: "Introduction to Apache Airflow"
description: "Everything you need to know to get started with Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "intro-to-airflow"
heroImagePath: null
tags: ["Basics", "Start"]
---

[Apache Airflow](https://airflow.apache.org/) is a tool for programmatically authoring, scheduling, and monitoring data pipelines. It is the de facto standard for programmatic data orchestration. Airflow is freely available as open source software, and has over 9 million downloads per month as well as a vibrant OSS community.

Data practitioners choose Airflow because it allows them to define their data pipelines as Python code in a highly extensible and infinitely scalable way. Airflow can integrate with virtually any other tool, and acts as the glue that holds your data ecosystem together.

This guide offers an introduction to Apache Airflow and its core concepts. We will cover:

- The history behind Apache Airflow
- Why to use Airflow
- When to use Airflow
- Basic concepts and terminology
- A list of advanced concepts to explore
- Resources for learning more

## Assumed Knowledge

To get the most out of this guide, users should have knowledge of:

- Basic Python 3 programming concepts like packages and functions.

The following resources are recommended:

- [Official Python Tutorial](https://docs.python.org/3/tutorial/index.html)

## History

Airflow started as an open source project at Airbnb. In 2015, Airbnb was growing rapidly and facing larger amounts of internal data every day. To achieve the vision of becoming a fully data-driven organization, they had to grow their workforce of data engineers, data scientists, and analysts — all of whom had to regularly automate processes by writing scheduled batch jobs. To satisfy the need for a robust scheduling tool, [Maxime Beauchemin](https://soundcloud.com/the-airflow-podcast/the-origins-of-airflow) created and open-sourced Airflow with the idea that it would allow them to quickly author, iterate on, and monitor their batch data pipelines.

Since Maxime's first commit, Airflow has come a long way. The project joined the official Apache Foundation Incubator in April of 2016, and graduated as a top-level project in January 2019. As of August 2022 Airflow has over 2,000 contributors, 16,900 commits and 26,900 stars on [GitHub](https://github.com/apache/airflow).

On December 17th 2020, [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0) was released, bringing with it major upgrades and powerful new features. Airflow is used by thousands of data engineering teams around the world and continues to be adopted as the community grows stronger.

## Why to use Airflow

[Apache Airflow](https://airflow.apache.org/index.html) is a platform for programmatically authoring, scheduling, and monitoring workflows. It is open source, and especially useful in architecting and orchestrating complex data pipelines.

Data orchestration sits at the heart of any modern data stack and provides elaborate automation of data pipelines. With orchestration, actions in your data pipeline become aware of each other and your data team has a central location to gain insight into, edit and debug their workflows.

Airflow has many key benefits, such as:

- **Dynamic data pipelines**: In Airflow, pipelines are defined as Python code. Anything you can do in Python, you can do in Airflow.
- **CI/CD for data pipelines**: With all the logic of your workflows defined in Python, it is possible to implement CI/CD processes for your data pipelines.
- **Tool agnosticism**: Airflow can connect with any other tool in the data ecosystem that allows connection through an API.
- **High extensibility**: For many commonly used data engineering tools, integrations exist in the form of provider packages, which are routinely extended and updated.
- **Infinite scalability**: Given enough computing power, you can orchestrate as many processes as you need, no matter how complex your pipelines get.
- **Visualization**: Airflow comes with a fully functional UI that offers an immediate overview over data pipelines.
- **Stable REST API**: The [Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html) allows Airflow to interact with RESTful web services.
- **Easy to use**: Thanks to the [Astro CLI](https://docs.astronomer.io/astro/cli/get-started), you can get a fully functional local Airflow instance running with only three bash commands.
- **Vibrant OSS community**: With millions of users and thousands of contributors, Airflow is here to stay and grow.

## When to use Airflow

Airflow can be used for virtually any batch data pipelines, and there are a ton of [documented use cases](https://soundcloud.com/the-airflow-podcast/use-cases) in the community. Because of its extensibility, Airflow is particularly powerful for orchestrating jobs with complex dependencies in multiple external systems.

For example, the diagram below shows a complex use case that can easily be accomplished with Airflow. By writing pipelines in code and using Airflow's many available providers, you can integrate with any number of different, dependent systems with just a single platform for orchestration and monitoring.

![Example Use Case](https://assets2.astronomer.io/main/guides/intro-to-airflow/example_pipeline.png)

Some common use cases of Airflow include:

- **ETL/ELT pipelines**: For example, running a write, audit, publish pattern on data in Snowflake as shown in the example implementation in the [Orchestrating Snowflake Queries with Airflow](https://www.astronomer.io/guides/airflow-snowflake/) guide.
- **MLOps**: For example, using Airflow with Tensorflow and MLFlow as shown in [this webinar](https://www.astronomer.io/events/webinars/using-airflow-with-tensorflow-mlflow/).
- **Operationalized Analytics**: For example, orchestrating a pipeline to extract insights from your data and display them in dashboards, an implementation of which is showcased in the [Using Airflow as a Data Analyst](https://www.astronomer.io/events/webinars/using-airflow-as-a-data-analyst/) webinar.

## Core Airflow Concepts

To navigate Airflow resources, it is helpful to have a general understanding of core Airflow concepts:

- **DAG**: Directed Acyclic Graph. An Airflow DAG is a workflow defined as a graph, where all dependencies between nodes are directed and nodes do not self reference. For more information on Airflow DAGs, see the [Introduction to Airflow DAGs](https://www.astronomer.io/guides/dags/) guide.
- **DAG run**: A DAG run is the execution of a DAG at a specific point in time. A DAG can have scheduled DAG runs and/or manually triggered DAG runs.
- **Task**: A task is a node in a DAG graph describing one unit of work.
- **Task Instance**: A task instance is the combination of a task, in a specific DAG, being executed at a specific point in time.

When authoring DAGs, you will mostly interact with operators, the building blocks of DAGs. An operator is an abstraction over Python code designed to perform a specific action and takes the form of a function that accepts parameters. Each operator in your DAG code corresponds to one Airflow task.

There are three main categories of operators:

- **Action operators** execute a function, like the [`PythonOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator) or the [`BashOperator`](https://www.astronomer.io/guides/scripts-bash-operator/).
- **Transfer operators** move data from a source to a destination, like the [`S3ToRedshiftOperator`](https://registry.astronomer.io/providers/amazon/modules/s3toredshiftoperator).
- **[Sensors](https://www.astronomer.io/guides/what-is-a-sensor/)** wait for something to happen, like the [`ExternalTaskSensor`](https://registry.astronomer.io/providers/apache-airflow/modules/externaltasksensor) or the [`HttpSensorAsync`](https://registry.astronomer.io/providers/astronomer-providers/modules/httpsensorasync).

While operators are defined individually, they can pass information to each other by using [XComs](https://www.astronomer.io/guides/airflow-passing-data-between-tasks/). You can learn more about operators in the [Operators 101](https://www.astronomer.io/guides/what-is-an-operator/) guide.

Some commonly used action operators like the `PythonOperator` are part of core Airflow and are automatically installed in your Airflow instance. Operators used to interact with external systems are maintained separately to Airflow in provider packages.

**Providers** are community-maintained packages that include all of the core operators, hooks and sensors for a given service, for example:

- [Amazon provider](https://registry.astronomer.io/providers/amazon)
- [Snowflake provider](https://registry.astronomer.io/providers/snowflake)
- [Google provider](https://registry.astronomer.io/providers/google)
- [Azure provider](https://registry.astronomer.io/providers/microsoft-azure)
- [Databricks provider](https://registry.astronomer.io/providers/databricks)
- [Fivetran provider](https://registry.astronomer.io/providers/fivetran)

> **Note**: The best way to explore available providers and operators is the [Astronomer Registry](https://registry.astronomer.io/). In many cases interacting with external systems will necessitate creating an [Airflow Connection](https://www.astronomer.io/guides/connections/).

## Airflow Components

When working with Airflow, it is important to understand the underlying components of its infrastructure. Even if you mostly interact with Airflow as a DAG author, knowing which components are “under the hood” and why they are needed can be helpful for developing your DAGs, debugging, and running Airflow successfully.

Airflow has four core components that must be running at all times:

- Webserver: A Flask server running with Gunicorn that serves the [Airflow UI](https://www.astronomer.io/guides/airflow-ui/).
- [Scheduler](https://airflow.apache.org/docs/apache-airflow/stable/concepts/scheduler.html): A Daemon responsible for scheduling jobs. This is a multi-threaded Python process that determines what tasks need to be run, when they need to be run, and where they are run.
- [Database](https://www.astronomer.io/guides/airflow-database): A database where all DAG and task metadata are stored. This is typically a Postgres database, but MySQL, MsSQL, and SQLite are also supported.
- [Executor](https://www.astronomer.io/guides/airflow-executors-explained/): The mechanism that defines how the available computing resources are used to execute tasks. An executor is running within the Scheduler whenever Airflow is up.

Additionally, you may also have the following situational components:

- Triggerer: A separate process which supports [deferrable operators](https://www.astronomer.io/guides/deferrable-operators). This component is optional and must be run separately.
- Worker: The process that executes tasks, as defined by the executor. Depending on which executor you choose, you may or may not have workers as part of your Airflow infrastructure.

> **Note**: You can learn more about the Airflow infrastructure in the [Airflow's Components](https://www.astronomer.io/guides/airflow-components/) guide.

## Resources

While it is easy to get started with Airflow, there are many more concepts and possibilities to explore. You can learn more by checking out:

- The [Astro CLI](https://docs.astronomer.io/astro/cli/get-started), which is the easiest way to get Airflow running locally.
- [Astronomer Webinars](https://www.astronomer.io/events/webinars/), which cover concepts and use cases in-depth and offer the possibility to ask us questions live on air.
- [LIVE with Astronomer](https://www.astronomer.io/events/live/), which are hands-on and code-focussed live walkthroughs of specific Airflow features.
- [Astronomer Guides](https://www.astronomer.io/guides/), which cover both entry and expert level concepts in Airflow.
- The [Astronomer Academy](https://academy.astronomer.io/), which offers many video tutorials and the option to purchase full length Airflow courses and to take exams to get certified.
- The [Official Airflow Documentation](https://airflow.apache.org/docs/), which contains comprehensive guidance on how to use Airflow.

## Conclusion

After reading this guide you should have a general idea what Apache Airflow is and how it can be used. High-level knowledge about the concepts explained will give you a good foundation to dive deeper into Airflow resources.

We are excited to see where your Airflow journey takes you! Please feel free to [reach out to us](https://www.astronomer.io/contact) if you have any questions or if there's anything we can do to help you succeed.
