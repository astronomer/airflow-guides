---
title: "Data Driven Scheduling in Airflow"
description: "Using datasets to implement DAG dependencies and scheduling in Airflow."
date: 2022-09-01T00:00:00.000Z
slug: "airflow-datasets"
tags: ["DAGs", "Dependencies", "Scheduling"]
---

The release of [Airflow 2.4](link release notes!) includes a new concept of datasets and data dependencies. This means that DAGs that touch the same data will have explicit, visible relationships, and DAGs can be scheduled based on updates to these datasets. This feature is a big step forward in making Airflow data-aware, and vastly expands Airflow's scheduling capabilities beyond time-based methods like Cron.

This feature will help with many common use cases, such as when a data engineering team has a DAG that creates a dataset, and an analytics team has a DAG that completes analysis of that data. Using datasets, the data analytics team can ensure their DAG runs only when the data engineering team's DAG has finished publishing the dataset.

In this guide, we'll explain the concept of datasets in Airflow and how to use them to implement triggering of DAGs based on dataset updates.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- Airflow scheduling concepts. See [Scheduling and Timetables in Airflow](https://www.astronomer.io/guides/scheduling-in-airflow/).
- Creating dependencies between DAGs. See [Cross-DAG Dependencies](https://www.astronomer.io/guides/cross-dag-dependencies/).

## Dataset Concepts

Code snippets


There are a couple of things to keep in mind when working with datasets:

- Datasets can only be used by DAGs in the *same* Airflow environment.
- 

The Airflow UI gives you observability for datasets and data dependencies in the DAG's schedule, the new **Datasets** tab, and the **DAG Dependencies** view.

On the **DAGs** view, we can see that our `dataset_downstream_1_2` DAG is scheduled on two upstream datasets (one in `dataset_upstream1` and `dataset_upstream2`), and its next run is pending one dataset update. At this point the `dataset_upstream` DAG has run and updated its dataset, but the `dataset_upstream2` DAG has not.

SCREENSHOT

The new **Datasets** tab shows a list of all datasets in your Airflow environment, including how many tasks update the dataset ("Producing tasks"), and how many DAGs are scheduled on updates to that dataset ("Consuming DAGs").

SCREENSHOT

The **DAG Dependencies** view (found under the **Browse** tab) shows a graph of all dependencies between DAGs (in green) and datasets (in orange) in your Airflow environment.

SCREENSHOT

## Example Dataset Implementation

 