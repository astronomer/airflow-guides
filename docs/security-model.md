---
title: "Security Model"
description: "The Astronomer Security Model"
date: 2018-10-12T00:00:00.000Z
slug: "security-model"
menu: ["root"]
position: [4]
---

Astronomer allows you to dictate who has access to specific Airflow deployments.

We do this through a concept we call **Workspaces**.

Workspaces are conceptually similar to Teams, and are collections of Airflow
deployments that only specific users have access to, allowing you to ensure that
only those you want viewing your production deployments are capable of doing so.

In an upcoming release, we'll include Airflow 1.10 features, which will include
[role-based access control (RBAC)](https://medium.com/datareply/apache-airflow-1-10-0-released-highlights-6bbe7a37a8e1).

To learn more about Workspaces and see screenshots of what their user management
capability looks like, check out the [Platform Overview](https://astronomer.io/docs/overview).

## Cloud Edition

Astronomer Cloud is hosted on infrastructure we control. We run a single NAT
that all internet bound traffic flows through. We don't persist any of your
data, and all computation runs in short-lived containers that terminate after
the task is finished.

If you're interested in having a dedicated NAT or IP, you'll have to use our
Enterprise product, which is installed into your Kubernetes.

## Enterprise Edition

Astronomer Enterprise is deployed in your cloud, on your Kubernetes. As such,
it should comply with your internal security specifications.
