---
title: "Introduction to Apache Airflow"
description: "Everything you need to know to get started with Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "intro-to-airflow"
heroImagePath: null
tags: ["Basics", "Intro", "Concepts", "Start"]
---

[Apache Airflow](https://airflow.apache.org/) is the de facto standard for programmatic data orchestration. Airflow is freely available as open source software, has over 9 million downloads per month and a vibrant OSS community.

Data practitioners are choosing Airflow because it allows them to define their data pipelines as Python code in a highly extensible and infinitely scalable way. Since Airflow is tool agnostic is the glue that holds your data ecosystem together.

This guide offers an introduction to Apache Airflow and its core concepts. We will cover:

- The history behind Apache Airflow
- Why to use Airflow
- When to use Airflow
- Basic concepts and terminology
- A list of advanced concepts to explore
- Resources to learn more.

> **Quickstart**: If you like learning by doing you can follow the [Get Started with Airflow](linkplaceholder) tutorial to get a practical introduction to Apache Airflow, complementary to this guide.

## Assumed Knowledge

To get the most out of this guide, users should have knowledge of:

- Basic Python 3 programming concepts like packages and functions.

The following resources are recommended:

- [Official Python Tutorial](https://docs.python.org/3/tutorial/index.html)

## History

Airflow started as an open source project at Airbnb. In 2015 they were growing rapidly and the facing larger amounts of internal data every day. To achieve the vision of becoming a fully data-driven organization, they had to grow their workforce of data engineers, data scientists, and analysts — all of whom had to regularly automate processes by writing scheduled batch jobs. To satisfy the need for a robust scheduling tool, [Maxime Beauchemin](https://soundcloud.com/the-airflow-podcast/the-origins-of-airflow) created and open-sourced Airflow with the idea that it would allow them to quickly author, iterate on, and monitor their batch data pipelines.

Since Maxime's first commit way back then, Airflow has come a long way. The project joined the official Apache Foundation Incubator in April of 2016, where it lived and grew until it graduated as a top-level project in January 2019. As of August 2022 Airflow has over 2'000 contributors, 16'900 commits and 26'900 stars on [GitHub](https://github.com/apache/airflow).

On December 17th 2020, [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0) was released, bringing with it major upgrades and powerful new features. Airflow is used by thousands of Data Engineering teams around the world and continues to be adopted as the community grows stronger.

## Why to use Airflow

[Apache Airflow](https://airflow.apache.org/index.html) is a platform for programmatically authoring, scheduling, and monitoring workflows. It is open source and especially useful in architecting and orchestrating complex data pipelines.

Data orchestration sits at the heart of any modern data stack and provides elaborate automation of data pipelines. With orchestration, actions in your data pipeline become aware of each other and your data team has a central location to gain insight into, edit and debug their workflows.

Airflow has many key benefits like:

- **Dynamic data pipelines**: In Airflow pipelines are defined as Python code. Anything you can do in Python, you can do in Airflow.
- **CI/CD for data pipelines**: With all logic of your workflows defined in Python it is possible to implement CI/CD processes for your data pipeline.
- **Tool agnosticism**: Airflow can connect with any other tool in the Data Engineering space that allows connection through an API.
- **High Extensibility**: For many commonly used data engineering tools, integrations exist in form of provider packages, which are routinely extended and updated.
- **Infinite Scalability**: given enough computing power you can orchestrate as many processes as you need, no matter how complex your pipelines get.
- **Visualization**: Airflow comes with a fully functional UI that offers immediate overview over data pipelines.
- **Stable REST API**:
- **Easy of use**: thanks to the [Astro CLI](ttps://docs.astronomer.io/astro/cli/get-started) you can get a fully functional local dockerized Airflow instance running with only three bash commands.
- **Vibrant OSS community**: with millions of users Airflow is here to stay and grow.

> **Note**: Astronomer is a company providing managed Airflow in production as a service to cooperations. We work closely with the OSS Airflow community and provide open source tools like the [Astro CLI](https://docs.astronomer.io/astro/cli/get-started), [the Astronomer provider](https://registry.astronomer.io/providers/astronomer-providers) and resources like guides, webinars and the [Astronomer Registry](https://registry.astronomer.io/).

## When to use Airflow

Airflow can be used for virtually any batch data pipelines, and there are a ton of [documented use cases](https://github.com/jghoman/awesome-apache-airflow#best-practices-lessons-learned-and-cool-use-cases) in the community. Because of its extensibility, Airflow is particularly powerful for orchestrating jobs with complex dependencies in multiple external systems.

For example, the diagram below shows a complex use case that can easily be accomplished with Airflow. By writing pipelines in code and using Airflow's many available providers, you can integrate with any number of different, dependent systems with just a single platform for orchestration and monitoring.

![Example Use Case](https://assets2.astronomer.io/main/guides/intro-to-airflow/example_pipeline.png)

Some common use cases of Airflow include:

- **ETL/ELT pipelines**: for example running a write, audit, publish pattern on data in Snowflake as shown in the example implementation in the [Orchestrating Snowflake Queries with Airflow](https://www.astronomer.io/guides/airflow-snowflake/) guide.
- **MLOps**: for example using Airflow with Tensorflow and MLFlow as shown in [this webinar](https://www.astronomer.io/events/webinars/using-airflow-with-tensorflow-mlflow/).
- **Operationalized Analytics**: for example orchestrating a pipeline to extract insights from your data and display them in dashboards, an implementation of which is showcased in the [Using Airflow as a Data Analyst](https://www.astronomer.io/events/webinars/using-airflow-as-a-data-analyst/) webinar.

> **Note**: If you are interested in diving deeper into use cases give this [Astronomer podcast](https://soundcloud.com/the-airflow-podcast/use-cases) episode a listen!

## Core Airflow Concepts

To navigate Airflow resources it is helpful to have a general understanding of  core Airflow concepts:

- **DAG**: Directed Acyclic Graph. An Airflow DAG is a workflow defined as a graph where all dependencies between nodes are directed and does not contain circles. For more information on Airflow DAGs see the [Introduction to Airflow DAGs](https://www.astronomer.io/guides/dags/) guide.
- **Dagrun**: The execution of a DAG at a specific point in time is called a Dagrun. A DAG can have scheduled Dagruns for example hourly or daily and manually triggered Dagruns.
- **Task**: In Airflow, a task is a node in a DAG graph describing one unit of work.
- **Task Instance**: The combination of a task in a specific DAG being executed at a specific point in time is refered to as a task instance.

When authoring DAGs you will mostly interact with Operators, the building blocks of DAGs. An operator is an abstraction over Python code designed to perform a specific action and takes the form of a function that accepts parameters. Each Operator in your DAG code corresponds to one Airflow task.

There are three main categories of operators:

- **Action Operators** execute a function, like the [PythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator) or the [BashOperator](https://www.astronomer.io/guides/scripts-bash-operator/).
- **Transfer Operators** move data from a source to a destination, like the [S3ToRedshiftOperator](https://registry.astronomer.io/providers/amazon/modules/s3toredshiftoperator).
- **[Sensors](https://www.astronomer.io/guides/what-is-a-sensor/)** wait for something to happen, like the [ExternalTaskSensor](https://registry.astronomer.io/providers/apache-airflow/modules/externaltasksensor) or the [HttpSensorAsync](https://registry.astronomer.io/providers/astronomer-providers/modules/httpsensorasync).

While operators are defined individually, they can pass information to each other by using [XComs](https://www.astronomer.io/guides/airflow-passing-data-between-tasks/). You can learn more about operators in the [Operators 101](https://www.astronomer.io/guides/what-is-an-operator/) guide.

Airflow comes with a set of preinstalled operators that can be extended by using Airflow provider packages.

**Providers** are community-maintained packages that include all of the core operators, hooks and sensors for a given service, for example:

- [Amazon Provider](https://registry.astronomer.io/providers/amazon)
- [Snowflake Provider](https://registry.astronomer.io/providers/snowflake)
- [Google Provider](https://registry.astronomer.io/providers/google)
- [Azure Provider](https://registry.astronomer.io/providers/microsoft-azure)
- [Databricks Provider](https://registry.astronomer.io/providers/databricks)
- [Fivetran Provider](https://registry.astronomer.io/providers/fivetran)

> **Note**: The best way to explore available providers and operators is the [Astronomer Registry](https://registry.astronomer.io/)!

**[Connections](https://www.astronomer.io/guides/connections/)** are where Airflow stores information that allows you to connect to external systems, such as authentication credentials or API tokens. This is managed directly from the UI and the actual information is encrypted and stored in the Airflow metadata database. Connections use [Hooks](https://www.astronomer.io/guides/what-is-a-hook/) as a way of interfacing with third party systems.

## Airflow Components

A fully functional Airflow instance is comprised of several components. While you don't have to interact directly with them when authoring DAGs it is good to have a general idea about what they are and their functionality.

The 4 components that are mandatory for Airflow to function are:

- The **Scheduler**: schedules DAGs and tasks.
- The **[Executor](https://www.astronomer.io/guides/airflow-executors-explained/)**: defines how the available computing resources are used to execute a task.
- The **Webserver**: serves the [Airflow UI](https://www.astronomer.io/guides/airflow-ui/) at `localhost:8080`.
- The **[Metadata Database]((https://www.astronomer.io/guides/airflow-database))**: stores all metadata generated by the Airflow instance.

Additionally you can have:

- a **Triggerer**: which is necessary when working with [Deferrable Operators](https://www.astronomer.io/guides/deferrable-operators/).
- one or more Celery **Worker**s: that distribute the task load in distributive set ups.   

## Resources

While it is easy to get started with Airflow there are many more concepts and possibilities to explore. You can learn more by checking out:

- [Astronomer Webinars](https://www.astronomer.io/events/webinars/) cover concepts and use cases in-depth and offer the possibility to ask us questions live on air.
- [Live with Astronomer](https://www.astronomer.io/events/live/) are hands-on and code focussed live walkthroughs of specific Airflow features.
- [Astronomer Guides](https://www.astronomer.io/guides/) cover both entry and expert level concepts in Airflow.
- The [Astronomer Academy](https://academy.astronomer.io/) offers many video tutorials and the option to purchase full length Airflow courses and to take exams to get certified.
- The [Official Airflow Documentation](https://airflow.apache.org/docs/) contains comprehensive guidance on how to use Airflow.

## Conclusion

After reading this guide should should have a general idea what Apache Airflow is and how it can be used. High-level knowledge about the concept explained will give you a good foundation to dive deeper into Airflow resources.

We are excited to see where your Airflow journey takes you! Please feel free to [reach out to us](https://www.astronomer.io/contact) if you have any questions or if there's anything we can do to help you succeed!
