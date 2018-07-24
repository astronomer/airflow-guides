---
title: "Airflow vs. Luigi"
description: "How Airflow differs from Luigi."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-luigi"
heroImagePath: null
tags: ["Luigi", "Competition"]
---

We often get questions regarding the differences between [Airflow](https://airflow.apache.org/) and [Luigi](https://github.com/spotify/luigi). Below you'll find a summary of the two tools and a comparison of the two communities surrounding the projects.

# Airflow Overview

Below is a quick summary of Airflow, but check out our [Intro to Airflow](https://www.astronomer.io/guides/intro-to-airflow/) guide if you're interested in learning more.

Created by [Airbnb Data Engineer Maxime Beauchemin](https://www.linkedin.com/in/maximebeauchemin), Airflow is an open source workflow management system designed for authoring, scheduling, and monitoring workflows as [DAGs, or directed acyclic graphs](https://www.astronomer.io/guides/dags/). All workflows are designed in python and it is currently the most popular open source workflow management tool on the market.

# Luigi Overview

Luigi is a python package developed by ex-Spotify engineer [Erik Bernhardsson](https://erikbern.com/). Originally created to run complex pipelines that powered Spotify's music recommendation engine, Luigi's design philosophy is to generalize complexities in workflow orchestration as much as possible, allowing it to be extended with other tasks such as Hive queries, Spark jobs, and more. Luigi is based in Python and allows you to parallelize workflows. 


# Comparison

As pointed out by [Quora user Angela Zhang](https://www.quora.com/Which-is-a-better-data-pipeline-scheduling-platform-Airflow-or-Luigi), Airflow and Luigi have a few key differences that are worth noting.

### Airflow

- Easy-to-use UI (+)
- Built in scheduler (+)
- Easy testing of DAGs (+)
- Separates output data and task state (+)
- Strong and active community (+)

### Luigi

- Creating and testing tasks is difficult (-)
- The UI is challenging to navigate (-)
- Not scalable due to tight coupling with cron jobs; the number of worker processes is bounded by number of cron workers assigned to a job (-)
- Re-running pipelines is not possible


+ Python Code for DAGs (+)
+ Has connectors for every major service/cloud provider (+)
+ More versatile (+)
+ Advanced metrics (+)
+ Better UI and API (+)
+ Capable of creating extremely complex workflows (+)
+ Jinja Templating (+)
+  Can be parallelized (=)
+ Native Connections to HDFS, HIVE, PIG etc.. (=)
+  Graph as DAG (=)

### Oozie

- Java or XML for DAGs (---)
- Hard to build complex pipelines (-)
- Smaller, less active community (-)
- Worse WEB GUI (-)
- Java API (-)
- Can be parallelized (=)
- Native Connections to HDFS, HIVE, PIG etc.. (=)
- Graph as DAG (=)