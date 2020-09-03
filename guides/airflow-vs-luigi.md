---
title: "Airflow vs. Luigi"
description: "How Airflow differs from Luigi."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-luigi"
heroImagePath: null
tags: ["Luigi", "Competition"]
---

We often get questions regarding the differences between [Airflow](https://airflow.apache.org/) and [Luigi](https://github.com/spotify/luigi). Below you'll find a summary of the two tools and a comparison of the two communities surrounding the projects.

## Airflow Overview

Created by [Airbnb Data Engineer Maxime Beauchemin](https://www.linkedin.com/in/maximebeauchemin), Airflow is an open source workflow management system designed for authoring, scheduling, and monitoring workflows as [DAGs, or directed acyclic graphs](https://www.astronomer.io/guides/dags/). All workflows are designed in python and it is currently the most popular open source workflow management tool on the market.

## Luigi Overview

Luigi is a python package developed by ex-Spotify engineer [Erik Bernhardsson](https://erikbern.com/). Originally created to run complex pipelines that powered Spotify's music recommendation engine, Luigi's design philosophy is to generalize complexities in workflow orchestration as much as possible, allowing it to be extended with other tasks such as Hive queries, Spark jobs, and more. Luigi is based in Python and allows you to parallelize workflows. It doesn't have a scheduler and users still have to rely on cron for scheduling jobs.


## Comparison

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


## Conclusions

While both Luigi and Airflow are viable options for workflow management, the Airflow community has grown to be much stronger than that of Luigi in recent years. As a result, Airflow features have been developing at a much quicker pace, and we've seen a "snowball effect" of companies migrating from Luigi to Airflow in order to reap the benefits of the strong community. Check out the photos below for code contributions to the two projects, and note the scale of the y axis in each:

![Airflow](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/Screen+Shot+2018-10-12+at+10.36.27+AM.png)

![Luigi](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/Screen+Shot+2018-10-12+at+10.36.19+AM.png)

We also interviewed [Luigi creator Erik Bernhardsson](https://twitter.com/fulhack?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor) for our Airflow Podcast. He had some interesting thoughts on the directions of Luigi and Airflow, so definitely check that out [here](https://soundcloud.com/the-airflow-podcast/episode-4-competitors) if you haven't heard it yet.
