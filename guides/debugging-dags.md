---
title: "Debugging DAGs"
description: "A beginner's guide to figuring out what's going wrong with your Airflow DAGs"
date: 2021-12-01T00:00:00.000Z
slug: "debugging-dags"
heroImagePath: null
tags: ["DAGs", "Basics"]
---

## Overview

Getting started with Airflow is easy if you know a bit of Python; you create your DAG file, import your operators, define your tasks, and you're off and running. But what happens when you run your DAG and something goes wrong? Maybe your tasks are failing unexpectedly, or are stuck in a scheduled state, or your DAGs aren't showing up in the Airflow UI at all. 

For these common situations (and a few more), we've got you covered! In this guide, we'll cover some frequently encountered issues with Airflow DAGs, and how to debug them. If you're brand new to Airflow, we recommend also checking out one of our [Introduction to Airflow Webinars](https://www.astronomer.io/events/webinars/intro-to-data-orchestration-with-airflow) to get started.

> Note: This guide focuses on Airflow 2.0+. For older Airflow versions, some debugging steps may be slightly different. 

## DAGs Aren't Showing Up in the Airflow UI

One of the first issues an Airflow user can encounter when developing DAGs is the DAGs not showing up in the Airflow UI. Maybe you've defined a DAG in a Python file and added it to your `dags_folder`, but when you check the Airflow UI, nothing shows up. 

Typically, if your DAG file has any error that causes Airflow to be unable to parse the DAG, you'll see an `Import Error` in the Airflow UI. 

![Import Error](https://assets2.astronomer.io/main/guides/debugging-dags/import_error.png)

In these cases, the error message in the UI should tell you what you need to fix. Most frequently these will be syntax or package import errors. 

If you *don't* see an import error message, here are some debugging steps to try:

- Airflow scans the `dags_folder` for *new* DAGs every `dag_dir_list_interval`, which defaults to 5 minutes but can be modified. Make sure this interval has passed since you added the DAG. Otherwise, you may just have to wait.
- Ensure your user has permission to see the DAGs, and that the permissions on the DAG file are correct.
- Run `airflow dags list` with the [Airflow CLI](https://airflow.apache.org/docs/apache-airflow/stable/usage-cli.html) to make sure Airflow has registered the DAG in the metastore. If the DAG shows in the list, try restarting the webserver.
- Try restarting the scheduler (if you are using the [Astronomer CLI](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart), run `astro dev stop && astro dev start`)
- If you see an error that the scheduler is not running like below, check the scheduler logs to see if something in the DAG file is causing the scheduler to crash (if you are using the Astronomer CLI, run `astro dev logs --scheduler`). Then try restarting.

    ![No Scheduler](https://assets2.astronomer.io/main/guides/debugging-dags/scheduler_not_running.png)

If you have this issue when working from an Astronomer Airflow deployment, there are a few additional things you can check:

- Ensure your Dockerfile Runtime/Astronomer Certified version matches the Airflow version of your deployment. A mismatch here can cause DAGs not to show up after they've been deployed.
- For Astronomer Certified images, ensure you are using the `onbuild` image (e.g. `FROM quay.io/astronomer/ap-airflow:2.2.2-buster-onbuild`). Images without `onbuild` will not bundle files in the `dags/` folder when deployed.
- Ensure the permissions on your local files aren't too [locked down](https://forum.astronomer.io/t/dags-arent-showing-up-in-my-astronomer-deployment-but-i-see-them-locally/146). 

### Installing Supporting Packages

As noted above, one frequent cause of DAG import errors is not having supporting packages installed in your Airflow environment. For example, any [provider packages](https://registry.astronomer.io/providers?page=1) that your DAGs use for hooks and operators must be installed separately.

How you install supporting Python or OS packages will depend on your Airflow setup. If you are working with an [Astronomer project](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart#step-3-initialize-an-airflow-project), you can add them to your `requirements.txt` and `packages.txt` files respectively, and they will be automatically installed when your Docker image builds when you deploy or start the project locally.

One thing to watch out for, especially with Python packages, is dependency conflicts. If you are running Airflow using Docker, and conflicts will cause errors when you build your image. With the Astronomer CLI, errors and warnings will be printed in your terminal when you run `astro dev start`, and you may see import errors for your DAGs in the Airflow UI if packages failed to install. In general, all packages you install should be available in your scheduler pod. You can double check they were installed successfully by exec'ing into your scheduler pod as described [here](https://www.astronomer.io/docs/cloud/stable/develop/customize-image#add-python-and-os-level-packages).

If you do have package conflicts that can't be resolved, consider splitting your DAGs into multiple Airflow deployments.

## Tasks Aren't Running

Your DAGs are deployed and visible in your Airflow UI, and you manually trigger your DAG or wait for it to be scheduled. But once your DAG run starts, your tasks don't actually run. This is a commonly encountered issue in Airflow, and the causes can be very simple, or more complex. Below are some debugging steps that will resolve the most common scenarios:

- Make sure your DAG is toggled to `Unpaused`. If your DAG is paused when you trigger it, the tasks will not be run. 

    ![Paused DAG](https://assets2.astronomer.io/main/guides/debugging-dags/paused_dag.png)

    DAGs are deployed paused by default, but you can change this behavior by updating `dags_are_paused_at_creation` to False in your Airflow config (be aware of the catchup parameter in your DAGs if you do this).

    > Note: As of Airflow 2.2, paused DAGs will be unpaused automatically if you manually trigger them.

- Ensure your DAG has a start date that is in the past. If your start date is in the future, triggering the DAG will result in a "successful" DAG run, but no tasks will actually be scheduled or run.
- If you are using a [custom timetable](https://www.astronomer.io/guides/scheduling-in-airflow), ensure that the data interval for your DAG run does not precede the DAG's start date.
- If your tasks are getting stuck in a `scheduled` or `queued` state, ensure your scheduler is running properly. If needed, restart the scheduler, or increase scheduler resources in your Airflow infrastructure.

## Tasks Have a Failure Status

Your tasks are now running, but what if some of your tasks have failed? You'll be able to see any failures in the Airflow UI by looking at the Tree View or the Graph View, where tasks will be shown as red.

![Tree View Task Failure](https://assets2.astronomer.io/main/guides/debugging-dags/tree_view_task_failure.png)

To figure out what's going on, task logs are your best resource. To access logs, click on the failed task in either the Tree View or Graph View and click the log button. 

![Get Logs](https://assets2.astronomer.io/main/guides/debugging-dags/access_logs.png)

This will take you to the logs for that task, which will have information about the error that caused the failure. 

![Error Log](https://assets2.astronomer.io/main/guides/debugging-dags/error_log.png)

For ease of debugging, it is also helpful to set up error notifications so you don't have to look at the UI to identify when failures happen. Check out [this guide](https://www.astronomer.io/guides/error-notifications-in-airflow) for details on setting up email, Slack, and custom notifications in Airflow.

## Logs Aren't Showing Up

Less commonly, when you check your task logs to debug a failure, you may not see any logs at all. On the log page in the UI, you may see a spinning wheel that goes forever, or you may just see a blank file. 

Generally, logs fail to show up when a process dies in your scheduler or worker and the communication is lost. Here are a couple of things to try to get your logs showing up again:

- In case it was a one-off issue, try rerunning the task by [clearing the task instance](https://www.astronomer.io/guides/rerunning-dags#rerunning-tasks) and see if the logs show up the second time.
- Increase your `log_fetch_timeout_sec` parameter to greater than the 5 second default. This parameter controls how long the webserver will wait for the initial handshake when fetching logs from the worker machines, and having extra time here can sometimes resolve issues.
- Increase the resources available to your workers (if using the Celery executor) or scheduler (if using the local executor).
- If you're using the Kubernetes executor, which spins up a separate pod for each task, sometimes if the task fails very quickly (e.g. in less than 15 or so seconds) the pod will be spun down before the webserver has a chance to collect the logs from the pod. If possible, you can try building in some wait time to your task depending on which operator you're using. If that isn't possible, try to diagnose what could be causing a near-immediate failure in your task. This is often related to either lack of resources (try increasing CPU/memory for the task), or an error in the task configuration.
- If you're looking at historical task failures, ensure that your logs are retained long enough. For example, the default log retention period on Astronomer is 15 days, so any logs prior to that will not be stored.
- If none of the above works, try checking your scheduler and webserver logs for any errors that might indicate why your task logs aren't showing up.

## Addressing Failures

Once you have identified the cause of any failures in your tasks, you can begin to address them. If you've made any changes to your code, make sure to redeploy (if applicable), and check the Code View in the Airflow UI to make sure your changes have been picked up by Airflow.

If you want to rerun your full DAG or certain tasks after making changes, you can easily do so with Airflow. Check out [this guide](https://www.astronomer.io/guides/rerunning-dags#rerunning-tasks) for details on how to rerun and apply backfills or catchups. 

How to address specific failures will depend heavily on the hook/operator/sensor used, and the use case. However, Airflow connections are an area that consistently cause issues in early DAG development, so we talk about those in more depth below.

### Connections

Typically, Airflow connections are needed for Airflow to talk to any external system. Most hooks and operators will expect a connection parameter to be defined. Improperly defined connections are one of the most common issues Airflow users have to debug when first working with their DAGs. Below are some tips and tricks for getting them to work:

- Check out the Airflow [managing connections documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html) to get familiar with how connections work.
- Most hooks and operators will use the `default` connection of the correct type. You can change the `default` connection to use your connection details, or define a new connection with a different name and pass that to the hook/operator.
- Consider upgrading to Airflow 2.2 so you can use the test connections feature in the UI or API. This will save you having to run your full DAG to make sure the connection works.
    ![Test Connections](https://assets2.astronomer.io/main/guides/debugging-dags/test_connections.png)
- Every hook/operator will have its own way of using a connection, and it can sometimes be tricky to figure out what parameters are needed. The [Astronomer Registry](https://registry.astronomer.io/) can be a great resource for this: many hooks and operators have documentation there on what is required for a connection.
- You can define connections using Airflow environment variables instead of adding them in the UI. Take care to not end up with the same connection defined in multiple places. If you do, the environment variable will take precedence.
