---
title: Airflow Best Practices Guide
sidebar: platform_sidebar
---

# Airflow Best Practices and Development Guide

## Introduction

One of the best practices you can adopt in regards to Airflow is to develop integrations in the form of plugins.

Developing with the [Airflow plugins system][0] allows you to keep core integration features separate from workflows (DAGs). This will support your engineering team to actively develop and version plugins while analysts leverage these plugins in their workflows. With this practice, your workflows will be clean and mostly configuration details as opposed to implementation logic.

## Plugins

Plugins are very powerful components in Airflow. This section covers plugin capabilities and provides some examples to show the flexibility they provide.

### Hooks

[Hooks][3] define how your plugin will interact with outside resources. This outside service may be an external API, database, web service, file server or just about anything else. A hook allows you to connect to this resource and perform a well defined set of actions against that external system.

### Operators

[Operators][4] are the workhorses in Airflow. They extend how you can interact with an external system.

At a high-level there are three types of operators:

1. **Sensor operator** - wait for and detect some condition in a source system.
1. **Transfer operator** - move data from one system to another.
1. **Action operator** - perform some action locally or make a call to an external system to perform some action.

Transfer operators and action operators inherit from [BaseOperator][6], while sensor operators inherit from [BaseSensorOperator][5].

### Macros

[Macros][2] are used to pass dynamic information into task instances at runtime via templating.

A current limitation of Airflow is that every global variable or top-level method in a DAG file is interpreted every cycle during the DAG processing loop on the scheduler. While the loop execution time can vary from seconds to minutes (depending on configuration, external connectivity, number of DAGs, etc), the point remains that there is certain code that the vast majority of code should only be interpreted in a task at execution time.

Macros are a tool in Airflow that provide a solution to this problem. Macros extend Airflow's [templating][13] capabilities to allow you to offload runtime tasks to the executor as opposed to the scheduler loop. Some examples of macros might include:

- timestamp formatting of last or next execution for incremental ETL
- decryption of a key used for authentication to an external system
- accessing custom user-defined params

### Blueprints and Views

The [blueprints][7] and [views][8] components in Airflow are extensions of blueprints and views in the Flask web app framework. Developers have extended the Airflow API to include things such as triggering a DAG run remotely, adding new connections or modifying [Airflow variables][9]. You can extend this to build an entire web app which sits alongside the Airflow webserver. One example of this is a plugin that allows analysts to input SQL through a web UI to be run on a scheduled interval.

### Menu Links

[Menu Links][1] allow developers to add custom links to the navigation menu in Airflow.

Airflow is a powerful tool that lives at the intersection of developers, analysts and many other jobs in your organization. Because of this, the Airflow webserver is customizable to meet a wide variety of use cases. With menu links, you can easily provide supporting resources to anyone who might access your Airflow instance.

For example, you may want to modify the Airflow webserver to have two menu link categories where each item is a link, like so:

- Developer
  - Plugins repository
  - CI/CD system
- Analyst
  - Organization-specific Domino install
  - CI/CD system
  - AI Management systems

Doing this provides each user access to the context they need when using an Airflow instance.

## Additional Information

### Example Plugin Directory Structure

Plugins ship as Python modules but there are a few tricks to keeping the project structure clean.

We recommend breaking out each plugin component type into a sub module that will house a file per component. This will allow for more simple upstreaming into [apache/incubator-airflow][10] at a later date.

For simplicity, we choose to put the AirflowPlugin class instantiation inside of the top level `__init__.py`. Just be aware of this when looking for where the the plugin entry point.

For example:

```
example_plugin/
├── hooks
│   ├── __init__.py
│   └── example_hook.py
├── macros
│   ├── __init__.py
│   └── example_macro.py
├── menu_links
│   ├── __init__.py
│   └── example_links.py
├── operators
│   ├── __init__.py
│   └── example_operator.py
├── README.md
└── __init__.py  <--- Your AirflowPlugin class instantiation
```

If you are looking for Plugin inspiration or want to see if a solution to your problem already exists, visit the [Airflow-Plugins][11] GitHub organization that is being actively maintained by [Astronomer][12].

### BaseOperator.execute()

Overriding [the execute() method][14] in a class that extends BaseOperator will define the code that gets run on task instantiation.

### Connection Pools

[Connection pools][16] allow multiple tasks to share a connection limit for a given resource.  This can be used as a parallelism constraint, but more importantly it's useful to limit the amount of connections to a resource like a database or API.  For instance, pools can be used to prevent Redshift from getting overloaded when you need to run thousands of tasks but want to cap the number of concurrent tasks across tasks across all DAGs to dozens.

### XComs

[XComs][15] are a great way to share information between tasks in your workflow, but they should not be used to store (or pass) large amounts of data such as batch data in an ETL job. The reason for this is that XComs are stored in the Airflow metadata database and using XComs to stream data through results in unnecessary bloat on the database over time. An alternative is to write the batch data or larger datasets to a block storage system, mounted volume, etc.

### More Information

A good resource for general best practices on Airflow is Gerard Toonstra's site [ETL best practices with Airflow][17].

The document [Common Pitfalls][18] from the official Airflow Confluence wiki also provides several useful bits of advice for common challenges.

[0]: https://airflow.apache.org/plugins.html "Airflow Plugins System"
[1]: https://github.com/flask-admin/flask-admin/blob/06aebf078574cbbe70b2691fc8a41f234f321962/flask_admin/menu.py#L129 "MenuLinks"
[2]: https://airflow.apache.org/code.html#macros "Airflow Macros"
[3]: https://airflow.apache.org/code.html?highlight=operators#hooks "Airflow Hooks"
[4]: https://airflow.apache.org/code.html?highlight=operators "Airflow Operators"
[5]: https://pythonhosted.org/airflow/code.html#basesensoroperator "Base Sensor Operator"
[6]: https://pythonhosted.org/airflow/code.html#baseoperator "Base Operator"
[7]: http://flask.pocoo.org/docs/0.12/blueprints/ "Flask Blueprints"
[8]: http://flask.pocoo.org/docs/0.12/views/ "Flask Views"
[9]: https://pythonhosted.org/airflow/concepts.html#variables "Airflow Variables"
[10]: https://github.com/apache/incubator-airflow "Apache incubator-airflow"
[11]: https://github.com/airflow-plugins "Airflow Plugin Github Org"
[12]: https://github.com/astronomerio "Astronomer Github"
[13]: https://airflow.apache.org/tutorial.html#templating-with-jinja "Airflow Templating System"
[14]: https://github.com/apache/incubator-airflow/blob/e76cda0ff5c9dfdbec7a9d199884d359cdf6dbbb/airflow/models.py#L2463 "Execute Entry Point"
[15]: https://airflow.incubator.apache.org/concepts.html#xcoms "XComs"
[16]: https://airflow.apache.org/concepts.html#pools "Connection pools"
[17]: https://gtoonstra.github.io/etl-with-airflow/ "ETL best practices with Airflow"
[18]: https://cwiki.apache.org/confluence/display/AIRFLOW/Common+Pitfalls "Common Pitfalls"