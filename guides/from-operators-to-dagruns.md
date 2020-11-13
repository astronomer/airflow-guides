---
title: "From Operators to DagRuns"
description: "From Operators to DagRuns"
date: 2018-05-21T00:00:00.000Z
slug: "from-operators-to-dagruns"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "DAGs"]
---

# How Work Gets Executed

**Operators become Tasks**
- Operators contain the logic - but once they are added to a DAG file with a `task_id` and `dag`, they become **tasks**.
- Being explicit, when an operator class is instantiated with a `task_id` and `dag` (along with its other settings) it becomes a **task** within a **DAG**.

**Tasks become Task Instances**
- Once a series of tasks becomes bundled to the same **DAG** object, the **DAG** can be executed based on its schedule.
- The scheduler "taps" the **DAG** and begins to execute the **tasks** depending on their dependencies.
- **Tasks** that get executed have a `execution_date` and are now called **task instances**. These get logged in the metadata database.

**DAGs become DAG Runs**
- **DAGs** that have run or are running (i.e. have an associated `execution_date`) are referred to as **DAG Runs**.
- **DAG Runs** are logged in the metadata database with their corresponding states.
- **Tasks** associated with a **DAG Run** are called **task instances**.

![title](https://assets2.astronomer.io/main/guides/airflow_task_flow.png)


**A Dag Run is an instantiation of a DAG object _in time_.**

**A Task Instance is an instantiation of a Task _in time_ and _in a DAG object_.**

## States

_States_ are used to keep track of how scheduled tasks and DAG Runs are doing. DAG Runs and tasks can have the following states:

_**DAG States**_<br>
**Running (Lime)**: The DAG is currently being executed.<br>
**Success (Green)**: The DAG executed successfully. <br>
**Failed (Red)**:  The task or DAG failed. <br>

_**Task States**_<br>
**None (Light Blue)**: No associated state. Syntactically - set as Python `None`. <br>
**Queued (Gray)** : The task is waiting to be executed, set as `queued`.<br>
**Scheduled (Tan)**: The task has been scheduled to run.<br>
**Running (Lime)**: The task is currently being executed. <br>
**Failed (Red)**:  The task failed. <br>
**Success (Green)**: The task executed successfully. <br>
**Skipped (Pink)**: The task has been skipped due to an upstream condition.<br>
**Shutdown (Blue)**: The task is up for retry. <br>
**Removed (Light Grey)**: The task has been removed. <br>
**Retry (Gold)**: The task is up for retry. <br>
**Upstream Failed (Orange)**: The task will not be run because of a failed upstream dependency.<br>

![title](https://assets2.astronomer.io/main/guides/states.png)