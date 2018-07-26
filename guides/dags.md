---
title: "Intro to Apache Airflow DAGs"
description: "What are DAGs and how they are constructed in Apache Airflow?"
date: 2018-05-21T00:00:00.000Z
slug: "dags"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["UI", "Frontend", "Airflow"]
---

# Functional Data Engineering

## What is a DAG

_Core definitions._

Data pipeline as a term is pretty straightforward. It leverages a common occurrence (i.e. plumbing) to illustrate what would otherwise be an unviewable process.

In practice, this analogy is a bit misleading, and if anything, fits for streaming architectures more than batch architectures.

Data isn’t literally in a single tube starting on one side and coming out of the other but it is isolated from other data during this time (as if in a physical pipe). Unlike water through a pipe data is transformed through a workflow and produces valuable metadata.

[In Airflow, pipelines are _directed acyclic graphs_ (DAGs)](https://airflow.apache.org/concepts.html?highlight=what%20dag#dags)

### Mathematical Background

Directed Graph: A directed graph is any graph where the vertices and edges have some sort of order or direction associated with them.

Directed Acyclic Graph: Finally, a directed acyclic graph is a directed graph without any cycles. A cycle is just a series of vertices that connect back to each other in a closed chain.

![title](https://cdn.astronomer.io/website/img/guides/dag_example.png)

In Airflow, each node in a DAG (soon to be known as a task) represents some form of data processing:

> Node A could be the code for pulling data out of an API.
>
> Node B could be the code for anonymizing the data and dropping any IP address.
>
> Node D could be the code for checking that no duplicate record ids exist.
>
> Node E could be putting that data into a database.
>
> Node F could be running a SQL query on the new tables to update a dashboard.

## Dependencies

Each of the verticies have a specific direction showing the relationship between nodes - data can only follow the direction of the vertices (from the example above, the IP addresses cannot be annonymized until the data has been pulled).

Node B is  _downstream_ from Node A - it won't execute until Node A finishes.

## DAGs are Acyclic

Workflows, particulary around those processing data, have to have a point of "completion." This espescially holds true in batch architectures to be able to say that a certain "batch" ran successfully.

![title](https://cdn.astronomer.io/website/img/guides/cycle_example.png)

### Recap

DAGs are a natural fit for batch architecture - they allow you to model natural dependencies that come up in data processing without and force you to architect your workflow with a sense of "completion."

**Directed** - If multiple tasks exist, each must have at least one defined upstream (previous) or downstream (subsequent) tasks, although they could easily have both.

**Acyclic** - No task can create data that goes on to reference itself. This could cause an infinite loop that would be, um, it’d be bad. Don’t do that.

**Graph** - All tasks are laid out in a clear structure with discrete processes occurring at set points and clear relationships made to other tasks.

## DAGs as Functional Programming

https://medium.com/@maximebeauchemin/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a

_Repeatable inputs for repeatable output_

Best practices emerging around data engineering are pointing towards concepts found in functional programming. Ideas around immutability, isolation, and idempotency that are defining charactersitics of good functional programming are very natural fits into good ETL architecture.

### Idempotency, Idempotency, Idempotency

This concept will be stressed throughout everything - idempotency is one of, if not the most, important characteristic of good ETL architecture.

Something is idempotent if it will produce the same result regardless of how many times it is run. In mathematical terms:

`$f(x) = f(f(x)) = f(f(f(x)))...$`

Idempotency usually hand in hand with **reproducability** - a set of inputs always produces the same set of outputs

Making ETL jobs idempotent can be easier for workflows  more than others - if it's just a SQL load for a days data, implemtenting upsert logic is pretty easy. If it's a file that's dropped on an externally controlled FTP that is not there for long, it is a little more difficult.

However, the initial investment is usually worth it for safety, operability, and modularity.

### Direct Association

There should be a clear and intuitive association between tables, intermediate files, and all other _levels_ of your data. DAGs are a natural fit here, as every task can have an exclusive target that does not propogate into another tasks target without a direct dependency being set.

Furthermore, this association should filter down into all metadata - logs, runtimes,

Mathematically, this idea of clarity and directness is intuitive:

`$f(x) = y$`
