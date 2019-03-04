---
title: "Airflow Executors: Explained"
description: "A thorough breakdown of Apache Airflow's Executors: Celery, Local and Kubernetes."
date: 2019-03-04T00:00:00.000Z
slug: "airflow-executors-explained"
heroImagePath: null
tags: ["Executor", "Airflow"]
---

If you're new to Apache Airflow, the world of Executors is difficult to navigate. Even if you're a veteran user overseeing 20+ DAGs, knowing what Executor best suits your use case at any given time isn't black and white - especially as the OSS project (and its utilities) continues to grow and develop.

This guide will do 3 things:

*   Define the core function of an Executor
*   Contextualize Executors with general Airflow fundamentals
*   Shed some insight to the 3 most popular Executors: Local, Celery, and Kubernetes

We'll give the Sequential Executor an honorable mention, too.

## Airflow Executors 101 

### What is an Executor?

Once a DAG is defined (perhaps with the help of an _Operator_), the following needs to happen in order for a single or set of "tasks" within that DAG to execute and be completed from start to finish:

1. The _Metadata Database_ (in Astronomer, that's PostgreSQL) keeps a record of all tasks within a DAG and their corresponding status (`queued`, `scheduled`, `running`, `success`, `failed`, etc) behind the scenes.
2. The _Scheduler_ reads from the Metadatabase to check on the status of each task and decide what needs to get done (and in what order).

This is where the Executor traditionally comes in.

3. The _Executor_ works closely with the _Scheduler_ to figure out what resources will actually complete those tasks (via a worker process or otherwise) as they're queued.

The difference _between_ executors comes down to the resources they have at hand and how they choose to utilize those resources to distribute work (or not distribute it at all).

### Related Definitions

When we're talking about task execution, you'll want to be familiar with these [somewhat confusing](https://issues.apache.org/jira/browse/AIRFLOW-57) terms, all of which we call "Environment Variables." The terms themselves have changed a bit over Airflow versions, but this list is compatible with 1.10.

**Environment Variables**: Env variables are a set of configurable values that allow you to dynamically fine tune your Airflow deployment. They're defined in your `airflow.cfg` (or directly through Astronomer's UI) and encompass everything from [email alerts](https://www.astronomer.io/docs/setting-up-airflow-emails/) to DAG concurrency (see below).

**Parallelism:** This determines how many task instances can be _actively_ running in parallel across DAGs given the resources available at any given time at the deployment level. Think of this as "maximum active tasks anywhere."

`ENV AIRFLOW__CORE__PARALLELISM=18`

**dag_concurrency**: This determines how many task instances your scheduler is able to schedule at once _per DAG_. Think of this as "maximum tasks that can be scheduled at once, per DAG." You might see the following:

`ENV AIRFLOW__CORE__DAG_CONCURRENCY=16`

**worker_concurrency**: This determines how many tasks _each_ _worker _can run at any given time. The CeleryExecutor for example, will [by default](https://github.com/apache/airflow/blob/master/airflow/config_templates/default_airflow.cfg#L358) run a max of 16 tasks concurrently. Think of it as "How many tasks each of my workers can take on at any given time." This number will naturally be limited by `dag_concurrency`. If you have 1 worker and want it to match your deployment's capacity, worker_concurrency = parallelism.

`ENV AIRFLOW__CELERY__WORKER_CONCURRENCY=9`

_Pro-Tip_: In our experience, parallelism and concurrency are somewhat co-dependent. We'd encourage you to keep them in line with one another.

**pool**: Pools are configurable via the Airflow UI and are used to limit the _parallelism_ on any particular set of tasks. You could use it to give some tasks priority over others, or to put a cap on execution for things like hitting a third party API that has rate limits on it, for example.

**max_threads**: This determines how many linear scheduling _processes_ the scheduler can handle in parallel at any given time. The default value is 2, but adjusting this number gives you some control over CPU usage - the higher the value, the more resources you'll need.

_Pro-Tip_: Rather than trying to find one set of configurations that work for _all_ jobs, we'd recommend grouping jobs by their type as much as you can.

## LocalExecutor: The Easy Option

Running Apache Airflow on a LocalExecutor exemplifies single-node architecture.

The LocalExecutor completes tasks in parallel that run on a single machine (think: your laptop, an EC2 instance, etc.) - the same machine that houses the Scheduler and all code necessary to execute. A single LocalWorker picks up and runs jobs as they’re scheduled and is fully responsible for all task execution.

In practice, this means that you don't need resources outside of that machine to run a DAG or a set of DAGs (even heavy workloads). For example, you might hear: "We are running the LocalExecutor for development on a t3.xlarge AWS EC2 instance."

### Bottom Line

**Pros:**

*   It's straightforward and easy to set up
*   It's cheap and resource light
*   It still offers parallelism

**Cons:**

*   It's not (as) scalable
*   It's dependent on a single point of failure

**When you should use it**

The LocalExecutor is ideal for testing.

The obvious risk is that if something happens to your machine, your tasks will see a standstill until that machine is back up.

Heavy Airflow users whose DAGs run in production will find themselves migrating from LocalExecutor to CeleryExecutor after some time, but you'll find plenty of use cases out there written by folks that run quite a bit on a LocalExecutor before making the switch. How much that executor can handle fully depends on your machine's resources and configuration. Until all resources on the server are used, the LocalExecutor actually scales up quite well.

## CeleryExecutor: The Mature Option

At its core, Airflow's CeleryExecutor is built for horizontal scaling.

[Celery](http://www.celeryproject.org/) itself is a way of running python processes in a distributed fashion. To optimize for flexibility and availability, the CeleryExecutor works with a "pool" of independent workers across which it can delegate tasks, via messages. On Celery, your deployment's scheduler adds a message to the queue and the Celery broker delivers it to a Celery worker (perhaps one of many) to execute.

If a worker node is ever down or goes offline, the CeleryExecutor quickly adapts and is able to assign that allocated task or tasks to another worker.

If you're running native Airflow, adopting a CeleryExecutor means you'll have to set up an underlying database to support it (RabbitMQ/Redis). If you're running on Astronomer, the switch really just means your deployment will be a bit heavier on resources (and price) - and that you'll likely have to keep a closer eye on your workers. 

_Astronomer Note_: Astronomer Cloud runs on top of Google's managed Kubernetes service, [GKE](https://cloud.google.com/kubernetes-engine/). If the Kubernetes cluster node on GKE that powers Celery workers for any reason goes down and brings a worker with it, Kube will handle rescheduling work assigned to that pod. When the pod comes back up, it'll reconnect to [Redis](https://redis.io/) and grab tasks.

### Worker Termination Grace Period

Airflow has what we call a "Worker Termination Grace Period" (otherwise known as the "Celery Flush Period") that helps minimize task disruption upon deployment by continuing to run tasks for an x number of minutes (configurable via the Astro UI) after you push up a deploy. Under a LocalExecutor, your workers will start immediately upon deployment regardless of whether or not tasks were mid-execution, which could be disruptive if any of your DAGs are on a tight schedule. If you're careful to plan code pushes and deploys you should be ok, but just something of note that our heavy users certainly appreciate.

_Astronomer Note_: This is a Kubernetes-only function that Astronomer leverages and exposes to give our users maximum control over their deployments. If you're running native Airflow without Kubernetes, you won't have access to this feature.

### Bottom Line

**Pros:**

*   High availability
*   Built for horizontal scaling
*   Worker Termination Grace Period (on Astronomer)

**Cons:**

*   It's pricier
*   It takes some work to set up
*   Worker maintenance

**When you should use it**

While the LocalExecutor is a great way to save on engineering resources for testing even with a heavy workload, we generally recommend going with Celery for running DAGs in production, especially if you're running anything that's time sensitive.

## Kubernetes Executor: Coming soon on Astronomer

The fresh-off-the-press [Kubernetes Executor](https://github.com/apache/airflow/blob/master/docs/kubernetes.rst) leverages the power of [Kubernetes](https://kubernetes.io/) for ultimate resource optimization. 

New to Airflow 1.10, the Kubernetes Executor relies on a fixed single Pod that dynamically delegates work and resources. For each and every task that needs to run, the Executor talks to the Kubernetes API to dynamically launch an _additional_ Pod, each with its own Scheduler and Webserver, which it terminates when that task is completed. The fixed single Pod has a Webserver and Scheduler just the same, but it'll act as the middle-man with connection to Redis and all other workers.

This means a few things:

*   In times of high traffic, you can scale up
*   In times of low traffic, you can scale to near-zero
*   For _each_ individual task, you can for the first time configure the following:
    *   Memory allocation
    *   Service accounts
    *   Airflow image

### Scale to Zero

With the Local and Celery Executors, a deployment whose DAGs run once a day will operate with a fixed set of resources for the full 24 hours - only 1 hour of which actually puts those resources to use. That's 23 hours of resources you're paying for but don't deliver.

### Less work for your Scheduler

On the Local and Celery Executors, the Scheduler is charged with constantly having to check the status of each task at all times from the Postgres backend - "Is it running? Queued? Failed?"

With the KubeExecutor, the workers (pods) talk directly to the _same_ Postgres backend as the Scheduler and can to a large degree take on the labor of task monitoring. In this architecture, a task failure is handled by its individual Pod. The Scheduler is only responsible for keeping an eye on the pods themselves and take action if one or more of them fail.

Via the Kubernetes "Watcher" API, the scheduler reads event logs for anything with a failed label tied to that Airflow instance. If a pod fails, the Scheduler alerts Postgres and bubbles that failure up to the user to trigger whatever alerting solution is set up on your deployment.

### Bottom Line

**Pros:**

*   Cost and resource efficient
*   Fault tolerant
*   Task-level configurations

**Cons:**

*   Kubernetes familiarity as a potential barrier to entry

**When you should use it**

While arguably not production-ready just yet, the Kubernetes Executor offers extraordinary potential. If you're familiar with Kubernetes and want to give it a shot, we'd highly recommend doing so to be at the forefront of the modern Apache Airflow configuration.

### Honorable Mention

**Sequential Executor:** The Sequential Executor runs a _single_ task instance at a time in a linear fashion with no parallelism functionality (A → B → C). It does identify a single point of failure, making it helpful for debugging. Otherwise, the Sequential Executor is not recommended for any use cases minimally robust that require more than a single task execution at a time.