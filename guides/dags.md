---
title: "Introduction to Airflow DAGs"
description: "How to write your first DAG in Apache Airflow"
date: 2018-05-21T00:00:00.000Z
slug: "dags"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Airflow UI", "DAGs", "Basics"]
---

In Airflow, a DAG is a data pipeline defined in Python code. DAG stands for "directed, acyclic, graph". In that graph, each node represents a task which completes a unit of work, and each edge represents a dependency between tasks. There is no limit to what a DAG can do so long as tasks remain acyclic (tasks cannot create data that goes on to self-reference).

In this guide, we'll cover everything you need to know to get started writing your first DAG, including how to define a DAG in Python, how to run the DAG on your local computer using the Astro CLI, and how to view and monitor the DAG in the Airflow UI.

## Creating DAGs


Most DAGs will follow this flow within a Python script:

- Imports: 
- DAG instantiation:
- Task instantiation:
- Dependencies: 


DAG params
Operators and tasks
Dependencies
Providers/registry

## Running DAGs

## Viewing DAGs

Airflow UI
States

One of the key pieces of data stored in Airflow’s metadata database is **State**. States are used to keep track of what condition task instances and DAG Runs are in. In the screenshot below, we can see how states are represented in the Airflow UI:

![Status view in the Airflow UI](https://assets2.astronomer.io/main/docs/airflow-ui/status-view.png)

DAG Runs and tasks can have the following states:

### DAG States

- **Running (Lime):** DAG is currently being executed.
- **Success (Green):** DAG was executed successfully.
- **Failed (Red):** The task or DAG failed.

### Task States

- **None (Light Blue):** No associated state. Syntactically - set as Python None.
- **Queued (Gray):** The task is waiting to be executed, set as queued.
- **Scheduled (Tan):** The task has been scheduled to run.
- **Running (Lime):** The task is currently being executed.
- **Failed (Red):** The task failed.
- **Success (Green):** The task was executed successfully.
- **Skipped (Pink):** The task has been skipped due to an upstream condition.
- **Shutdown (Blue):** The task is up for retry.
- **Removed (Light Grey):** The task has been removed.
- **Retry (Gold):** The task is up for retry.
- **Upstream Failed (Orange):** The task will not run because of a failed upstream dependency.