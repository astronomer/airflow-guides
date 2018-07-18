---
layout: page
title: Astronomer User System
permalink: /guides/user-system/
hide: true
---

# Astronomer User System

The first user created will have the role `platform.owner` and will
have access to the Grafana dashboards, etc.

Every user, when created, will have start with a personal workspace
with `workspace.owner` that they can create Airflow Cluster deployments into.

They can also add other users to their workspace. All workspace
users will be owners and have full control over the Airflow
instances within.

NOTE: Additional access control granularity will be introduced in
0.4. Please reference the [RBAC Guide](/guides/rbac/).
