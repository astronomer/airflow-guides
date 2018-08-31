---
title: "Introduction to Kubernetes"
description: "High-level overview of introductory concepts in Kubernetes."
date: 2018-08-30T00:00:00.000Z
slug: "intro-to-kubernetes"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Airflow", "Kubernetes", "Infrastructure"]
---

# Kubernetes 101
_Modern Distrbuted Applications_

## Container and Data Center Orchestration

Modern best practice for most modern application has them running across containers in a distributed architecture. Though this may add infrastructural complexity, it allows for a more fault tolerant, scalable system that keeps compute costs low. This microservice architectures (where each part of your application runs as a microservice) allows for independent deployment, greater granularity for performance tuning (e.g. switch Python for Go just one part of an application), and a host of other benefits.

However, applications cannot be developed this way without an abstraction to manage, deploy, and coordinate t hese containers.

## Current players in the Container Orchestration Space

The most popular options for container orchestration tools right now are Kubernetes, Docker Swarm, and Apache Mesos. As a whole, Kubernetes  has the most community support and is the most popular by a significant margin. Regardless, we'll compare the three here, as the best option for container orchestration is largely contingent on your use case.

**Kubernetes** is a powerful and highly extensible orchestrator. though it comes with its own vocabularly and complexities, it has the most community support (with growing corporate support from Google, Amazon, Microsoft, and others).

**Docker Swarm** is very simple to set up, but is not as robust as Kubernetes. It's a good option if simplicity is desired and your services are limited to those provided by Docker Compose.

**Apache Mesos** is more suited for large data centers where multiple complex applications will need to be setup and configured. It's a good option if you're going to need to manage multiple Kubernetes clusters ]within a larger data center. Mesos existed prior to the widespread interest in containerization, and is therefore less geared towards running containers.

The best option should depend on your use case, but Kubernetes has the strongest community support, upward-trending development, and flexibility.


## So What is Kubernetes Anyway?

Kubernetes, also known as k8s, is originally an internal project Google that is now maintained by the Cloud Native Computing  Foundation. With Kubernetes, you can cluster together groups of hosts running Linux containers and easily manage those clusters. It works with a range of different container tools, but is designed with Docker as a first class citizen.

    
## Why use Kubernetes?

If implementing a modern microservice architecture, containers are probably running across a host of nodes, each with different resources and requirements required to run. Kubernetes provides a common abstraction to deploy, manage, and scale those containers as the application needs. 

As system requirements change, move container workloads in Kubernetes can be moved from one cloud provider or hosting infrastructure to another without changing any applicatoin level code.

![move_to_kubes](https://cdn.astronomer.io/website/img/guides/move_to_kubes.jpg)


## Key Terms

**Master**: Responsible for maintaining the desired state for your cluster, the master is the machine that controls nodes. This is where task assignments originate. When you interact with Kubernetes using their `kubectl` CLI, you're directly communicating with the cluster's master. The master can also be replicated for availability and redundancy.

**Node**: The machines (VMs, physical servers, etc) that perform the requested, assigned tasks from the Master. The nodes are responsible for running your applications and cloud workflows.

**Pod**: The basic scheduling unit in Kubernetes, a pod consists of a group of one or more containers deployed to a single node. All containers in a pod share an IP address, IPC, hostname, and other resources. Pods abstract network and storage away from the underlying container, allowing you to move containers around the cluster easily.

**Container**: Resides inside a pod and is the lowest level of a microservice which holds the running application, the libraries, and their dependencies. 

**Controller**: A reconciliation loop that drives actual cluster state towards the desired cluster state. Controllers manage how many identical copies of a pod should be running on the cluster.

**Service**: A set of pods that works together and are defined by a label selector, services decouple work definitions from the pods.

**Kubelet**: Responsible for the running state of each node, ensuring that all containers are healthy. Kubelet monitors the state of a pod and, if the pod is not in the desired state, kubelet ensures that the pod is redeployed to the same node in the desired state.

**Kubectl**: The command line configuration tool for Kubernetes. For an overview detailing kubectl syntax, command operations, and examples, check out the [documentation here](https://kubernetes.io/docs/reference/kubectl/overview/).

![ui-dashboard](https://cdn.astronomer.io/website/img/guides/ui-dashboard.png)



[Source 1](https://searchitoperations.techtarget.com/definition/Google-Kubernetes)
[Source 2](https://codefresh.io/kubernetes-tutorial/kubernetes-vs-docker-swarm-vs-apache-mesos/)
[Source 3](https://en.wikipedia.org/wiki/Kubernetes#Controllers)
[Source 4](https://www.redhat.com/en/topics/containers/what-is-kubernetes)
[Source 5](https://kubernetes.io/docs/concepts/overview/components/)



