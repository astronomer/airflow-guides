---
title: Apache Airflow Hooks Overview
sidebar: platform_sidebar
---

Along with Operators, Hooks are key to extending capabilities with airflow while keeping your DAGs clean and simple.

A **hook** is an object that embodies a connection to a remote server, service, or platform.

Hooks are importers that dynamically load classes and modules from their parents. They are meant as an interface to interact with external systems.

Check out our [Sources and Destinations](../sources-and-destinations.html) doc to see our hook development roadmap.