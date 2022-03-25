---
title: "Orchestrating Redshift Operations from Airflow"
description: "Setting up a connection to Redshift and using available Redshift modules."
date: 2022-03-21T00:00:00.000Z
slug: "airflow-redshift"
tags: ["Database", "SQL", "DAGs", "Integrations", "AWS"]
---

>Note: All code in this guide can be found [in this GitHub repo](https://github.com/astronomer/cs-tutorial-redshift). 

## Overview

Amazon Redshift is a fully-managed cloud data warehouse. It is capable of analyzing exabytes of data and running complex
analytical queries, making it the most widely used cloud data warehouse. Developing a dimensional data mart in Redshift
requires automation and orchestration for repeated queries, data quality checks, and overall cluster operations.

Airflow is the perfect orchestrator to pair with Redshift. With Airflow, you can easily orchestrate each step of your
Redshift pipeline, integrate with services that clean your data, and store and publish your results using only SQL and 
Python code.

In this guide, we'll review the Redshift modules available as part of the 
[AWS Airflow provider](https://registry.astronomer.io/providers/amazon). We'll also provide three example 
implementations using Redshift with Airflow: one for executing SQL in a Redshift Cluster, one for Pausing & Resuming a 
Redshift Cluster, and one for transferring data between Amazon S3 and a Redshift Cluster.

## Setup

To use any Redshift operators in Airflow, you will first need to install the provider package and create a connection 
to your Redshift cluster.

### Install Required pip Dependency

Before you can use all the Airflow components for Redshift, you will need to ensure that you have the Amazon 
Provider installed on your Airflow deployment. To do this, simply add `apache-airflow-providers-amazon` to your 
`requirements.txt` file.

### Add Required Connections

You will need to set up your Airflow instance so that it can connect to Redshift. You can do this by adding the following 
connections in the Airflow UI to authenticate to Redshift. In the Airflow UI, navigate to *Admin >> Connections* and add 
the following connections:
 
- `redshift_default` (this is the default connection that Airflow redshift components will search for and use). If a 
  different name from `redshift_default` is used for this connection, then it will have to be specified on the 
  components that require a Redshift connection. Use the following parameters for your new connection (all other fields 
  can be left blank):
  
  ```yaml
  Connection ID: redshift_default
  Connection Type: Amazon Redshift
  Host: <YOUR-REDSHIFT-ENDPOINT> (i.e. redshift-cluster-1.123456789.us-west-1.redshift.amazonaws.com)
  Schema: <YOUR-REDSHIFT-DATABASE> (i.e. dev, test, prod, ect.)
  Login: <YOUR-REDSHIFT-USERNAME> (i.e. awsuser)
  Password: <YOUR-REDSHIFT-PASSWORD>
  Port: <YOUR-REDSHIFT-PORT> (i.e. 5439)
  ```
  
- `aws_default` (this is the default connection that other Airflow AWS components will search for and use). If a 
  different name from `aws_default` is used for this connection, then it will have to be specified on the components 
  that require an AWS connection. Use the following parameters for your new connection (all other fields can be left 
  blank):
  
  ```yaml
  Connection ID: aws_default
  Connection Type: Amazon Web Services
  Extra: {
    "aws_access_key_id": "<your-access-key-id>", 
    "aws_secret_access_key": "<your-secret-access-key>", 
    "region_name": "<your-region-name>"
  }
  ```


**Additional Notes:**

- To authenticate to Redshift using IAM Authentication or Okta Identity Provider, see 
  [this doc](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/connections/redshift.html) 
  for instructions
- Ensure that your Redshift Cluster allows inbound traffic from the IP Address where Airflow is running
- The `aws_default` connection will need the following permissions on AWS:
    - Access to perform read/write actions for a pre-configured S3 Bucket
    - Access to interact with the Redshift Cluster, specifically: 
        - `redshift:DescribeClusters`
        - `redshift:PauseCluster`
        - `redshift:ResumeCluster`

### Underlying Data

It is worth noting that these examples will be using the Sample database (TICKIT) provided by AWS. For more details 
on the underlying data, please see Amazon's documentation [here](https://docs.aws.amazon.com/redshift/latest/dg/c_sampledb.html).

## Using the RedshiftSQLOperator

With an established connection to Redshift, it's time to explore the 
[RedshiftSQLOperator](https://registry.astronomer.io/providers/amazon/modules/redshiftsqloperator)! The 
RedshiftSQLOperator is used to run one or multiple SQL statements against a Redshift Cluster. Use cases for this include: 
creating data schema models in your data warehouse, creating fact or dimension tables for various data models, 
performing data transformations or data cleaning, etc. The below example shows how to call a `.sql` file in the 
RedshiftSQLOperator:

```python
from datetime import datetime
from airflow.models import DAG
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator

from datetime import datetime
with DAG(
    dag_id=f"example_dag_redshift",
    schedule_interval="@daily",
    start_date=datetime(2008, 1, 1),
    end_date=datetime(2008, 1, 7),
    max_active_runs=1,
    template_searchpath='/usr/local/airflow/include/example_dag_redshift',
    catchup=True
) as dag:

    t = RedshiftSQLOperator(
        task_id='fct_listing',
        sql='/sql/fct_listing.sql',
        params={
            "schema": "fct",
            "table": "listing"
        }
    )
```

Notice how the `template_searchpath` parameter is used on the `DAG()` object. This means that our `.sql` file would be 
located at `/usr/local/airflow/include/example_dag_redshift/sql/fct_listing.sql`. Here would be the contents of that 
file:

```sql
begin;
create table if not exists {{ params.schema }}.{{ params.table }} (
  date_key date,
  total_sellers int,
  total_events int,
  total_tickets int,
  total_revenue double precision
) sortkey(date_key)
;

delete from {{ params.schema }}.{{ params.table }} where date_key = '{{ ds }}';

insert into {{ params.schema }}.{{ params.table }}
  select
    listtime::date as date_key,
    count(distinct sellerid) as total_sellers,
    count(distinct eventid) as total_events,
    sum(numtickets) as total_tickets,
    sum(totalprice) as total_revenue
  from tickit.listing
  where listtime::date = '{{ ds }}'
  group by date_key
;
end;
```

Looking at the SQL, you may be wondering what `{{ params.schema }}`, `{{ params.table }}`, and `{{ ds }}` are. Based on 
the task definition, `{{ params.schema }}` was set as *fct* and `{{ params.table }}` was set as *listing*. So 
those values will be injected into the SQL at runtime. The `{{ ds }}` variable is a built-in [Airflow Jinja Template 
Variable](https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html) that will return the DAG run's 
logical date as *YYYY-MM-DD*. Using these variables will make your SQL code reusable and on par with DAG writing best
practices (particularly around the concept of 
[idempotency](https://www.astronomer.io/guides/dag-best-practices#reviewing-idempotency)).

## Using the S3ToRedshiftOperator

The [S3ToRedshiftOperator](https://registry.astronomer.io/providers/amazon/modules/s3toredshiftoperator) executes a 
`COPY` command to load files from s3 to Redshift. The example below demonstrates how to use this Operator:

```python
from datetime import datetime
from airflow.models import DAG
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

from datetime import datetime
with DAG(
    dag_id=f"example_dag_redshift",
    schedule_interval="@daily",
    start_date=datetime(2008, 1, 1),
    end_date=datetime(2008, 1, 7),
    max_active_runs=1,
    template_searchpath='/usr/local/airflow/include/example_dag_redshift',
    catchup=True
) as dag:

    s3_to_redshift = S3ToRedshiftOperator(
        task_id='s3_to_redshift',
        schema='fct',
        table='from_redshift',
        s3_bucket='airflow-redshift-demo',
        s3_key='fct/from_redshift',
        redshift_conn_id='redshift_default',
        aws_conn_id='aws_default',
        copy_options=[
            "DELIMITER AS ','"
        ],
        method='REPLACE'
    )
```

The result of this would be to copy the s3 blob `s3://airflow-redshift-demo/fct/from_redshift` into the table 
`fct.from_redshift` on the Redshift cluster. With this operator, you can pass all the same copy options that exist in
AWS via the `copy_options` parameter. This includes:

- [Data format parameters](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html) (i.e 
  [FORMAT](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html#copy-format), 
  [CSV](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html#copy-csv), 
  [DELIMITER](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html#copy-delimiter), 
  [FIXEDWIDTH](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-format.html#copy-fixedwidth), etc.)
- [Data conversion parameters](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-conversion.html) (i.e. 
  [ACCEPTANYDATE](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-conversion.html#copy-acceptanydate), 
  [EMPTYASNULL](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-conversion.html#copy-emptyasnull), 
  [NULL AS](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-conversion.html#copy-null-as), 
  [TRUNCATECOLUMNS](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-conversion.html#copy-truncatecolumns), etc.)
- [Data load operations](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html) (i.e 
  [COMPROWS](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html#copy-comprows), 
  [COMPUPDATE](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html#copy-compupdate), 
  [NOLOAD](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html#copy-noload), 
  [MAXERROR](https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html#copy-maxerror), etc.)
  
Read AWS's official documentation for the `COPY` commmand 
[here](https://docs.aws.amazon.com/redshift/latest/dg/r_COPY.html#r_COPY-syntax-overview-data-format). In this example, 
the delimiter for the blob has been specified as a comma (this overrides the default of a pipe delimiter). 

## Using the RedshiftToS3Operator

The [RedshiftToS3Operator](https://registry.astronomer.io/providers/amazon/modules/redshifttos3operator) executes an 
`UNLOAD` command to s3 as a CSV with headers. `UNLOAD` automatically creates encrypted files using Amazon S3 server-side
encryption (SSE). There are various use cases for using the `UNLOAD` command. Some of the more common ones include:

- Archiving old data that is no longer needed in your Redshift Cluster
- Sharing the results of query data without granting access to Redshift 
- Saving the result of query data into S3 to analyze it with BI tools or use it in an ML pipeline 

```python
from datetime import datetime
from airflow.models import DAG
from airflow.providers.amazon.aws.transfers.redshift_to_s3 import RedshiftToS3Operator

with DAG(
    dag_id=f"example_dag_redshift",
    schedule_interval="@daily",
    start_date=datetime(2008, 1, 1),
    end_date=datetime(2008, 1, 7),
    max_active_runs=1,
    template_searchpath='/usr/local/airflow/include/example_dag_redshift',
    catchup=True
) as dag:
  
    redshift_to_s3 = RedshiftToS3Operator(
        task_id='fct_listing_to_s3',
        s3_bucket='airflow-redshift-demo',
        s3_key='fct/listing/{{ ds }}_',
        schema='fct',
        table='listing',
        redshift_conn_id='redshift_default',
        aws_conn_id='aws_default',
        table_as_file_name=False,
        unload_options=[
            "DELIMITER AS ','",
            "FORMAT AS CSV",
            "ALLOWOVERWRITE",
            "PARALLEL OFF",
            "HEADER"
        ]
    )
```

The result of this would be to copy the `fct.listing` table from a Redshift cluster to the following s3 blob 
`s3:://airflow-redshift-demo/fct/listing/YYYY-MM-DD_` (where YYYY-MM-DD is the logical date for the DAG run). With this
operator, you can pass all the same unload options that exist in AWS. Read AWS's official documentation for the `UNLOAD` 
command [here](https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html). In this example, the delimiter for the 
blob has been specified as a comma, the format of the blob has been specified as a csv, any existing files will be 
overwritten, data will *not* be written in parallel across multiple files, and  a header line containing column names 
will be included at the top of the file.

## Pause and Resume a Redshift Cluster from Airflow

Amazon Redshift supports the ability to pause and resume a cluster, allowing customers to easily suspend on-demand 
billing while the cluster isn't being used. Read more on this from AWS [here](https://aws.amazon.com/about-aws/whats-new/2020/03/amazon-redshift-launches-pause-resume/#:~:text=Amazon%20Redshift%20now%20supports%20the,suspended%20when%20not%20in%20use.).
You may want your Airflow DAG to pause and unpause a Redshift cluster at times when it isn't being queried or used. 
Additionally, you may want to pause your Redshift cluster at the end of your Airflow pipeline and/or resume your 
Redshift cluster at the beginning of your Airflow pipeline. There are currently three Airflow modules available to 
accomplish this use case: 

1. The [RedshiftPauseClusterOperator](https://registry.astronomer.io/providers/amazon/modules/redshiftpauseclusteroperator)
   can be used to pause an AWS Redshift Cluster.
2. The [RedshiftResumeClusterOperator](https://registry.astronomer.io/providers/amazon/modules/redshiftresumeclusteroperator)
   can be used to resume a paused AWS Redshift Cluster.
3. The [RedshiftClusterSensor](https://registry.astronomer.io/providers/amazon/modules/redshiftclustersensor) can be 
   used to wait for a Redshift cluster to reach a specific status *(i.e. Available after it has been unpaused)*

If there were no operations querying your Redshift cluster after your last ETL job of the day, you could use the 
`RedshiftPauseClusterOperator` to pause your Redshift cluster which would lower your AWS bill. On the first ETL job of 
the day, you could add the `RedshiftResumeClusterOperator` at the beginning of your DAG to send the request to AWS to 
unpause it. Following that task, you could use a `RedshiftClusterSensor` to ensure the cluster is fully available before 
running the remainder of your DAG.
   
The following DAG would effectively pause and unpause a Redshift Cluster. The DAG would only be marked as success once
the cluster has the state of `Available`:

```python
from datetime import datetime
from airflow.models import DAG
from airflow.providers.amazon.aws.operators.redshift_cluster import RedshiftPauseClusterOperator
from airflow.providers.amazon.aws.operators.redshift_cluster import RedshiftResumeClusterOperator
from airflow.providers.amazon.aws.sensors.redshift_cluster import RedshiftClusterSensor


with DAG(
    dag_id=f"example_dag_redshift",
    schedule_interval="@daily",
    start_date=datetime(2008, 1, 1),
    end_date=datetime(2008, 1, 7),
    max_active_runs=1,
    template_searchpath='/usr/local/airflow/include/example_dag_redshift',
    catchup=True
) as dag:
  
    pause_redshift = RedshiftPauseClusterOperator(
        task_id='pause_redshift',
        cluster_identifier='astronomer-success-redshift',
        aws_conn_id='aws_default'
    )
    
    resume_redshift = RedshiftResumeClusterOperator(
      task_id='resume_redshift',
      cluster_identifier='astronomer-success-redshift',
      aws_conn_id='aws_default'
    )

    cluster_sensor = RedshiftClusterSensor(
        task_id='wait_for_cluster',
        cluster_identifier='astronomer-success-redshift',
        target_status='available',
        aws_conn_id='aws_default'
    )

    pause_redshift >> resume_redshift >> cluster_sensor
```
