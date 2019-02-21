---
title: "Introduction to Apache Airflow"
description: "Everything you need to know to get started with Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "intro-to-airflow"
heroImagePath: null
tags: ["Airflow"]
---

If you're at all involved in the data engineering space, you've probably heard of [Apache Airflow](https://github.com/apache/airflow). Since its [inception as an open-source project at AirBnb in 2015](https://medium.com/airbnb-engineering/airflow-a-workflow-management-platform-46318b977fd8), Airflow has quickly become the gold standard for data engineering, getting public contributions from folks at major orgs like [Bloomberg](https://www.techatbloomberg.com/blog/airflow-on-kubernetes/), [Lyft](https://eng.lyft.com/running-apache-airflow-at-lyft-6e53bb8fccff), [Robinhood](https://robinhood.engineering/why-robinhood-uses-airflow-aed13a9a90c8), and [many more](https://github.com/apache/airflow#who-uses-apache-airflow).

If you're just getting your feet wet, you're probably wondering what all the hype is about. We're here to walk you through the basic concepts that you need to know to get started with Airflow.

## History

In 2015, Airbnb experienced a problem. They were growing like crazy and had a massive amount of data that was only getting larger. To achieve the vision of becoming a fully data-driven organization, they had to grow their workforce of data engineers, data scientists, and analysts- all of whom had to regularly work to automate processes by writing scheduled batch jobs. To satisfy the need for a robust scheduling tool, [Data Engineer Maxime Beauchemin](https://soundcloud.com/the-airflow-podcast/the-origins-of-airflow) created and open-sourced Airflow with the idea that it would allow them to quickly author, iterate on, and monitor their batch data pipelines.

Since Maxime's first commit way back then, Airflow has come a long way. The project joined the official Apache Foundation Incubator in April of 2016, where it lived and grew until it graduated as a top-level project on January 8th, 2019. As of February 2019, Airflow has 715 contributors, 5958 commits, and 11,108 stars on Github. It's used by almost every major Data Engineering team around the world and is only getting more powerful as the community grows stronger. 

## Overview

[Apache Airflow](https://airflow.apache.org/index.html) is a platform for programmatically authoring, scheduling, and monitoring workflows. It is completely open-source and is especially useful in architecting complex data pipelines. It's written in Python, so you're able to interface with any third party python API or database to extract, transform, or load your data into its final destination. It was created to solve the issues that come with long-running cron tasks that execute hefty scripts.

With Airflow, workflows are architected and expressed as DAGs, with each step of the DAG defined as a specific Task. It is designed with the belief that all ETL (Extract, Transform, Load data processing) is best expressed as code, and as such is a code-first platform that allows you to iterate on your workflows quickly and efficiently. As a result of its code-first design philosophy, Airflow allows for a degree of customizibility and extensibility that other ETL tools do not support.

## Use Cases

There are a ton of [documented use cases for Airflow](https://github.com/jghoman/awesome-apache-airflow#best-practices-lessons-learned-and-cool-use-cases). While there are a plethora of different use cases Airflow can address, it's particularly good for just about any ETL you need to do- since every stage of your pipeline is expressed as code, it's easy to tailor your pipelines to fully fit your needs. Whether it be pinging specific API endpoints or performing custom transformations that clean the data according to your custom specifications, there is truly any way you can tailor things to fit your use case.

If you're interested in getting more specific, here are a few cool things we've seen folks do with Airflow:

- Aggregate daily sales team updates from Salesforce to send a daily report to executives at the company.
- Use Airflow to organize and kick off machine learning jobs running on external Spark clusters.
- Load website/applicaiton analytics data into a data warehouse on an hourly basis.

We further discuss Airflow's use cases in our [podcast episode here](https://soundcloud.com/the-airflow-podcast/use-cases) if you're interested in diving deeper!

## Core Concepts

### DAG

DAG stands for "Directed Acyclic Graph". Each DAG represents a collection of all the tasks you want to run and is organized to show relationships between tasks directly in the Airflow UI. They are defined this way for the following reasons:

1. Directed: If multiple tasks exist, etch must have at least one defined upstream or downstream task.
2. Acyclic: Tasks are not allowed to create data that goes on to self-reference. This is to avoid creating infinite loops.
3. Graph: All tasks are laid out in a clear structure with processes occurring at clear points with set relationships to other tasks.

For a more in-depth review on DAGs, check out our [Intro to DAGs guide](https://astronomer.io/guides/dags).

### Tasks

Tasks represent each node of a defined DAG. They are visual representations of the work being done at each step of the workflow, with the actual work that they represent being defined by Operators.

### Operators

Operators in Airflow determine the actual work that gets done. They define a single task, or one node of a DAG. DAGs make sure that operators get scheduled and run in a certain order, while operators define the work that must be done at each step of the process.

Operators are typically standalone and do not share information with other operators, but you can check out [XComs](https://airflow.apache.org/concepts.html#xcoms) if you're interested in how they might work with other operators. DAGs make sure operators are run in a specific order.

### Hooks

Hooks are Airflow's way of interfacing with third-party systems. They allow you to connect to external APIs and databases like Hive, S3, GCS, MySQL, Postgres, etc. They act as building blocks for larger operators. Secure information such as authentication credentials are kept out of hooks- that information is stored via Airflow connections in the encrypted metadata db that lives under your Airflow instance.

### Plugins

Airflow plugins represent a combination of Hooks and Operators that allows you to accomplish a certain task, like [transfer data from Salesforce to Redshift](http://astronomer.io/guides/salesforce-to-redshift). Check out our [open-source library of Airflow plugins](https://github.com/airflow-plugins) if you'd like to check if a plugin you need has already been created by the community.

### Connections

Connections are where Airflow stores information that allows you to connect to external systems, such as authentication credentials or API tokens. This is managed directly from the UI and the actual information is encrypted and stored in as metadata in Airflow's underlying Postgres or MySQL.


## Learn by Doing

If you'd like to get started playing around with Airflow on your local machine, check out our [Astronomer CLI](https://github.com/astronomer/astro-cli)- it's open source and completely free to use. With the CLI, you can spin up Airflow locally and start getting your hands dirty with the core concepts mentioned above in just a few minutes. 

As always, please feel free to [reach out to us](https://astronomer.io/contact) if you have any questions or if there's anything we can do to help you on your Airflow journey!