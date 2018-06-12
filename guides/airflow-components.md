---
title: "Airflow's Components"
description: "How everything fits together in Airflow"
date: 2018-05-21T00:00:00.000Z
slug: "airflow-branch-operator"
heroImagePath: null
tags: ["Airflow", "Components"]
---


#Airflow Components

## Core Components
_How everything fits together_

At the core,  Airflow consists of 4 core components:

**Webserver:** Airflow's UI. At it's core, this is just a flask app that displays the status of your jobs and provides an interface to interact with the database and reads logs from a remote file store (S3, Google Cloud Storage, AzureBlobs, etc.).

**Scheduler:** This is responsible for scheduling jobs. It is a multithreaded Python process that uses the DAG object wtih the state of tasks in teh metadata database to decide what tasks need to be run, when they need to be run, and where they are run.

**Executor:** The mechanisms by which work actually gets done. It is a message queuing process that communicates with the Scheduler to determine how work gets done. There are a few different varieties of executors, each wtih their own stregnths and weaknesses.

**Metadata Database:** A database (usually Postgres, but can be anything with SQLAlchemy support) that powers how the other components interact. The scheduler stores and updates task statuses, which the webserver then uses to display job information

![title](img/airflow_component_relationship.png)

## How does work get scheduled?

Once the scheduler is started:

1) The scheduler "taps" the _dags_ folder and instanstiates all DAG objects in the metadata databases. Depending on the configuration, each DAG gets a configurable number of processes.

2) Each process parses the DAG file and creates the necessary DagRuns based on the scheduling parameters of each DAG's tasks. A TaskInstance is instanstiated for each task that needs to be executed. These TaskInstances are set to `Scheduled` in the metadata database. 

3) The primary scheduler process queries the database for all tasks in the `SCHEDULED` state and sends them to the executors to be executed (with state changed to `QUEUED`).  

4) Depending on the execution setup, workers will pull tasks from the queue and start executing it. Tasks that are pulled off of the queue are changed from "queued" to "running."

5) If a task finishes, the worker then changes the status of that task to it's final state (finished, failed, etc.). The scheduler then reflects this change in the metadata database.


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