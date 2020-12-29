---
title: "Introduction to Apache Airflow"
description: "Everything you need to know to get started with Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "intro-to-airflow"
heroImagePath: null
tags: ["Basics", "DAGs"]
---

If you're at all involved in the data engineering space, you've probably heard of [Apache Airflow](https://github.com/apache/airflow). Since its [inception as an open-source project at AirBnb in 2015](https://medium.com/airbnb-engineering/airflow-a-workflow-management-platform-46318b977fd8), Airflow has quickly become the gold standard for data engineering, getting public contributions from folks at major orgs like [Bloomberg](https://www.techatbloomberg.com/blog/airflow-on-kubernetes/), [Lyft](https://eng.lyft.com/running-apache-airflow-at-lyft-6e53bb8fccff), [Robinhood](https://robinhood.engineering/why-robinhood-uses-airflow-aed13a9a90c8), and [many more](https://github.com/apache/airflow#who-uses-apache-airflow).

If you're just getting your feet wet, you're probably wondering what all the hype is about. We're here to walk you through the basic concepts that you need to know to get started with Airflow.

## History

In 2015, Airbnb experienced a problem. They were growing like crazy and had a massive amount of data that was only getting larger. To achieve the vision of becoming a fully data-driven organization, they had to grow their workforce of data engineers, data scientists, and analysts - all of whom had to regularly work to automate processes by writing scheduled batch jobs. To satisfy the need for a robust scheduling tool, [Data Engineer Maxime Beauchemin](https://soundcloud.com/the-airflow-podcast/the-origins-of-airflow) created and open-sourced Airflow with the idea that it would allow them to quickly author, iterate on, and monitor their batch data pipelines.

Since Maxime's first commit way back then, Airflow has come a long way. The project joined the official Apache Foundation Incubator in April of 2016, where it lived and grew until it graduated as a top-level project on January 8th, 2019. Almost two years later, as of December 2020, Airflow has over 1,400 contributors, 11,230 commits, and 19,800 stars on Github. On December 17th 2020, [Airflow 2.0](https://www.astronomer.io/blog/introducing-airflow-2-0) was released, bringing with it major upgrades and powerful new functionality. Airflow is used by thousands of Data Engineering teams around the world and is only getting more widely adopted as the community grows stronger. 

## Overview

[Apache Airflow](https://airflow.apache.org/index.html) is a platform for programmatically authoring, scheduling, and monitoring workflows. It is completely open-source and is especially useful in architecting and orchestrating complex data pipelines. Airflow was originally created to solve the issues that come with long-running cron tasks that execute hefty scripts, but has grown beyond that to be arguably the most flexible and powerful open-source data pipeline platform out there.

Airflow has a couple of key benefits, namely:

- **It's dynamic:** everything is written in Python, so anything you can do in Python you can do in Airflow
- **It's extensible:** Airlfow has many plugins available out of the box that allow you to interact with most common external systems. You can also always create your own as needed.
- **It's scalable:** teams use Airflow's broad functionality to run thousands of tasks per day.

With Airflow, workflows are architected and expressed as Directed Acyclic Graphs (DAGs), with each node of the DAG defined as a specific task. It is designed with the belief that all data pipelines are best expressed as code, and as such is a code-first platform that allows you to iterate on your workflows quickly and efficiently. As a result of its code-first design philosophy, Airflow allows for a degree of customizibility and extensibility that other pipeline tools do not support.

## Use Cases

Airflow can be used for virtually any batch data pipelines, and there are a ton of [documented use cases](https://github.com/jghoman/awesome-apache-airflow#best-practices-lessons-learned-and-cool-use-cases) in the community. Because of its extensibility, Airflow is particularly powerful for orchestrating jobs with complex dependencies in multiple external systems.

For example, the diagram below shows a complex use case that can easily be accomplished with Airflow. It highlights that by writing pipelines in code and leveraging the many available plugins, Airflow can easily integrate with any number of different, dependent systems and still provide a one-stop-shop for orchestration and monitoring.

![Example Use Case](https://assets2.astronomer.io/main/guides/intro-to-airflow/example_pipeline.png)

If you're interested in more specific examples, here are a few cool things we've seen folks do with Airflow:

- Aggregate daily sales team updates from Salesforce to send a daily report to executives at the company.
- Use Airflow to organize and kick off machine learning jobs running on external Spark clusters.
- Load website/application analytics data into a data warehouse on an hourly basis.

We further discuss Airflow's use cases in our [podcast episode here](https://soundcloud.com/the-airflow-podcast/use-cases) if you're interested in diving deeper!

## Core Concepts

### DAG

A Directed Acyclic Graph, or DAG, is a data pipeline defined in Python code. Each DAG represents a collection of all the tasks you want to run and is organized to show relationships between tasks directly in the Airflow UI. They are defined this way for the following reasons:

1. Directed: If multiple tasks with dependencies exist, each must have at least one defined upstream or downstream task.
2. Acyclic: Tasks are not allowed to create data that goes on to self-reference. This is to avoid creating infinite loops.
3. Graph: All tasks are laid out in a clear structure with processes occurring at clear points with set relationships to other tasks.

For example, the image below shows a valid DAG on the left with a couple of simple dependencies, in contrast to an invalid DAG on the right that is not acyclic.

![Example DAGs](https://assets2.astronomer.io/main/guides/intro-to-airflow/dags.png)

For a more in-depth review on DAGs, check out our [Intro to DAGs guide](https://astronomer.io/guides/dags).

### Tasks

[Tasks](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=hook#tasks) represent each node of a defined DAG. They are visual representations of the work being done at each step of the workflow, with the actual work that they represent being defined by operators.

### Operators

[Operators](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=hook#operators) are the building blocks of Airflow, and determine the actual work that gets done. They can be thought of as a wrapper around a single task, or node of a DAG, that defines how that task will be run. DAGs make sure that operators get scheduled and run in a certain order, while operators define the work that must be done at each step of the process.


![Example DAGs](https://assets2.astronomer.io/main/guides/intro-to-airflow/operator.png)

There are three main categories of operators:
 - **Action Operators** execute a function, like the [PythonOperator](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html) or [BashOperator](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/bash.html)
 - **Transfer Operators** move data from a source to a destination, like the [S3ToRedshiftOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/operators/s3_to_redshift.html)
 - **Sensor Operators** wait for something to happen, like the [ExternalTaskSensor](https://airflow.readthedocs.io/en/1.9.0/_modules/airflow/operators/sensors.html)

Operators are defined individually, but they can pass information to other operators using [XComs](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=hook#xcoms).

Taking DAGs, operators, and tasks together gives something conceptually like this:

![Combined Concepts](https://assets2.astronomer.io/main/guides/intro-to-airflow/combined_concepts.png)

### Hooks

[Hooks](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=hook#hooks) are Airflow's way of interfacing with third-party systems. They allow you to connect to external APIs and databases like Hive, S3, GCS, MySQL, Postgres, etc. They act as building blocks for operators. Secure information such as authentication credentials are kept out of hooks - that information is stored via Airflow connections in the encrypted metadata db that lives under your Airflow instance.

### Plugins

Airflow plugins represent a combination of Hooks and Operators that allow you to accomplish a certain task, like [transfer data from Salesforce to Redshift](http://astronomer.io/guides/salesforce-to-redshift). Check out our [open-source library of Airflow plugins](https://github.com/airflow-plugins) if you'd like to check if a plugin you need has already been created by the community.

### Connections

[Connections](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html?highlight=hook#connections) are where Airflow stores information that allows you to connect to external systems, such as authentication credentials or API tokens. This is managed directly from the UI and the actual information is encrypted and stored as metadata in Airflow's underlying Postgres or MySQL database.


## Learn by Doing

If you'd like to get started playing around with Airflow on your local machine, check out our [Astronomer CLI](https://github.com/astronomer/astro-cli)- it's open source and completely free to use. With the CLI, you can spin up Airflow locally and start getting your hands dirty with the core concepts mentioned above in just a few minutes. 

As always, please feel free to [reach out to us](https://astronomer.io/contact) if you have any questions or if there's anything we can do to help you on your Airflow journey!
