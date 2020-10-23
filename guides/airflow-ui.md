---
title: "The Airflow UI"
description: "A high-level overview of the Airflow UI"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-ui"
heroImagePath: null
tags: ["DAGs", "Airflow UI", “Basics”, “XCom”, “Tasks”, “Connections”]
---

A notable part of Apache Airflow is its built-in UI, which allows you to see the status of your jobs, their underlying code, and even some meta-data on their execution time. It'll help you both monitor and troubleshoot your workflows and, if used correctly, can make your use of Airflow that more effective. 

Since the UI isn't always the most intuitive, here's a guide that'll walk you through it. 

## Getting Started

Upon signing into the UI, you'll immediately land on the DAGs dashboard.

![dashboard](https://assets.astronomer.io/website/img/guides/dags_dashboard.png)

Your initial options:

- **On/Off Toggle** To the left of the DAG name, look for an on/off toggle that allows you to pause any DAG at any time. By default, DAGs are instanstiated as off.

- **Recent Tasks** shows a summary of the last scheduled DAG run.

- **Show Paused DAGs** at the bottom of the page can be used to hide/show DAGs that are currently turned off.

- **Links** on the right-hand side will allow you to toggle between views for that DAG (tree, gantt, etc.)

- **DAG Runs** are a history of how that DAG has run in the past.

**Note**: If a DAG has a small _i_ next to it, it means that a DAG with that name was once there, but is no longer found in the database. We'll expand on this later.

Paused DAGs can be toggled to be hidden from the UI - but we would advise against this. There's usually a reason why something is paused

![paused_dags](https://assets.astronomer.io/website/img/guides/paused_dags.png)

## Admin Panel

The Admin panel will have information regarding things that are ancillary to DAGs. Note that for now, Astronomer handles the _Pools_ and _Configuration_ views as environment variables, so they cannot be changed from the UI.

![admin](https://assets.astronomer.io/website/img/guides/admin_views.png)

### Users

Here, you'll be able to see the users that have access to your instance, and their corresponding username (email address used for login).

This view won't be helpful for much at the moment, but it will be roped into the Role Based Authentication system on Airflow's roadmap.

![users](https://assets.astronomer.io/website/img/guides/airflow_users.png)

### Connections

Airflow needs to know how to connect to your environment. `Connections` is the place to store that information - anything from hostname, to port to logins to other systems. The pipeline code you will author will reference the ‘conn_id’ of the Connection objects.

The Airflow `Variables` section can also hold that information, but storing them as Connections allows:

- Encryption on passwords and extras.
- Common JSON structure for connections below:

(**Note**: When you save a connection, expect the password field to be empty the next time you return to it. That's just Airflow encrypting the password - it does not need to be reset). 

![users](https://assets.astronomer.io/website/img/guides/airflow_connections.png) 

**Note**: Some connections will have different fields in the UI, but they can all be called from the BaseHook. For example, a Postgres connection may look like:

![postgres](https://assets.astronomer.io/website/img/guides/postgres_connection.png)

However, a Docker Registry will look like this:

![docker](https://assets.astronomer.io/website/img/guides/docker_registry.png)

However, they can both be called as such:

```python
from airflow.hooks.base_hook import BaseHook
...

hook = BaseHook.get_connection('CONNECTION_NAME').extra_dejson
# Hook now contains the information in the extras field as a JSON object
# The Connection Name is the name of the connection.
```

For more on Connections, check out this guide: [Managing Your Connections in Airflow](https://www.astronomer.io/guides/connections/).

### Variables

Variables are a generic way to store and retrieve arbitrary content or settings as a simple key value store within Airflow. Any DAG running in your Airflow instance can access, reference, or edit a Variable as a part of the workflow.

The data is stored in Airflow's underyling Postgres, so while it's not a great spot to store large amounts of data -  it is a good fit for storing configuration information, lists of external tables, or constants.

_Note_: Most of your constants and variables should be defined in code, but it's useful to have some variables or configuration items accessible and modifiable through the UI itself.

https://airflow.apache.org/concepts.html#variables
![airflow_variables](https://assets.astronomer.io/website/img/guides/airflow_variables.png)

PRO TIP: If the key contains any of the following words (`password`, `secret`, `passwd`, `authorization`, `api_key`, `apikey`, `access_token`), that particular variable will be encrypted or hidden in the UI by default. If you want it to show in clear-text, you are indeed able to configure it.

### XComs

Similar to Variables, Xcoms can be used as places to store information on the fly.

However, Variables are designed to be a place to store constants, whereas Xcoms are designed to communicate between tasks.

https://airflow.apache.org/concepts.html#xcoms

![ui_xcom](https://assets.astronomer.io/website/img/guides/ui_xcom.png)
_Various bits of metadata that have been passed back and forth between DAGs_.

**Note**: Just like Variables, only small amounts of data are meant to live in XComs.
Things can get tricky when putting data here, so Astronomer recommends staying away from them unless absolutely needed.

## Browsing Tasks

### Tree View

Clicking on an individual DAG brings out the Tree View by default. This shows a summary of the past few DAG runs, indicating its status from left to right. If any workflows are late or running behind, you'll be able to see on what exact task something failed and troubleshoot from there.

![tree_view](https://assets.astronomer.io/website/img/guides/tree_view.png)
_Each task of this DAG has succeeded for the last 25 runs._

### Graph View

The Graph View shows the actual DAG down to the task level.
![graph_view](https://assets.astronomer.io/website/img/guides/graph_view.png)

Double-clicking on an individual task offers a few options:

![task_options](https://assets.astronomer.io/website/img/guides/task_options.png)

- **Task Instance Details:**  Shows the fully rendered task - an exact summary of what the task does (attributes, values, templates, etc.)
- **Rendered:** Shows the task's metadata after it's been templated
- **Task Instances** A historical view of that particular task - times it ran successfully, failed, was skipped, etc.
- **View Log:** Brings you to Logs of that particular taskinstance.
- **Clear: ** Removes that task runs existence from Airflow's metadata. This clears all downstream tasks and runs that task and all downstream tasks again. (**This is the recommended way to re-run a task **).
- **Mark Success:** Sets a task to success. This will update the task's status in the metadata and allow downstream tasks to run.

### Code View

While the code for your pipeline is in source control, this is a quick way to get to the code that generates the DAG.

![dag_details](https://assets.astronomer.io/website/img/guides/code_view.png)

**Note:** This only covers the dag file itself, not the underlying code in the operators and plugins

### Details

This shows a summary for the past run of the DAG. There's no information that is unique to this view, but it offers a good summary.

![dag_details](https://assets.astronomer.io/website/img/guides/dag_details.png)

## Data Profiling

### Visualizing Metadata

Airflow offers a slew of metadata on individual DAG runs along with a few visualizations.

**Gantt View** is helpful for breaking down run times of individual tasks:
![gantt_view](https://assets.astronomer.io/website/img/guides/gantt_view.png)

**Landing Times** allows you to compare how DAGs have performed over time:

![landing_times](https://assets.astronomer.io/website/img/guides/landing_times.png)

## Manipulating Tasks and DAGs in Aggregate

Tasks and DAGs can also be manipulated in aggregate.
All meta-data regarding DAGs is stored in the underlying database. So, instead of having to directly query and update the meta-database, Airflow provides a UI to make changes of that nature - both at a task and DAG level.

### Tasks

The "Task Instances" panel is where you can clear out, re-run, or delete any particular tasks within a DAG or across all DAG runs.

**If you want to re-run tasks**:

Tasks will NOT automatically re-run if the DAG has failed (which you'll notice by a red circle at the top of tree view). Let's say one of your DAGs stopped because of a database shutdown, and a task within a DAG fails. Assuming you'd want to re-run the DAG from where it left off, you can do either of the following:

1. Browse > Task Instances, filter for and select the failed task(s), and Delete (this is essentially the same as clearing individual tasks in the DAG graph or tree view).

1. Browse > DAG Runs, filter for and select the failed DAG(s), and set state to 'running.'

This will automatically trigger a DAG re-run start|ing with the first unsuccessful task(s).

**If you want to delete task records:**

If you're running a DAG but intentionally stopped it (turned it "off") during execution, and want to permanently clear remaining tasks, you can delete all the records relevant to the DAG id in the 'Task Instances' panel as well.

_Note_: The task and DAG status field on your main dashboard may take a bit to reflect these changes.

![delete_task_instances](https://assets.astronomer.io/website/img/guides/delete_task_instances.png)

### DAGs

The same can be done for DAGs from **Browse-> DAG Runs**. This can be particularly helpful when migrating databases or re-running all history for a job with just a small change.

![browse_dag_runs](https://assets.astronomer.io/website/img/guides/browse_dag_runs.png)

### SLA Misses.

SLA misses can also be viewed at a task level.

![delete_task_instances](https://assets.astronomer.io/website/img/guides/sla_misses.png)
