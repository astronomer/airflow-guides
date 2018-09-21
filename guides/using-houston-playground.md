---
title: "Using Houston Playground"
description: "How to write queries against the Houston playground directly"
date: 2018-09-21T00:00:00.000Z
slug: "houston-playground"
heroImagePath: null
tags: ["astronomer, houston, api, playground"]
---

## Houston Playground
The [houston-api](https://github.com/astronomerio/houston-api) is the source of truth across the entire Astronomer Enterprise platform. Playground is a web portal which allows you to write graphql queries directly against the API. This guide will walk you through authenticating and writing queries against the Houston API playground.

### Getting Acquainted with Playground

Before we get started there are some core components of the Playground that you will want to be familiar with. 

#### Query Editor

The main screen of Playground is divided into two halves. The left half is where you can write queries against the Houston API. There is some basic intellisense and code formatting to make your query writing easier. Once you have written a query, and corrected any mistakes picked up by Playground's intellisense, you can run the query by pressing the play/execution button which is located near the top of your screen aligned center horizontally. 

#### Results Viewer

The right half of the screen is for displaying the results of a query. After pressing the play/execution your results will appear in this right half of the screen. 

#### Query Variables and Headers

The bottom of the Query Editor (left half) panel has another smaller panel with two tabs. "Query Variables" and "HTTP Headers". This is where you can provided variables and headers such as authorization tokens to your queries.

#### Schema Explorer

On the far right, you will find a small tab with the label "SCHEMA". Clicking this tab will bring up the schema explorer which can allow you to discover various queries and mutations available to the user. This is a great place to start when first becoming acquainted with the Houston API as it allows you to explore what is possible.

## Authenticating Against The API
This guide assumes you have already created a user (via the CLI or UI) and have basic familiarity with [querying a graphql API](https://graphql.org/learn/queries/). Once you have done that, the first step is to generate an authentication token. You can use the following query as a template to get started.

```graphql
mutation CreateToken {
  createToken(identity: "USERNAME", password:"PASSWORD") {
    token {
      value
    }
  }
}
```

If your user and account have been setup properly, you can expect to receive an authorization token in the results panel which looks something like the example below.

```json
{
  "data": {
    "createToken": {
      "token": {
        "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiNjZmN2Y4NjUtMzE0NS00YmNlLTg0NmUtOWJlZjhlZDAxMTQwIiwiaWF0IjoxNTM3NTU4MzY3LCJleHAiOjE1Mzc2NDQ3Njd9.FM8PrnlWxMQSOfFuXDrfbysY8ckZNUpYk7E3bYfH3PQ"
      }
    }
  }
}
```

We now need to pass this authentication token through Playground to the houston-api in order to prove to houston that we have the proper authorization to perform various actions. You can pass this token into the Query Headers panel on the bottom left. Click "HEADERS" and copy and paste your token into the header so that it looks like the example below.


```json
{"authorization": "PASTE_TOKEN_HERE"}
```

You are now able to perform actions against the API which require authentication.


## Example Queries

Now that you have authenticated to the API, you can begin to perform queries. Below we have provided a few example queries to get you started. Remember, if you are unsure of how you might accomplish a task, you can always explore the possibilities with the schema explorer.

### Listing Your Available Workspaces


```graphql
query GetWorkspaces {
  workspaces {
    uuid
    label
  }
}
```

You could further extend the information returned by adding fields to the result attributes like so,

```graphql
query GetWorkspaces2 {
  workspaces {
    uuid
    label
    active
    createdAt
  }
}
```


### Listing A Workspace's Deployments

```graphql
query GetDeployments {
  deployments(workspaceUuid:"WORKSPACE-UUID") {
    uuid
    type
    label
    description
  }
}
```

In some cases, the query may return a nested object, you can access the nested object attributes using a query similar to the example below

```graphql
query GetDeployments {
  deployments(workspaceUuid:"WORKSPACE-UUID") {
    uuid
    type
    label
    description
    workspace {
      label
      uuid
    }
  }
}
```


### Modifying Objects with A Mutation


In this example we create a new Airflow deployment.

```graphql
mutation CreateDeployment {
  createDeployment(
    type: "airflow", label: "EXAMPLE LABEL", workspaceUuid:"WORKSPACE UUID", version: "1.9.0")
  {
    uuid
    type
    label
    workspace {
      uuid
    }
  }
}
```

When updating an existing object you may need to pass in a JSON payload of attributes. Notice how the `payload` parameter is unquotes raw json.

```graphql
mutation UpdateDeployment {
  updateDeployment(deploymentUuid:"DEPLOYMENT UUID", payload: {label: "MY NEW LABEL"}) {
    uuid
    label
  }
}
```
