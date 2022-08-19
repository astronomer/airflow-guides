---
title: "Data Driven Scheduling in Airflow"
description: "Using datasets to implement DAG dependencies and scheduling in Airflow."
date: 2022-09-01T00:00:00.000Z
slug: "airflow-datasets"
tags: ["DAGs", "Dependencies", "Scheduling"]
---

With the release of [Airflow 2.4](link release notes!), users have access to a data dependency mechanism which can be used across DAGs. This means that DAGs that touch the same data will have explicit, visible relationships, and DAGs can be scheduled based on updates to these datasets. This feature is a big step forward in making Airflow data-aware, and vastly expands Airflow's scheduling capabilities beyond time-based methods like Cron.

This feature will help with many common use cases, such as when a data engineering team has a DAG that publishes a dataset, and an analytics team has a DAG that completes analysis of that data. Using datasets, the data analytics team can ensure their DAG runs only when the data engineering team's DAG has finished publishing the dataset.

In this guide, we'll explain the concept of datasets in Airflow and how to use them to implement triggering of DAGs based on dataset updates.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- Airflow scheduling concepts. See [Scheduling and Timetables in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow/).
- Creating dependencies between DAGs. See [Cross-DAG Dependencies](https://www.astronomer.io/guides/cross-dag-dependencies/).

## Dataset Concepts

Code snippets


There are a couple of things to keep in mind when working with datasets:

- 
- 

The Airflow UI gives us observability for datasets and data dependencies in the new **Datasets** tab, the **DAG Dependencies** view, and the DAG's schedule.


## Example Dataset Implementation

 