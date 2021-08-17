---
title: "From Operators to DagRuns"
description: "From Operators to DagRuns"
date: 2018-05-21T00:00:00.000Z
slug: "from-operators-to-dagruns"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "DAGs"]
---
<!-- markdownlint-disable-file -->
## How Work Gets Executed in Airflow

### Operators are wrappers around types of work.

**Operators** contain the logic of how data is processed in a pipeline. There are different Operators for different types of work: some Operators execute general types of code, while others are designed to complete very specific types of work.

### An instance of an Operator is a task.

Operators are reusable task templates, and a **task** is an instantiation of an operator. Tasks take the parameters and process data within the context of the DAG.

### Tasks are nodes in a DAG.

Once you define tasks within a **DAG** object, a DAG can be executed based on its schedule. A built-in Scheduler in Airflow "taps" the DAG and begins to execute the tasks based on their dependencies.

A real-time run of a task is called a **task instance**. These task instances get logged in the metadata database with information about when and how they ran.

### DAGs become DAG Runs

If a task instance is a run of a task, then a **DAG Run** is simply an instance of a complete DAG that has run or is currently running. At the code level, a DAG becomes a DAG Run once it has an `execution_date`. Just like with task instances, information about each DAG Run is logged in Airflow’s metadata database.

## States

One of the key pieces of data stored in Airflow’s metadata database is **State**. States are used to keep track of how task instances and DAG Runs are performing. In the screenshot below, we can see how states are represented in the Airflow UI:

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
