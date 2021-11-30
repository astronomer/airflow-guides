---
title: "Debugging DAGs"
description: "A beginner's guide to figuring out what's going wrong with your Airflow DAGs"
date: 2021-11-18T00:00:00.000Z
slug: "debugging-dags"
heroImagePath: null
tags: ["DAGs", "Basics"]
---

## Overview

Getting started with Airflow is easy if you know a bit of Python; you create your DAG file, import your operators, define your tasks, and you're off and running. But what happens when you run your DAG and something goes wrong? Maybe your tasks are failing unexpectedly, or are stuck in a scheduled state, or your DAGs aren't showing up in the Airflow UI at all. 

For these common situations (and a few more), we've got you covered! In this guide, we'll cover some frequently encountered issues with Airflow DAGs, and how to debug them. If you're brand new to Airflow, we recommend also checking out one of our I[ntroduction to Airflow Webinars](https://www.astronomer.io/events/webinars/intro-to-data-orchestration-with-airflow) to get started.

> Note: This guide focuses on Airflow 2.0+. For older Airflow versions, some debugging steps may be irrelevant or slightly different. 

## DAGs Aren't Showing Up in the Airflow UI

One of the first issues an Airflow user can encounter when developing DAGs is the DAGs not showing up in the Airflow UI. Maybe you've defined a DAG in a Python file and added it to your `dag_folder`, but when you check the Airflow UI, nothing shows up. 

Typically, if your DAG file has a syntax error or any error that causes Airflow to be unable to parse the DAG, you'll see an `Import Error` in the Airflow UI. 

SCREENSHOT

In these cases, the error message in the UI should tell you what you need to fix. 

If you *don't* see an import error message, here are some debugging steps to try:

- Airflow scans the `dags_folder` for *new* DAGs every `dag_dir_list_interval`, which defaults to 5 minutes but can be modified. Make sure this interval has passed since you added the DAG. Otherwise, you may just have to wait.
- Run `airflow dags list` with the [Airflow CLI](https://airflow.apache.org/docs/apache-airflow/stable/usage-cli.html) to make sure Airflow has registered the DAG in the metastore. If the DAG shows in the list, try restarting the webserver.
- Try restarting the scheduler (if you are using the [Astronomer CLI](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart), run `astro dev stop && astro dev start`)
- If you see an error that the scheduler is not heart beating like below, check the scheduler logs to see if something in the DAG file is causing the scheduler to crash. Then try restarting.

    SCREENSHOT

If you have this issue when working from an Astronomer Airflow deployment, there are a few additional things you can check:

- Ensure your Dockerfile Runtime/Astronomer Certified version matches the Airflow version of your deployment. A mismatch here can cause DAGs not to show up after they've been deployed.
- For Astronomer Certified images, ensure you are using the `onbuild` image (e.g. `FROM quay.io/astronomer/ap-airflow:2.2.2-buster-onbuild`). Images without `onbuild` will not bundle files in the `dags/` folder when deployed.
- Ensure the permissions on your local files aren't too [locked down](https://forum.astronomer.io/t/dags-arent-showing-up-in-my-astronomer-deployment-but-i-see-them-locally/146). 

## Tasks Aren't Running

- Make sure your DAG is toggled `On`

## Tasks Have a Failure Status

## Logs Aren't Showing Up

## Addressing Failures
