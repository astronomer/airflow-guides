---
title: "Airflow vs. Oozie"
description: "How Airflow differs from Oozie."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-oozie"
tags: ["Oozie", "Competition"]
---

> This guide was last updated September 2020

We often get questions regarding the differences between [Airflow](https://airflow.apache.org/) and [Oozie](http://oozie.apache.org/). While we at Astronomer may be a bit biased in our knowledge, we’ve done our best to give an objective summary of the differences between two open-source frameworks for data engineering.

## Summary

At a high level, Airflow leverages the increasingly standardized use of Python to allow you to create extremely complex workflows via a commonly understood programming language, while Oozie is optimized for writing Hadoop workflows in Java and XML. While both projects are open-sourced and supported by the Apache foundation, Airflow has a larger and more active community.

## Airflow Overview

Created by [Airbnb Data Engineer Maxime Beauchemin](https://www.linkedin.com/in/maximebeauchemin), Airflow is an open-source workflow management system designed for authoring, scheduling, and monitoring workflows as [DAGs, or directed acyclic graphs](https://www.astronomer.io/guides/dags/). Workflows are designed in Python, which allows them to be flexible in their interaction with third-party APIs, databases, infrastructure layers, and data systems. It is currently the most popular open-source workflow management tool on the market, as measured by Github stars and contributors.

## Oozie Overview

Oozie is an open-source workflow scheduling system written in Java for Hadoop systems. Oozie has a coordinator that triggers jobs by time, event, or data availability and allows you to schedule jobs via command line, Java API, and a GUI. Workflows are written in hPDL (XML Process Definition Language) and use an SQL database to log metadata for task orchestration. Workflows can support jobs such as Hadoop Map-Reduce, Pipe, Streaming, Pig, Hive, and custom Java applications.

## Key Differences

### Compatibility

The main difference between Oozie and Airflow is their compatibility with data platforms and tools. Oozie was primarily designed to work within the Hadoop ecosystem. Contributors have expanded Oozie to work with other Java applications, but this expansion is limited to what the community has contributed. Airflow, on the other hand, is quite a bit more flexible in its interaction with third-party applications. In-memory task execution can be invoked via simple bash or Python commands. With the addition of the [KubernetesPodOperator](https://airflow.readthedocs.io/en/latest/howto/operator/kubernetes.html), Airflow can even schedule execution of arbitrary Docker images written in any language. With these features, Airflow is quite extensible as an agnostic orchestration layer that does not have a bias for any particular ecosystem.

### Python vs. Java

As mentioned above, Airflow allows you to write your DAGs in Python while Oozie uses Java or XML. Per the [PYPL popularity index](http://pypl.github.io/PYPL.html), which is created by analyzing how often language tutorials are searched on Google, Python now consumes over 30% of the total market share of programming and is far and away the most popular programming language to learn in 2020.  Because of its pervasiveness, Python has become a first-class citizen of all APIs and data systems; almost every tool that you’d need to interface with programmatically has a Python integration, library, or API client. Java is still the default language for some more traditional Enterprise applications but it’s indisputable that Python is a first-class tool in the modern data engineer’s belt.

### Community

Airflow is the most active workflow management tool in the open-source community and has 18.3k stars on Github and 1317 active contributors. See below for an image documenting code changes caused by recent commits to the project.

![airflow](https://assets2.astronomer.io/main/guides/airflow_contrib_2020.png)

Oozie has 584 stars and 16 active contributors on Github. See below for an image documenting code changes caused by recent commits to the project.

![oozie](https://assets2.astronomer.io/main/guides/oozie_contrib_2020.png)

Community contributions are significant in that they're reflective of the community's faith in the future of the project and indicate that the community is actively developing features. Oozie will work to orchestrate your Hadoop workflows but go with Airflow to future proof your data infrastructure as its active community will continue to add features, support, and extensions that help accommodate more robust use cases.

