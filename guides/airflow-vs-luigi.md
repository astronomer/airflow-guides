---
title: "Airflow vs. Luigi"
description: "How Airflow differs from Luigi."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-luigi"
heroImagePath: null
tags: []
---

> This guide was last updated September 2020

As tools within the data engineering industry continue to expand their influence, it's common for product offerings in the space to be directly compared against each other for a variety of use cases.

For those evaluating [Apache Airflow](https://airflow.apache.org/) and [Luigi](https://github.com/spotify/luigi), we've put together a summary of the key differences between the two open-source frameworks.

## Airflow Overview

Created by [Airbnb Data Engineer Maxime Beauchemin](https://www.linkedin.com/in/maximebeauchemin), Airflow is an open source workflow management system designed for authoring, scheduling, and monitoring workflows as [DAGs, or directed acyclic graphs](https://www.astronomer.io/guides/dags/). Workflows are written in Python, which makes for flexible interaction with third-party APIs, databases, infrastructure layers, and data systems. As measured by Github stars and number of contributors, Apache Airflow is the most popular open-source workflow management tool on the market today.


## Luigi Overview

Luigi is an open-source framework developed by ex-Spotify engineer [Erik Bernhardsson](https://erikbern.com/). Originally created to run complex pipelines in Hadoop that powered Spotify's music recommendation engine, Luigi's design philosophy is to generalize complexities in workflow orchestration as much as possible, allowing it to be extended with other tasks such as Hive queries, Spark jobs, and more. Luigi is based in Python and allows you to parallelize workflows. It doesn't have a scheduler and users rely on cron for scheduling jobs.


## Comparison

### Compatiblity

Users write data pipelines in Python in both Luigi and Airflow, which makes them compatible with third-party tools. Almost every tool that you’d need to interface with programmatically has a Python integration, library, or API client. Where Airflow and Luigi differentiate is in Airflow’s use of operators, which allow for users to leverage community-contributed integrations. The Airflow community maintains operators for hundreds of external tools.

With the addition of the [KubernetesPodOperator](https://airflow.readthedocs.io/en/latest/howto/operator/kubernetes.html), Airflow can even schedule and execute arbitrary Docker images written in any language. Luigi’s Python base makes it compatible with many different APIs. However, Airflow is quite extensible as an agnostic orchestration layer that does not have a bias for any particular ecosystem.

### User Interface 

Airflow and Luigi both have UIs that allow you to visualize your DAGs. Both UIs help show the state of tasks (i.e., pending, failed, success, etc.). One big difference between UIs is that task logs were made easy to be found in Airflow, while this is not the case in Luigi. When a task fails, it can be very advantageous to see logs available for that task to determine why it failed.

### Scalability 

Airflow includes a centralized scheduler that allows it to efficiently scale the amount of DAGs and tasks that it is running with its different executors. Luigi does not have a scheduler and relies on cron jobs to schedule tasks. The number of cron workers limits the number of processes that can run at a time, which limits the scalability of Luigi. Additionally, Luigi cannot rerun tasks because they run with cron. Airflow allows the user to rerun tasks as many times as needed.

Airflow’s scheduler is optimized for ease of use and testing of DAGs. DAGs are coupled with data in Luigi, which makes testing challenging. Engineers usually push DAGs straight to production because of this reason.

### Community

Airflow is the most active workflow management tool in the open-source community and has 18.3k stars on Github and 1317 active contributors. See below for an image documenting code changes caused by recent commits to the project.

![Airflow](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/Screen+Shot+2018-10-12+at+10.36.27+AM.png)


Luigi has 13.8k stars and 454 active contributors on Github. See below for an image documenting code changes caused by recent commits to the project.

![Luigi](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/Screen+Shot+2018-10-12+at+10.36.19+AM.png)


## Conclusions

While both Luigi and Airflow are viable options for workflow management, the Airflow community has had considerable growth in recent years. As a result, Airflow features have been developing at a quick pace, and we've seen a large number of companies starting to use Airflow in order to reap the benefits of the strong community.

We also interviewed [Luigi creator Erik Bernhardsson](https://twitter.com/fulhack?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor) for our Airflow Podcast. He had some interesting thoughts on the directions of Luigi and Airflow, so definitely check that out [here](https://soundcloud.com/the-airflow-podcast/episode-4-competitors) if you're interested.
