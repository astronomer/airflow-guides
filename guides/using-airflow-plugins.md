---
title: "Using Apache Airflow Plugins"
description: "A crash-course in using Airflow Plugins."
date: 2018-05-21T00:00:00.000Z
slug: "using-airflow-plugins"
heroImagePath: "https://assets.astronomer.io/website/img/guides/bestpractices.png"
tags: ["Airflow", "Best Practices", "Plugins"]
---

## Plugins

Plugins are powerful components in Airflow used to customize your installation. This section covers plugin capabilities and provides some examples to show the flexibility they provide.

### Hooks & Operators

It is no longer considered best practice to use the Airflow Plugins mechanism for hooks, operators or sensors. Please see [this](https://www.astronomer.io/guides/airflow-importing-custom-hooks-operators) guide on the best way to implement these.

### Macros

[Macros](https://airflow.apache.org/docs/stable/macros-ref.html) are used to pass dynamic information into task instances at runtime via templating.

A current limitation of Airflow is that every global variable or top-level method in a DAG file is interpreted every cycle during the DAG processing loop on the scheduler. While the loop execution time can vary from seconds to minutes (depending on configuration, external connectivity, number of DAGs, etc), the point remains that there is certain code that the vast majority of code should only be interpreted in a task at execution time.

Macros are a tool in Airflow that provide a solution to this problem. Macros extend Airflow's [templating](https://airflow.apache.org/tutorial.html#templating-with-jinja) capabilities to allow you to offload runtime tasks to the executor as opposed to the scheduler loop. Some examples of macros might include:

- timestamp formatting of last or next execution for incremental ETL
- decryption of a key used for authentication to an external system
- accessing custom user-defined params

**Note:** a template will always return a string.
### Blueprints and Views

The [blueprints](http://flask.pocoo.org/docs/0.12/blueprints/) and [views](http://flask.pocoo.org/docs/0.12/views/) components in Airflow are extensions of blueprints and views in the Flask web app framework. Developers have extended the Airflow API to include things such as triggering a DAG run remotely, adding new connections or modifying [Airflow variables](https://pythonhosted.org/airflow/concepts.html#variables). You can extend this to build an entire web app which sits alongside the Airflow webserver. One example of this is a plugin that allows analysts to input SQL through a web UI to be run on a scheduled interval.

### Menu Links

[Menu Links](https://github.com/flask-admin/flask-admin/blob/06aebf078574cbbe70b2691fc8a41f234f321962/flask_admin/menu.py#L129 ) allow developers to add custom links to the navigation menu in Airflow.

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
