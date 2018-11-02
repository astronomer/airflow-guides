---
title: "Security Model"
description: "The Astronomer Security Model"
date: 2018-10-12T00:00:00.000Z
slug: "security-model"
menu: ["root"]
position: [4]
---


## Cloud Security

Since Astronomer Cloud is hosted on our infrastructure, we often get questions about how data is received and processed by our platform. In Cloud, we run a single NAT that all internet bound traffic flows through. We don't persist any of your data and all computation runs in short lived containers that die after the task is finished. This ensures that we don't keep any of the data that you run through your Airflow DAGs.

If you're interested in having a dedicated NAT, you'll have to use our Enterprise product, which is hosted entirely on your infrastructure.

## Enterprise Security

Astronomer Enterprise is deployed and hosted in your cloud via Kubernetes, so it complies to your internal security specifications.

## User Access

Our app allows you to dictate who has access to specific Airflow deployments. We do this via the concept of Workspaces. Workspaces, which are conceptually similar to Teams, are collections of Airflow deployments that only specific users have access to, allowing you to ensure that only those you want viewing your production deployments are capable of doing so. In an upcoming release, we'll rope in Airflow 1.10 features, which will include [role-based access control (RBAC)](https://medium.com/datareply/apache-airflow-1-10-0-released-highlights-6bbe7a37a8e1). To read more about Workspaces and see screenshots of what their user management capability looks like, check out our [Platform Overview doc](https://astronomer.io/docs/overview).

