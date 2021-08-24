---
title: "The Airflow UI"
description: "A high-level overview of the Airflow UI"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-ui"
heroImagePath: null
tags: ["DAGs", "Airflow UI", "Basics", "XCom", "Tasks", "Connections"]
---

A notable feature of Apache Airflow is its UI, which provides insights into your DAGs and DAG Runs. The UI a useful tool for understanding, monitoring, and troubleshooting your pipelines.

In this guide, we'll walk through an overview of some of the most useful features and visualizations in the Airflow UI. In general, sections in the guide correspond to the tab at the top of the Airflow UI. If you're not already using Airflow and want to get it up and running to follow along, check out the [Astronomer CLI](https://www.astronomer.io/docs/enterprise/v0.25/develop/cli-quickstart) to quickly run Airflow on your local machine. 

> Note: This guide focuses on the Airflow 2 UI, which got a significant refresh over previous Airflow versions. If you haven't upgraded yet, check out this guide on [getting started with Airflow 2.0](https://www.astronomer.io/guides/get-started-airflow-2).

## DAGs

The DAGs view is the landing page when you sign in to Airflow. It shows a list of all your DAGs, the status of recent DAG Runs and tasks, the time of the last DAG Run, and basic metadata about the DAG like the owner and the schedule.

![dashboard](https://assets.astronomer.io/website/img/guides/dags_dashboard.png)

From the DAGs view you can:

 - Pause/unpause a DAG with the toggle to the left of the DAG name
 - Filter the list of DAGs shown to active, paused, or all DAGs
 - Trigger, refresh, or delete a DAG with the buttons in the Actions section
 - Navigate quickly to other DAG-specific pages from the Links section

To drill down on a specific DAG, you can click on its name or use one of the Links. This will give you access to the views described in the following sections.

### Graph View
The graph view shows a visualization of the tasks and dependencies in your DAG and their current status for a specific DAG Run. This view is particularly useful when reviewing and developing a DAG as it allows you to quickly see what is happening in the DAG.

Clicking on a specific task in the graph will give you links to additional views and actions you can take on that task instance.

Specifically, the additional views available are:

- **Instance Details:**  Shows the fully rendered task - an exact summary of what the task does (attributes, values, templates, etc.).
- **Rendered:** Shows the task's metadata after it has been templated.
- **Log:** Shows the logs of that particular `TaskInstance`.
- **All Instances:** Shows a historical view of task instances and statuses for that particular task.
- **Filter Upstream:** Updates the Graph View to show only the task selected and any upstream tasks.

The actions available for the task instance are:
- **Run**: Manually runs a specific task in the DAG. You have the ability to ignoring dependencies and the current task state when you do this.
- **Clear**: Removes that task run from the metadata database. This is one way of manually re-running a task (and any downstream tasks, if you choose). You can choose to also clear upstream or downstream tasks, or past or future task runs.
- **Mark Failed:** Changes the task's status to failed. This will update the metadata database and stop downstream tasks from running if that is how you have defined your DAG. You have additional capabilities for marking past and future task instances as failed and for marking upstream or downstream tasks as failed at the same time.
- **Mark Success:** Changes the task's status to success. This will update the metadata database and allow downstream tasks to run if that is how you have defined your DAG. You have additional capabilities for marking past and future task instances as successful and for marking upstream or downstream tasks as successful at the same time.

### Tree View

The tree view shows a tree representation of the DAG and its tasks across time. Each column represents a DAG Run and each square is a task instance in that DAG Run. Task instances are color-coded according to their status. DAG Runs with a black border represent scheduled runs, whereas DAG Runs with no border are manually triggered.

Clicking on a specific task instance in the tree will give you links to the same additional views and actions described in the graph view section above.

### Calendar View

The calendar view is new as of Airflow 2.1. It shows the state of DAG runs overlaid on a calendar. States are represented by color. If there were multiple DAG runs on the same day that had different states (e.g. one failed, one success), the color will be a gradient between green (success) and red (failed).

### Code View

The code view shows the code that is used to generate the DAG. While your code should live in source control, the code view can be a useful way of gaining quick insight into what is going on in the DAG. Note that code for the DAG cannot be edited directly in the UI.

![dag_details](https://assets.astronomer.io/website/img/guides/code_view.png)

Also note, this view only shows code from the file that generated the DAG; it does not show any code that may be imported in the DAG, such as custom hooks or operators, or code in your `/include` directory.

### Additional DAG Views

There are a couple of additional DAG views that we don't cover in depth here, but are still good to be aware of:

 - **Task Duration:** Shows a line graph of the duration of each task over time.
 - **Task Tries:** Shows a line graph of the number of each task tries in a DAG Run over time.
 - **Landing Times:** Shows a line graph of the time of day each task started over time.
 - **Gantt:**: Shows a Gantt chart with the duration of each task for the chosen DAG Run.

## Security

The Security tab links to multiple pages, including List Users and List Roles, that can be used to review and manage Airflow RBAC. For more information on working with RBAC in Airflow, check out the [documentation](https://airflow.apache.org/docs/apache-airflow/1.10.12/security.html?highlight=ldap).

Note that if you are running Airflow on Astronomer, the Astronomer RBAC will extend into Airflow and take precedence (i.e. there is no need for you to use Airflow RBAC in addition). Astronomer RBAC can be managed from the Astronomer UI, and 

## Browse



## Admin

The Admin panel will have information regarding things that are ancillary to DAGs. Note that for now, Astronomer handles the _Pools_ and _Configuration_ views as environment variables, so they cannot be changed from the UI.

![admin](https://assets.astronomer.io/website/img/guides/admin_views.png)



### Connections

Airflow needs to know how to connect to your environment. `Connections` is the place to store that information - anything from hostname, to port to logins to other systems. The pipeline code you will author will reference the `conn_id` of the Connection objects.

The Airflow `Variables` section can also hold that information, but storing them as `Connections` allows:

- Encryption on passwords and extras.
- Common JSON structure for connections below:

**Note**: When you save a connection, expect the password field to be empty the next time you return to it. That's just Airflow encrypting the password - it does not need to be reset.

![users](https://assets.astronomer.io/website/img/guides/airflow_connections.png)

**Note**: Some connections will have different fields in the UI, but they can all be called from the [BaseHook](https://registry.astronomer.io/providers/apache-airflow/modules/basehook). For example, a Postgres connection may look like:

![postgres](https://assets.astronomer.io/website/img/guides/postgres_connection.png)

However, a Docker Registry will look like this:

![docker](https://assets.astronomer.io/website/img/guides/docker_registry.png)

However, they can both be called in the same manner:

```python
from airflow.hooks.base_hook import BaseHook
...

hook = BaseHook.get_connection('CONNECTION_NAME').extra_dejson
# Hook now contains the information in the extras field as a JSON object
# The Connection Name is the name of the connection.
```

For more on `Connections`, check out this guide: [Managing Your Connections in Airflow](https://www.astronomer.io/guides/connections/).

### Variables

`Variables` are a generic way to store and retrieve arbitrary content or settings as a simple key value store within Airflow. Any DAG running in your Airflow instance can access, reference, or edit a `Variable` as a part of the workflow.

The data is stored in Airflow's underlying Postgres database, so while it's not a great spot to store large amounts of data it is a good fit for storing configuration information, lists of external tables, or constants.

**Note**: Most of your constants and variables should be defined in code, but it's useful to have some variables or configuration items accessible and modifiable through the UI itself.

For more information on `Variables`, visit the [Airflow documentation](https://airflow.apache.org/concepts.html#variables)

![airflow_variables](https://assets.astronomer.io/website/img/guides/airflow_variables.png)

> **PRO TIP**: If the key contains any of the following words (`password`, `secret`, `passwd`, `authorization`, `api_key`, `apikey`, `access_token`), that particular variable will be encrypted or hidden in the UI by default. If you want it to show in clear-text, you are indeed able to configure it.

### XComs

Similar to `Variables`, `XComs` can be used as places to store information on the fly.

However, `Variables` are designed to be a place to store constants, whereas `XComs` are designed to communicate between tasks.

For more information on `XComs`, visit the [Airflow documentation](https://airflow.apache.org/concepts.html#xcoms)

![ui_xcom](https://assets.astronomer.io/website/img/guides/ui_xcom.png)
_Various bits of metadata that have been passed back and forth between DAGs_.

**Note**: Just like `Variables`, only small amounts of data are meant to live in `XComs`.
Things can get tricky when putting data here, so Astronomer recommends staying away from them unless absolutely needed.

## Browsing Tasks







## Manipulating Tasks and DAGs in Aggregate

Tasks and DAGs can also be manipulated in aggregate.
All metadata regarding DAGs is stored in the underlying database. So, instead of having to directly query and update the metadata database, Airflow provides a UI to make changes of that nature - both at a task and DAG level.

### Tasks

The "Task Instances" panel is where you can clear out, re-run, or delete any particular tasks within a DAG or across all DAG runs.

**If you want to re-run tasks:**

Tasks will _NOT_ automatically re-run if the DAG has failed (which you'll notice by a red circle at the top of Tree View). Let's say one of your DAGs stopped because of a database shutdown, and a task within a DAG fails. Assuming you'd want to re-run the DAG from where it left off, you can do either of the following:

1. _Browse > Task Instances_, filter for and select the failed task(s), and select "Delete" (this is essentially the same as clearing individual tasks in the DAG Graph or Tree View).

1. _Browse > DAG Runs_, filter for and select the failed DAG(s), and set state to 'running.'

This will automatically trigger a DAG re-run start|ing with the first unsuccessful task(s).

**If you want to delete task records:**

If you're running a DAG but intentionally stopped it (turned it "off") during execution, and want to permanently clear remaining tasks, you can delete all the records relevant to the DAG id in the 'Task Instances' panel as well.

**Note**: The task and DAG status field on your main dashboard may take a bit to reflect these changes.

![delete_task_instances](https://assets.astronomer.io/website/img/guides/delete_task_instances.png)


## Docs

