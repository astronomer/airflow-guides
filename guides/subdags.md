---
title: "Using SubDAGs in Airflow"
description: "Using SubDAGs to build modular workflows in Airflow."
date: 2018-05-23T00:00:00.000Z
slug: "subdags"
heroImagePath: null
tags: ["DAGs", "Subdags"]
---

## Overview

SubDAGs were a legacy feature in Airflow that allowed users to implement reusable patterns of tasks in their DAGs. SubDAGs caused performance and functional issues for many users, and they have been [deprecated](https://github.com/apache/airflow/issues/12292) as of Airflow 2.0 and will be removed entirely in a future release. As such, Astronomer highly recommends against using SubDAGs and instead using an alternative supported Airflow feature.

In this guide, we'll cover some alternatives to SubDAGs and provide links to resources for implementing those features. We'll also briefly touch on some of the issues that occurred with SubDAGs so you can be sure to avoid them.

## Alternatives to SubDAGs

Since SubDAGs have been deprecated, the best practice is to use other Airflow features to implement your use case. The following alternatives cover most common use cases:

- [TaskGroups](https://www.astronomer.io/guides/task-groups): These are UI grouping concept released in Airflow 2.0 that can be used to organize tasks in the DAG's Graph View. TaskGroups are ideal if you need to simplify and organize viewing and monitoring of a complex DAG. Astronomer's academy course on [grouping in Airflow](https://academy.astronomer.io/airflow-grouping) also covers how TaskGroups can replace SubDAGs.
- [Cross-DAG dependencies](https://www.astronomer.io/guides/cross-dag-dependencies): These are dependencies implemented between different DAGs either in the same Airflow environment or across separate environments. Cross-DAG dependencies are ideal if you have task dependencies that cannot be implemented within a single DAG. There are multiple methods of implementing cross-DAG dependencies based on your use case.

## Issues with SubDAGs

SubDAGs are really just DAGs embedded in other DAGs. This can cause both performance and functional issues:

- When a SubDAG is triggered, the SubDAG and child tasks take up worker slots until the entire SubDAG is complete. This can delay other task processing and, depending on your number of worker slots, can lead to deadlocking.
- SubDAGs have their own parameters, schedule, and enabled settings. When these are not consistent with their parent DAG, unexpected behavior can occur.
