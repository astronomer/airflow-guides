---
title: "Airflow High-Availability"
description: "Best practice for running a high-availability Airflow cluster"
date: 2018-09-11T00:00:00.000Z
slug: "airflow-high-availability"
heroImagePath: "https://assets.astronomer.io/website/img/guides/bestwritingpractices.png"
tags: ["Best Practices", “Components”, “Kubernetes”, “Executors”]
---

## Overview
High-Availability (HA) is a concept which refers to a particular service or cluster meeting a specified amount of uptime. In order to meet more stringent uptime requirements, a service or cluster will often leverage a more complex architecture to ensure that downtime is rare and brief when it does occur.

While the Apache Airflow project does not discuss specifics of HA, some in the community have discussed [Airflow HA previously](http://site.clairvoyantsoft.com/making-apache-airflow-highly-available/). Unlike those previous discussions, this article will focus on HA for an Airflow cluster orchestrated by Kubernetes. 

Kubernetes is an open-source container-orchestration tool, ["providing basic mechanisms for deployment, maintenance, and scaling of applications."](https://github.com/kubernetes/kubernetes/#kubernetes) It provides abstractions that simplify highly-available Airflow clusters for our customers.

## Components

Apache Airflow contains several core components that we must consider when writing about the availability of an Airflow cluster. This section discusses each component and the best effort scenario for ensuring that it's uptime meets your high-availability needs.

### Webserver

Webserver HA in general is widely considered a solved problem. The basic idea is to have a pool of webservers that can then have traffic distributed amongst the pool. This has the effect of both ensuring that each resource in the pool remains at a safe level of utilization as well as insuring against any one webserver going down. In the event of a resource crashing, the load balancer is responsible for redirecting traffic to an available resource.

Kubernetes provides some abstractions around these concepts to help developers easily load balance their webservers. Within Kubernetes one can deploy a [service](https://kubernetes.io/docs/concepts/services-networking/service/) of type [LoadBalancer](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) which distributes traffic to your [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/#what-is-ingress) or Ingresses. These ingress controller(s) are then responsible for routing your traffic to your webserver containers.

### Executors

Airflow provides the user an abstraction around how the work is "executed", known as [executors](https://airflow.apache.org/code.html#executors). 

The [LocalExecutor](https://airflow.apache.org/code.html#airflow.executors.local_executor.LocalExecutor) runs on the same node as the scheduler and therefore can only be scaled up, preventing a user from creating execution redundancy one would see if they were able to scaled out.

The [CeleryExecutor](https://airflow.apache.org/code.html#airflow.executors.celery_executor.CeleryExecutor) is a common choice for a distributed executor that allows a user to spin up many worker nodes. If a single node goes down, other workers remain available. If workers begin to fall behind, one can scale out the workers to meet the current demand.

The [KubernetesExecutor](https://airflow.apache.org/kubernetes.html?highlight=kubernetes%20executor) removes the need to run individual workers, instead allowing work to be evenly distributed across the entire Kubernetes cluster. The work is executed inside a Docker container managed by a [Kubernetes Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod/). Pods represent a unique service running on one or more containers and provide a clean abstraction around the creation, execution, termination and deletion of that service.

### Scheduler

At the time of writing, the scheduler is the only component of Airflow that cannot truly be highly-available. This is the result of it not being designed as a distributed service, therefore only one scheduler can be running at any given time. This leaves us focusing on how to minimize downtime in the event of a scheduler failing.

The first step one can take is setting appropriate [health checks and liveness probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/) to allow Kubernetes to appropriately manage the state of the scheduler pod and containers. Once configured, one can begin to explore [Pod Disruption Budgets](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/#how-disruption-budgets-work) to ensure that there is always a scheduler available for failover in the event of a failure. 
