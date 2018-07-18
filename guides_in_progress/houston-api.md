---
layout: page
title: Astronomer Houston API (GraphQL)
permalink: /guides/houston-api/
hide: true
---

# Houston API

The [Houston GraphQL API](https://github.com/astronomerio/houston-api)
is the source of truth for the Astronomer Platform.
[Playground](https://houston.astronomer.win/playground).

Queries:

* Clusters - Fetches one or more deployments based on input
* ClusterConfig - Fetches config needed to create a module deployment

Mutations:

* createToken - Verify a user's credentials and issues a token if valid
* createUser - Creates a new user
* updateUser - Update an existing user
* createCluster - Creates a new Airflow Cluster
* updateCluster - Updates an Airflow cluster
* deleteCluster - Deletes an Airflow Cluster
