---
title: "Airflow vs. Oozie"
description: "How Airflow differs from Oozie."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-oozie"
heroImagePath: null
tags: ["Oozie", "Competition"]
---

We often get questions regarding the differences between [Airflow](https://airflow.apache.org/) and [Oozie](http://oozie.apache.org/). Below you'll find a summary of the two tools and a comparison of the two communities surrounding the projects.

# Airflow

Below is a quick summary of Airflow, but check out our [Intro to Airflow](https://www.astronomer.io/guides/intro-to-airflow/) guide if you're interested in learning more.

Created by [Airbnb Data Engineer Maxime Beauchemin](https://www.linkedin.com/in/maximebeauchemin), Airflow is an open source workflow management system designed for authoring, scheduling, and monitoring workflows as [DAGs, or directed acyclic graphs](https://www.astronomer.io/guides/dags/). All workflows are designed in python and it is currently the most popular open source workflow management tool on the market.

Airflow has 8,636 stars on Github and 491 active contributors. See below for an image documenting code changes caused recent commits to the project.

![airflow](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/Screen+Shot+2018-07-10+at+4.26.28+PM.png)

# Oozie

Oozie is an open-source workflow scheduling system written in Java for Hadoop systems. Oozie has a coordinator that allows for jobs to be triggered by time, event, or data availability and allows you to schedule jobs via command line, Java API, and a GUI. It supports XML property files and uses an SQL database to log metadata pertaining to task orchestration.

While it has been used successfully by a few teams, [it has been reported](https://stackoverflow.com/questions/47928995/which-one-to-choose-apache-oozie-or-apache-airflow-need-a-comparison) that Oozie has difficulty handling complex pipelines and has an underdeveloped GUI that is challenging to navigate.

Oozie has 386 stars and 16 active contributors on Github. See below for an image documenting code changes caused by recent commits to the project.

![oozie](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/Screen+Shot+2018-07-10+at+4.26.17+PM.png)

