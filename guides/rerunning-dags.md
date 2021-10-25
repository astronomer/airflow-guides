---
title: "Re-running Airflow DAGs"
description: "How to use catchup, backfill, and cleared task instances to re-run DAGs in Airflow."
date: 2021-10-28T00:00:00.000Z
slug: "rerunning-dags"
tags: ["DAGs"]
---

## Overview

In Airflow have multiple options for triggering historical DAG runs or even re-running specific DAG runs.

In this guide, we'll cover the concepts of catchup, backfilling, and re-running tasks as methods for re-running all or parts of your DAG, as well as best practices for using these methods. 

## Catchup

For other catchup params: https://www.astronomer.io/guides/scheduling-tasks

## Backfill

## Re-running Tasks

## Best Practices

We have a lot of customers attempt to run Airflow backfills without fully knowing best practices. We should write a doc that covers:

the Airflow CLI backfill command not being super reliable (yet)
warning against changing or modifying task status in the the database (postgres on Astronomer) directly
scheduling best practices
resource considerations
