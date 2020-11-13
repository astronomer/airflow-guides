---
title: "Useful SQL queries for Apache Airflow"
description: "A home for SQL queries that we frequently run on our Airflow postgres database."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-queries"
heroImagePath: "https://assets.astronomer.io/website/img/guides/usefulsqlqueries.png"
tags: ["Database", "SQL", "DAGs", "Tasks"]
---

## Get total completed task count

```sql
SELECT COUNT(1)
FROM task_instance
WHERE
  state IS NOT NULL
  AND state NOT IN ('scheduled', 'queued');
```

## Get tasks started per hour for past week

```sql
SELECT
  date_trunc('hour', start_date) AS d,
  count(1)
FROM task_instance
GROUP BY d
ORDER BY 1 DESC
LIMIT 24*7;
```

## Get tasks finished per hour for past week

```sql
SELECT
  date_trunc('hour', end_date) AS d,
  count(1)
FROM task_instance
WHERE
  state IN ('skipped', 'success', 'failed')
  AND end_date IS NOT NULL
GROUP BY d
ORDER BY 1 DESC
LIMIT 24*7;
```

## Unpause a list of paused DAGs

```sql
UPDATE dag
SET is_paused = FALSE
WHERE
  is_paused is TRUE
  AND dag_id in (
    'clickstream_v2_to_redshift__xxx',
    'clickstream_v2_to_redshift__yyy',
    'clickstream_v2_to_redshift__zzz',
  );
```

## Pause all active DAGs and unpause with a temp table

We use this to be able to limit the impact of prod rollouts by only affecting one or two Astronomer DAGs before all customers.

Change `dag_tmp` to something unique and make sure it doesn't exist first.

```sql
SELECT dag_id
INTO dag_tmp
FROM dag
WHERE is_paused IS FALSE;

UPDATE dag
SET is_paused = TRUE
FROM dag_tmp
WHERE dag.dag_id = dag_tmp.dag_id;

UPDATE dag
SET is_paused = FALSE
FROM dag_tmp
WHERE dag.dag_id = dag_tmp.dag_id;

DROP TABLE dag_tmp;
```

## Delete a DAG completely

Deleting the DAG file itself leaves traces across 7 database tables, such as those for DAG runs and task instances.

Sometimes we need to completely blow out these rows for a certain DAG to re-run it from scratch, rewind the start date forward or backward, etc.

In the next release of Airflow after 1.9, a [delete_dags command](https://stackoverflow.com/a/49683543/149428) will be included in the CLI and REST API.  For Airflow versions through 1.9, we have this.

```sql
delete from xcom where dag_id = 'my_dag_id';
delete from task_instance where dag_id = 'my_dag_id';
delete from sla_miss where dag_id = 'my_dag_id';
delete from log where dag_id = 'my_dag_id';
delete from job where dag_id = 'my_dag_id';
delete from dag_run where dag_id = 'my_dag_id';
delete from dag where dag_id = 'my_dag_id';
```

For Airflow 1.10, two additional tables have been added where the DAG also needs to be removed.

```sql
delete from xcom where dag_id = 'my_dag_id';
delete from task_instance where dag_id = 'my_dag_id';
delete from task_reschedule where dag_id = 'my_dag_id';
delete from task_fail where dag_id = 'my_dag_id';
delete from sla_miss where dag_id = 'my_dag_id';
delete from log where dag_id = 'my_dag_id';
delete from job where dag_id = 'my_dag_id';
delete from dag_run where dag_id = 'my_dag_id';
delete from dag where dag_id = 'my_dag_id';
```

## Rewinding a DAG

To rewind a DAG:

1. Turn the DAG off in Airflow.
1. Blow out the Airflow metadata for that DAG.
1. The DAG will be automatically recreated and started from the new config.

If you blow out the metadata before the cache has updated, it will re-create the DAG with the old data.

## Fast Forwarding a DAG

You can fast forward a DAG by generating fake DAG runs in the Airflow metadata database.

First determine the timestamp of the latest DAG run:

```sql
-- NOTE: PAUSE THE DAG FIRST
-- change to your desired dag_id
select max(execution_date)
from dag_run
where dag_id = 'clickstream_v2_to_redshift__59ca877951ad6e2f93f870c5';
```

Take the timestamp output from the first query and add 1 hour (the output above was 5:15 AM, so 6:15 AM is used below), then put the new value where _both_ of the timestamps are in the second query:

```sql
insert into dag_run(dag_id, execution_date, run_id, state)
values (
  'clickstream_v2_to_redshift__59ca877951ad6e2f93f870c5',
  '2018-04-27 06:15:00.000000',
  'scheduled__2018-04-27T06:15:00__fake',
  'failed'
);
```

If you want to go all the way up until (exclusive) 5/9/18 00:00 UTC, then the last fake DAG run to create is '2018-05-08 23:15:00.000000'.
