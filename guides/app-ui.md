---
title: "Workspace and User Management with Astronomer"
description: "A walkthrough of our app's UI features for user managementprett."
date: 2018-07-17T00:00:00.000Z
slug: "app-ui"
heroImagePath: null
tags: ["Astronomer", "admin-docs", "Airflow"]
---

# Overview

To satisfy Astronomer's goal to improve Airflow usability, we have built a custom UI that makes user access and deployment management dead simple. In this guide, we'll walk through the specific components of the Astronomer UI and discuss the design principles that led to their creation.

## Getting Started

[Once you've created an account and authenticated in](https://astronomer.io/guides/getting-started-with-new-cloud/), you'll land on a dashboard that gives you an  overview of your Workspaces. We'll call this the `Account Dashboard`:

![Account Dashboard](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/account_dashboard.png)

You can think of your Workspaces the same way you'd think of teams- they're just collections of Airflow clusters that specific user groups have access to. From this dashboard, you can spin up new Workspaces and get a high-level overview of active Airflow deployments in your current workspaces. 

Once you click into a workspace, you'll land on another dashboard that we'll call the `Workspace Dashboard`:

![Workspace Dashboard](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/workspace_dashboard.png)

Here, you have a high-level overview of all of the active Airflow deployments you have running in that given workspace. In this case, we only have one cluster activated. From this screen, you can create new Airflow deployments, manage user access to the workspace, and generate tokens for CI/CD systems via service accounts.

## User Management

If you navigate over to the `Users` tab of your Workspace Dashboard, you'll be able to see who has access to the Workspace and invite other members of your organization to access the Airflow instances in that Workspace.

![Users](https://s3.amazonaws.com/astronomer-cdn/website/img/guides/user_dashboard.png)

Note that, in an upcoming release, you'll be able to designate DAG-level permissions for each of the users who has access to the Workspace.

## Service Accounts

If you're interested in integrating your deployment process into your CI/CD system, [check out this guide](https://astronomer.io/guides/deploying-dags-with-cicd/). Through the `Services Account` tab in your Workspace Dashboard, you can generate API keys that you can plug into your CI/CD secrets manager. Creating Service Accounts at the Workspace level allows you to customize how your deployment pipeline works- check out [this video](https://www.youtube.com/watch?time_continue=2&v=8h9lXzGa4sQ) for a more detailed walkthrough of that process.

