---
title: "The Airflow UI"
description: "A high-level overview of the Airflow UI"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-ui"
heroImagePath: null
tags: ["DAGs", "Airflow UI", "Basics", "XCom", "Tasks", "Connections"]
---

## Overview

A notable feature of Apache Airflow is the [UI](https://airflow.apache.org/docs/apache-airflow/stable/ui.html#), which provides insights into your DAGs and DAG Runs. The UI is a useful tool for understanding, monitoring, and troubleshooting your pipelines.

In this guide, we'll walk through an overview of some of the most useful features and visualizations in the Airflow UI. Each section of the guide corresponds to one of the tabs at the top of the Airflow UI. If you're not already using Airflow and want to get it up and running to follow along, check out the [Astronomer CLI](https://docs.astronomer.io/astro/install-cli) to quickly run Airflow on your local machine. 

> Note: This guide focuses on the Airflow 2 UI, which was significantly redesigned compared to previous Airflow versions. If you haven't upgraded yet, check out this guide on [getting started with Airflow 2.0](https://www.astronomer.io/guides/get-started-airflow-2).

## DAGs

The DAGs view is the landing page when you sign in to Airflow. It shows a list of all your DAGs, the status of recent DAG Runs and tasks, the time of the last DAG Run, and basic metadata about the DAG like the owner and the schedule.

![DAGs View](https://assets2.astronomer.io/main/guides/airflow-ui/ui_dags.png)

> Note: All screenshots in this guide were taken from an [Astronomer Certified](https://docs.astronomer.io/software/image-architecture) Airflow image. Other than the additional `Astronomer` tab and some modified colors, the UI is the same as that of OSS Airflow. 

From the DAGs view you can:

- Pause/unpause a DAG with the toggle to the left of the DAG name
- Filter the list of DAGs to show active, paused, or all DAGs
- Trigger, refresh, or delete a DAG with the buttons in the Actions section
- Navigate quickly to other DAG-specific pages from the Links section

To drill down on a specific DAG, you can click on its name or use one of the links. This will give you access to the views described in the following sections.

### Graph View

The Graph View shows a visualization of the tasks and dependencies in your DAG and their current status for a specific DAG Run. This view is particularly useful when reviewing and developing a DAG. When running the DAG, you can toggle the Auto-refresh button to `on` to see the status of the tasks update in real time.

![Graph View](https://assets2.astronomer.io/main/guides/airflow-ui/ui_graph.png)

Clicking on a specific task in the graph will give you links to additional views and actions you can take on that task instance.

![Graph Actions](https://assets2.astronomer.io/main/guides/airflow-ui/ui_graph_actions.png)

Specifically, the additional views available are:

- **Instance Details:**  Shows the fully rendered task - an exact summary of what the task does (attributes, values, templates, etc.).
- **Rendered:** Shows the task's metadata after it has been templated.
- **Log:** Shows the logs of that particular `TaskInstance`.
- **All Instances:** Shows a historical view of task instances and statuses for that particular task.
- **Filter Upstream:** Updates the Graph View to show only the task selected and any upstream tasks.

The actions available for the task instance are:

- **Run**: Manually runs a specific task in the DAG. You have the ability to ignore dependencies and the current task state when you do this.
- **Clear:** Removes that task instance from the metadata database. This is one way of manually re-running a task (and any downstream tasks, if you choose). You can choose to also clear upstream or downstream tasks in the same DAG, or past or future task instances of that task.
- **Mark Failed:** Changes the task's status to failed. This will update the metadata database and stop downstream tasks from running if that is how you have defined dependencies in your DAG. You have additional capabilities for marking past and future task instances as failed and for marking upstream or downstream tasks as failed at the same time.
- **Mark Success:** Changes the task's status to success. This will update the metadata database and allow downstream tasks to run if that is how you have defined dependencies in your DAG. You have additional capabilities for marking past and future task instances as successful and for marking upstream or downstream tasks as successful at the same time.

### Tree View

The Tree View shows a tree representation of the DAG and its tasks across time. Each column represents a DAG Run and each square is a task instance in that DAG Run. Task instances are color-coded according to their status. DAG Runs with a black border represent scheduled runs, whereas DAG Runs with no border are manually triggered.

![Tree View](https://assets2.astronomer.io/main/guides/airflow-ui/ui_tree.png)

Clicking on a specific task instance in the tree will give you links to the same additional views and actions described in the Graph View section above.

### Calendar View

The Calendar View is new as of Airflow 2.1. It shows the state of DAG Runs overlaid on a calendar. States are represented by color. If there were multiple DAG Runs on the same day that had different states (e.g. one failed, one succeeded), the color will be a gradient between green (success) and red (failed).

![Calendar View](https://assets2.astronomer.io/main/guides/airflow-ui/ui_calendar.png)

### Code View

The Code View shows the code that is used to generate the DAG. While your code should live in source control, the Code View can be a useful way of gaining quick insight into what is going on in the DAG. Note that code for the DAG cannot be edited directly in the UI.

![Code View](https://assets2.astronomer.io/main/guides/airflow-ui/ui_code.png)

Also of note: This view shows code only from the file that generated the DAG. It does not show any code that may be imported in the DAG, such as custom hooks or operators or code in your `/include` directory.

### Additional DAG Views

There are a couple of additional DAG views that we won't cover in depth here, but are still good to be aware of:

- **Task Duration:** Shows a line graph of the duration of each task over time.
- **Task Tries:** Shows a line graph of the number of tries for each task in a DAG Run over time.
- **Landing Times:** Shows a line graph of the time of day each task started over time.
- **Gantt:** Shows a Gantt chart with the duration of each task for the chosen DAG Run.

## Security

The Security tab links to multiple pages, including List Users and List Roles, that can be used to review and manage Airflow RBAC. For more information on working with RBAC, check out the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/1.10.12/security.html?highlight=ldap).

![Security](https://assets2.astronomer.io/main/guides/airflow-ui/ui_security_menu.png)

Note that if you are running Airflow on Astronomer, the Astronomer RBAC will extend into Airflow and take precedence (i.e. there is no need for you to use Airflow RBAC in addition to Astronomer RBAC). Astronomer RBAC can be managed from the Astronomer UI, so the Security tab may be less relevant for Astronomer users.

## Browse

The Browse tab links to multiple pages that provide additional insight into and control over your DAG Runs and Task Instances for all DAGs in one place. 

![Browse](https://assets2.astronomer.io/main/guides/airflow-ui/ui_browse_menu.png)

The DAG Runs and Task Instances (shown in the screenshot below) pages are the easiest way to view and manipulate these objects in aggregate. If you need to re-run tasks in multiple DAG Runs, you can do so from this page by selecting all relevant tasks and clearing their status. 

![Task Instance](https://assets2.astronomer.io/main/guides/airflow-ui/ui_task_instance.png)

Other views in the Browse tab include: 

- **Jobs:** Shows a list of all jobs that have been completed. This includes executed tasks as well as scheduler jobs.
- **Audit Logs:** Shows a list of events that have occurred in your Airflow environment that can be used for auditing purposes.
- **Task Reschedules:** Shows a list of all tasks that have been rescheduled.
- **SLA Misses:** Shows any task instances that have missed their SLAs.
- **DAG Dependencies:** Shows a graphical representation of any cross-DAG dependencies in your Airflow environment. 


## Admin

The Admin tab links to pages for content related to Airflow administration (i.e. not specific to any particular DAG). Many of these pages can be used to both view and modify parts of your Airflow environment.

![Admin](https://assets2.astronomer.io/main/guides/airflow-ui/ui_admin_menu.png)

For example, the Connections page shows all Airflow connections stored in your environment. You can click on the `+` to add a new connection. For more information, check out our [guide on connections](https://www.astronomer.io/guides/connections/).

![Connections](https://assets2.astronomer.io/main/guides/airflow-ui/ui_connections.png)

Similarly, the XComs page shows a list of all XComs stored in the metadata database and allows you to easily delete them.

![XCom](https://assets2.astronomer.io/main/guides/airflow-ui/ui_xcoms.png)

Other pages in the Admin tab include:

- **Variables:** View and manage [Airflow variables](https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html).
- **Configuration:** View the contents of your `airflow.cfg` file. Note that this can be disabled by your Airflow admin for security reasons.
- **Plugins:** View any [Airflow plugins](https://airflow.apache.org/docs/apache-airflow/stable/plugins.html) defined in your environment.
- **Pools:** View and manage [Airflow pools](https://airflow.apache.org/docs/apache-airflow/stable/concepts/pools.html).


## Docs

The Docs tab provides links out to external Airflow resources including:

- [Airflow documentation](http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/latest/)
- [The Airflow website](https://airflow.apache.org/)
- [The Airflow GitHub repo](https://github.com/apache/airflow)
- The REST API Swagger and and Redoc documentation

![Docs](https://assets2.astronomer.io/main/guides/airflow-ui/ui_docs_menu.png)

## Conclusion

This guide provided a basic overview of some of the most commonly used features of the Airflow UI. It is not meant to be comprehensive, and we highly recommend diving in yourself to discover everything the Airflow UI can offer. 

The Airflow community is consistently working on improvements to the UI to provide a better user experience and additional functionality. Make sure you upgrade your Airflow environment frequently to ensure you are taking advantage of Airflow UI updates as they are released. 
