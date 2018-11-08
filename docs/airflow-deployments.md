---
title: "Airflow Deployments"
date: 2018-10-12T00:00:00.000Z
slug: "airflow-deployments"
menu: ["root"]
position: [5]
---

In the context of Astronomer, the term _Airflow Deployment_ is used to describe an instance of Airflow that you've spun up either via our [app UI](ttps://astronomer.io/docs/overview) or [command line](https://astronomer.io/docs/cli-getting-started). Within your Astronomer Workspace, you can create one or more Airflow deployments. Under the hood, each deployment gets its own Kubernetes namespace and has a set isolated resources reserved for itself.

You will soon be able to control specific resource allocations and choose your executor (local or celery) directly from our app's UI. This functionality will allow you to easily provision additional resources for specific Airflow deployments as you scale up.

