---
title: "Airflow's Components"
description: "How all of Apache Airflow's components fit together."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-components"
heroImagePath: null
tags: ["Airflow", "Components"]
---

## Core Components

Apache Airflow consists of 4 core components:

**Webserver** Airflow's UI.

At its core, this is just a Flask app that displays the status of your jobs and provides an interface to interact with the database and reads logs from a remote file store (S3, Google Cloud Storage, AzureBlobs, ElasticSearch etc.).

**Scheduler** This is responsible for scheduling jobs.

This is a multi-threaded Python process that uses the DAG object with the state of tasks in the metadata database to decide what tasks need to be run, when they need to be run, and where they are run.

**Executor** The mechanism by which work actually gets done.

There are several executors, each with strengths and weaknesses.

**Metadata Database** A database (usually PostgresDB or MySql, but can be anything with SQLAlchemy support) that determines how the other components interact. The scheduler stores and updates task statuses, which the Webserver then uses to display job information.

![title](https://assets2.astronomer.io/main/guides/airflow_component_relationship_fixed.png)

## How does work get scheduled?

Once the scheduler is started:

1. The scheduler "taps" the _dags_ folder and instantiates all DAG objects in the metadata databases. Depending on the configuration, each DAG gets a configurable number of processes.

  **Note**: This means all top level code (i.e. anything that isn't defining the DAG) in a DAG file will get run each scheduler heartbeat. Try to avoid top level code to your DAG file unless absolutely necessary.

1. Each process parses the DAG file and creates the necessary DagRuns based on the scheduling parameters of each DAG's tasks. A TaskInstance is instantiated for each task that needs to be executed. These TaskInstances are set to `Scheduled` in the metadata database.

1. The primary scheduler process queries the database for all tasks in the `SCHEDULED` state and sends them to the executors (with state changed to `QUEUED`).

1. Depending on the execution setup, workers will pull tasks from the queue and start executing it. Tasks that are pulled off of the queue are changed from "queued" to "running."

1. If a task finishes, the worker then changes the status of that task to its final state (finished, failed, etc.). The scheduler then reflects this change in the metadata database.

```python
# https://github.com/apache/incubator-airflow/blob/2d50ba43366f646e9391a981083623caa12e8967/airflow/jobs.py#L1386

def _process_dags(self, dagbag, dags, tis_out):
        """
        Iterates over the dags and processes them. Processing includes:
        1. Create appropriate DagRun(s) in the DB.

        2. Create appropriate TaskInstance(s) in the DB.

        3. Send emails for tasks that have missed SLAs.

        :param dagbag: a collection of DAGs to process
        :type dagbag: models.DagBag
        :param dags: the DAGs from the DagBag to process
        :type dags: DAG
        :param tis_out: A queue to add generated TaskInstance objects
        :type tis_out: multiprocessing.Queue[TaskInstance]
        :return: None
        """
        for dag in dags:
            dag = dagbag.get_dag(dag.dag_id)
            if dag.is_paused:
                self.log.info("Not processing DAG %s since it's paused", dag.dag_id)
                continue

            if not dag:
                self.log.error("DAG ID %s was not found in the DagBag", dag.dag_id)
                continue

            self.log.info("Processing %s", dag.dag_id)

            dag_run = self.create_dag_run(dag)
            if dag_run:
                self.log.info("Created %s", dag_run)
            self._process_task_instances(dag, tis_out)
            self.manage_slas(dag)

        models.DagStat.update([d.dag_id for d in dags])
```

## Controlling Component Interactions

The schedule at which these components interact can be set through airflow.cfg. This file has tuning for several airflow settings that can be optimized for a use case.

This file is well documented, but a few notes:

### Executors:

By default, Airflow can use the LocalExecutor, SequentialExecutor, the CeleryExecutor, or the KubernetesExecutor.

- The SequentialExecutor just executes tasks sequentially, with no parallelism or concurrency. It is good for a test environment or when debugging deeper Airflow bugs.

- The LocalExecutor supports parallelism and hyperthreading and is a good fit for Airflow running on local machine or a single node.

- The CeleryExecutor is the preferred method to run a distributed Airflow cluster. It requires Redis, RabbitMq, or another message queue system to coordinate tasks between workers.

- The KubernetesExecutor, which was introduced in Airflow 1.10, calls the Kubernetes API to create a temporary pod for each task to run, enabling users to pass in custom configurations for each of their tasks and use resources efficiently.

### Parallelism

The `parallelism`, `dag_concurrency` and `max_active_runs_per_dag` settings can be tweaked to determine how many tasks can be executed at once.

It is important to note that `parallelism` determines how many task instances can run in parallel in the executor, while `dag_concurrency` determines the maximum number of tasks that can run within each DAG. These two numbers should be fine tuned together when optimizing an Airflow deployment, with the ratio depending on the number of DAGs.

`max_active_runs_per_dag` determines how many DagRuns across time can be scheduled for each particular DAG. This number should depend on how how long DAGs take to execute, their schedule interval, and scheduler performance.

### Scheduler Settings

`job_heartbeat_sec` determines the frequency at which the scheduler listens for external kill signals,  while `scheduler_heartbeat_sec` looks for new tasks.

As the cluster grows in size, increasing the `scheduler_heartbeat_sec` gets increasingly expensive. Depending on the infrastructure and how long tasks generally take, and how the scheduler performs, consider increasing this number from the default.
