---
title: "Airflow vs. Oozie"
description: "How Airflow differs from Oozie."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-oozie"
heroImagePath: "https://assets.astronomer.io/website/img/guides/Oozie+vs+Airflow.png"
tags: ["Oozie", "Competition"]
---

We often get questions regarding the differences between [Airflow](https://airflow.apache.org/) and [Oozie](http://oozie.apache.org/). Below you'll find a summary of the two tools and a comparison of the two communities surrounding the projects.

# TL;DR

Airflow leverages growing use of python to allow you to create extremely complex workflows, while Oozie allows you to write your workflows in Java and XML. The open-source community supporting Airflow is 20x the size of the community supporting Oozie.

# Airflow Overview

Created by [Airbnb Data Engineer Maxime Beauchemin](https://www.linkedin.com/in/maximebeauchemin), Airflow is an open source workflow management system designed for authoring, scheduling, and monitoring workflows as [DAGs, or directed acyclic graphs](https://www.astronomer.io/guides/dags/). All workflows are designed in python and it is currently the most popular open source workflow management tool on the market.

# Oozie Overview

Oozie is an open-source workflow scheduling system written in Java for Hadoop systems. Oozie has a coordinator that allows for jobs to be triggered by time, event, or data availability and allows you to schedule jobs via command line, Java API, and a GUI. It supports XML property files and uses an SQL database to log metadata pertaining to task orchestration.

While it has been used successfully by a few teams, [it has been reported](https://stackoverflow.com/questions/47928995/which-one-to-choose-apache-oozie-or-apache-airflow-need-a-comparison) that Oozie has difficulty handling complex pipelines and has an underdeveloped GUI that is challenging to navigate.

# Key Differences

## Python vs. Java

As mentioned above, Airflow allows you to write your DAGs in Python while Oozie uses Java or XML. Per [Codecademy](https://codecademy.com)'s recent report, the Python community has grown exponentially in recent years, and even excelled to the most active programming language on Stack Overflow in 2017:

![pythongraph](https://assets.astronomer.io/website/img/guides/lo5t9UKVQ1VDW8zq1fQg_growth-of-python.png)

## Community

Airflow is the most active workflow management tool on the market and has 8,636 stars on Github and 491 active contributors. See below for an image documenting code changes caused recent commits to the project.

![airflow](https://assets.astronomer.io/website/img/guides/Screen+Shot+2018-07-10+at+4.26.28+PM.png)

Oozie has 386 stars and 16 active contributors on Github. See below for an image documenting code changes caused by recent commits to the project.

![oozie](https://assets.astronomer.io/website/img/guides/Screen+Shot+2018-07-10+at+4.26.17+PM.png)

Note that, with open source projects, community contributions are significant in that they're reflective of the community's faith in the future of the project and indicate that features are actively being developed.

## Other Features

As pointed out by [Stack Overflow user Michele De Simoni](https://stackoverflow.com/users/8050556/michele-ubik-de-simoni), there are a few reasons why Airflow is preferred over Oozie by the community for workflow management.

### Airflow

- Python Code for DAGs (+)
- Has connectors for every major service/cloud provider (+)
- More versatile (+)
- Advanced metrics (+)
- Better UI and API (+)
- Capable of creating extremely complex workflows (+)
- Jinja Templating (+)
- Can be parallelized (=)
- Native Connections to HDFS, HIVE, PIG etc.. (=)
- Graph as DAG (=)

### Oozie

- Java or XML for DAGs (---)
- Hard to build complex pipelines (-)
- Smaller, less active community (-)
- Worse WEB GUI (-)
- Java API (-)
- Can be parallelized (=)
- Native Connections to HDFS, HIVE, PIG etc.. (=)
- Graph as DAG (=)
