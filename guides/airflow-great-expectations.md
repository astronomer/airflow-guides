---
title: "Integrating Airflow and Great Expectations"
description: "Using the Great Expectations provider natively in your Airflow DAGs."
date: 2020-11-22T00:00:00.000Z
slug: "airflow-great-expectations"
heroImagePath: "https://assets2.astronomer.io/main/guides/airflow-ge.png"
tags: ["DAGs", "Integrations"]
---

> You can now find the [Great Expectations Provider](https://registry.astronomer.io/providers/great-expectations) on the [Astronomer Registry](https://registry.astronomer.io), the discovery and distribution hub for Apache Airflow integrations created to aggregate and curate the best bits of the ecosystem.

## Overview

[Great Expectations](https://greatexpectations.io) is an open source Python-based data validation framework. It allows you to test your data by expressing what you “expect” from it as simple declarative statements in Python, then run validation using those “expectations” against datasets. The [Great Expectations team maintains an Airflow provider](https://registry.astronomer.io/providers/great-expectations) that gives users a convenient method for running validation directly from their DAGs.

This guide will walk through how to use the [official `GreatExpectationsOperato`r](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsoperator), how to use the [official `GreatExpectationsBigQueryOperator`](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsbigqueryoperator), and how to configure an Airflow DAG containing Great Expectations tasks to work with Airflow.

## Great Expectations Concepts

Typically, using Great Expectations is a two-step process:

1. Expectation Suite creation
2. Validation

First, a user creates test suites, or “Expectation Suites”, using [Great Expectations methods](https://docs.greatexpectations.io/docs/reference/expectations/expectations/). These suites are usually stored in JSON and can be checked into version control, just like regular tests. The suites are then loaded by the Great Expectations framework at test runtime, e.g. when processing a new batch of data in a pipeline.

> For a step-by-step guide on how to configure a simple Great Expectations project, please see the [“Getting started” tutorial](https://docs.greatexpectations.io/en/latest/guides/tutorials.html).

## Setup

This walkthrough assumes that you have downloaded the code from the [demo repository](https://github.com/astronomer/airflow-data-quality-demo/) which contains a sample Great Expectations project.

If you wish to use your own Great Expectations project along with this guide, ensure you have completed the following steps:

1. Initialized a Great Expectations project
2. Configured at least one Datasource `my_datasource`
3. Created at least one Expectation Suite `my_suite`
4. Optional: Created a Checkpoint `my_checkpoint`

If you set up a project manually, you will see a `great_expectations` directory which contains several sub-directories, as well as the `great_expectations.yml` configuration file. If you cloned the demo repository, the `great_expectations` directory can be found under `include/`.


> Note: If you are running Airflow 2.0 and beyond, you will need to also change the value of `enable_xcom_pickling` to `true` in your airflow.cfg. If you are using an Astronomer project structure, add `ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True` to your Dockerfile. If you are working from the demo repository, this step has already been completed for you.

## Use Case: Great Expectations Operator

Now that we've set up our system to work with Great Expectations, we can start exploring how to use it in our DAGs. In this first use case, we'll use the `GreatExpectationsOperator` to run an Expectation Suite.

### Configuration

The `GreatExpectationsOperator` provides a convenient method for loading an existing Expectation Suite and using it to validate a batch of data. You can point the operator to any location by setting the `data_context_root_dir` parameter (more on that to follow). Our [demo repository](https://github.com/astronomer/airflow-data-quality-demo/) uses the following configuration:

- The `great_expectations` directory is accessible by your DAG, as it is loaded into Docker as part of the `include` directory. Ideally the `great_expectations` directory should be located in the same project as your DAG, but you can point the environment variable at any location.
- The Great Expectations provider is installed when you run `astro dev start`, as it is part of `requirements.txt`. Otherwise, install Great Expectations and the Great Expectations provider in your environment manually:

    ```bash
    pip install great_expectations airflow-provider-great-expectations
    ```

- When deploying with Astronomer, it's important to note that Great Expectations needs to know where to find the Data Context by setting the `data_context_root_dir`, which you can then access in the DAG. We recommend adding this variable to your Dockerfile, but you can use [any of the methods described in our docs](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables/) to set environment variables for your deployment:

  ```shell
  ENV GE_DATA_CONTEXT_ROOT_DIR=/usr/local/airflow/include/great_expectations
  ```

   If you are using the demo repository, then this variable has already been set in the Dockerfile to this location.

### Using the Great Expectations Operator

1. Import the operator in your DAG file.

    ```python
    from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
    ```

2. Create a task using the [`GreatExpectationsOperator`](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsoperator).


The `GreatExpectationsOperator` supports multiple ways of invoking validation with Great Expectations:

- Using an Expectation Suite name and `batch_kwargs`.
- Using a list of Expectation Suite names and `batch_kwargs`.
- Using a Checkpoint.

The method you use for invoking validation determines which parameters you should pass to the operator. The following example DAG shows how you would implement each of these methods in your code:

```python
with DAG(
    dag_id="example_great_expectations_dag",
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    default_args={"data_context_root_dir": ge_root_dir}
) as dag:

    """
    ### Simple Great Expectations Example
    """

    """
    #### This runs an expectation suite against a data asset that passes the tests
    """
    ge_batch_kwargs_list_pass = GreatExpectationsOperator(
        task_id="ge_batch_kwargs_list_pass",
        assets_to_validate=[
            {
                "batch_kwargs": {"path": data_file, "datasource": "data__dir"},
                "expectation_suite_name": "taxi.demo",
            }
        ]
    )

    """
    #### This runs a checkpoint and passes in a root dir
    """
    ge_checkpoint_pass_root_dir = GreatExpectationsOperator(
        task_id="ge_checkpoint_pass_root_dir",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.pass.chk"
    )

    """
    #### This runs an expectation suite using the batch_kwargs parameter
    """
    ge_batch_kwargs_pass = GreatExpectationsOperator(
        task_id="ge_batch_kwargs_pass",
        expectation_suite_name="taxi.demo",
        batch_kwargs={"path": data_file, "datasource": "data__dir"}
    )

    """
    #### This runs a checkpoint that will fail, but we set a flag to exit the
         task successfully.
    """
    ge_checkpoint_fail_but_continue = GreatExpectationsOperator(
        task_id="ge_checkpoint_fail_but_continue",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.fail.chk",
        fail_task_on_validation_failure=False
    )

    """
    #### This runs a checkpoint that will pass. Make sure the checkpoint yml file
         has the correct path to the data file
    """
    ge_checkpoint_pass = GreatExpectationsOperator(
        task_id="ge_checkpoint_pass",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.pass.chk"
    )

    """
    #### This runs a checkpoint that will fail. Make sure the checkpoint yml file
         has the correct path to the data file
    """
    ge_checkpoint_fail = GreatExpectationsOperator(
        task_id="ge_checkpoint_fail",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.fail.chk"
    )

    chain(
        ge_batch_kwargs_list_pass, ge_checkpoint_pass_root_dir, ge_batch_kwargs_pass,
        ge_checkpoint_fail_but_continue, ge_checkpoint_pass, ge_checkpoint_fail
    )
```

By default, a Great Expectations task will run validation and raise an `AirflowException` if any of the tests fail. To override this behavior and continue running even if tests fail, set the `fail_task_on_validation_failure` flag to `false`.

For more information about possible parameters and examples, see the [README in the provider repository](https://github.com/great-expectations/airflow-provider-great-expectations) and the [example DAG in the provider package](https://registry.astronomer.io/dags/example-great-expectations-dag).

## Use Case: Great Expectations BigQuery Operator

In the second use case, we'll use the `GreatExpectationsBigQueryOperator` to run an Expectation Suite on data that is already loaded into BigQuery.

### Prerequisites

The `GreatExpectationsBigQueryOperator` requires the Google Provider Package, which comes with the Astronomer Core Airflow Distribution. To run the Astronomer Core Airflow Distribution:

- Ensure you have the [Astronomer CLI](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart) installed.
- If you are using the demo repository, simply run `astro dev start`. Otherwise, run `astro dev init` first.  

Additionally, a GCP key associated with a service account that has access to BigQuery and Google Cloud Storage is needed. For more information generating a key, [follow the instructions in this guide](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

### Using the Great Expectations BigQuery Operator

The [`GreatExpectationsBigQueryOperator`](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsbigqueryoperator) allows you to run Great Expectation suites directly on tables in BigQuery or on a subset of data chosen by an SQL query. The test suites are stored in Google Cloud Storage, so the entire process can run in the cloud.

1. In the Airflow UI, go to **Admin** > **Connections** and add a new connection with `Conn ID` set to `google_cloud_default`.
2. Set the connection type to `Google Cloud`. This connection type comes with the Astronomer Airflow distribution.
3. The GCP key can either be added as a path via the `Keyfile Path` field, or the JSON contents can be directly copied and pasted into the `Keyfile JSON` field. In the case of the `Keyfile Path`, a relative path is allowed, and if using Astronomer, the recommended path is under the `include/` directory, as Docker will mount all files and directories under it. Make sure the file name is included in the path.
4. Add the project ID to the `Project ID` field.
  The connection should look like this:
![GCP Connection](https://assets2.astronomer.io/main/guides/great-expectations/gcp_connection.png)
5. Add an environment variable to the project Dockerfile or `.env` file that points to your GCP key with permissions to read and write from Google Cloud Storage and BigQuery. The entry in the Dockerfile will look like:

  `ENV GOOGLE_APPLICATION_CREDENTIALS=/usr/local/airflow/include/keys/your-google-cloud-key.json`

> Note: For more on configuring environment variables for any credentials required for external data connections, see the [Great Expectations documentation](https://docs.greatexpectations.io/en/latest/guides/how_to_guides/configuring_data_contexts/how_to_use_a_yaml_file_or_environment_variables_to_populate_credentials.html?highlight=environment%20variables), which provides an explanation on using environment variables for Datasource credentials in your `great_expectations.yml` configuration.

With the connection to GCP set, the next step is creating and running the DAG. In the example below, the DAG:

1. Creates a BigQuery dataset for the sample table.
2. Creates a BigQuery table and inserts the sample data.
3. Uploads the test suite to GCS.
4. Runs the Expectation suite on the table.
5. Tears down the table and dataset.

The example DAG below can be seen in full in Astronomer's [data quality repository](https://github.com/astronomer/airflow-data-quality-demo/tree/main/dags/great_expectations/).

```python
with DAG("great_expectations_bigquery_example",
         description="Example DAG showcasing loading and data quality checking with BigQuery and Great Expectations.",
         schedule_interval=None,
         start_date=datetime(2021, 1, 1),
         catchup=False) as dag:
    """
    ### Simple EL Pipeline with Data Quality Checks Using BigQuery and Great Expectations
    """

    """
    #### BigQuery dataset creation
    Create the dataset to store the sample data tables.
    """
    create_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset",
        dataset_id=BQ_DATASET
    )

    """
    #### Upload taxi data to GCS
    Upload the test data to GCS so it can be transferred to BigQuery.
    """
    upload_taxi_data = LocalFilesystemToGCSOperator(
        task_id="upload_taxi_data",
        src=DATA_FILE,
        dst=GCP_DATA_DEST,
        bucket=GCP_BUCKET,
    )

    """
    #### Transfer data from GCS to BigQuery
    Moves the data uploaded to GCS in the previous step to BigQuery, where
    Great Expectations can run a test suite against it.
    """
    transfer_taxi_data = GCSToBigQueryOperator(
        task_id="taxi_data_gcs_to_bigquery",
        bucket=GCP_BUCKET,
        source_objects=[GCP_DATA_DEST],
        skip_leading_rows=1,
        destination_project_dataset_table="{}.{}".format(BQ_DATASET, BQ_TABLE),
        schema_fields=[
            {"name": "vendor_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "pickup_datetime", "type": "DATETIME", "mode": "NULLABLE"},
            {"name": "dropoff_datetime", "type": "DATETIME", "mode": "NULLABLE"},
            {"name": "passenger_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "trip_distance", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "rate_code_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "store_and_fwd_flag", "type": "STRING", "mode": "NULLABLE"},
            {"name": "pickup_location_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "dropoff_location_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "payment_type", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "fare_amount", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "extra", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "mta_tax", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "tip_amount", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "tolls_amount", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "improvement_surcharge", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "total_amount", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "congestion_surcharge", "type": "FLOAT", "mode": "NULLABLE"}
        ],
        source_format="CSV",
        create_disposition="CREATE_IF_NEEDED",
        write_disposition="WRITE_TRUNCATE",
        allow_jagged_rows=True
    )

    """
    #### Upload test suite to GCS
    The GreatExpectationsBigQueryOperator expects the test suite to reside in
    GCS, so the local file gets uploaded to GCS here.
    """
    upload_expectations_suite = LocalFilesystemToGCSOperator(
        task_id="upload_test_suite",
        src=EXPECTATION_FILE,
        dst=GCP_SUITE_DEST,
        bucket=GCP_BUCKET,
    )

    """
    #### Great Expectations suite
    Run the Great Expectations suite on the table.
    """
    ge_bigquery_validation = GreatExpectationsBigQueryOperator(
        task_id="ge_bigquery_validation",
        gcp_project="{{ var.value.gcp_project_id }}",
        gcs_bucket=GCP_BUCKET,
        # GE will use a folder "$my_bucket/expectations"
        gcs_expectations_prefix="expectations",
        # GE will use a folder "$my_bucket/validations"
        gcs_validations_prefix="validations",
        # GE will use a folder "$my_bucket/data_docs"
        gcs_datadocs_prefix="data_docs",
        # GE will look for a file $my_bucket/expectations/taxi/demo.json
        expectation_suite_name="taxi.demo",
        table=BQ_TABLE,
        bq_dataset_name=BQ_DATASET,
        bigquery_conn_id="google_cloud_default"
    )

    """
    #### Delete test dataset and table
    Clean up the dataset and table created for the example.
    """
    delete_dataset = BigQueryDeleteDatasetOperator(
        task_id="delete_dataset",
        project_id="{{ var.value.gcp_project_id }}",
        dataset_id=BQ_DATASET,
        delete_contents=True
    )

    begin = DummyOperator(task_id="begin")
    end = DummyOperator(task_id="end")

    chain(begin, create_dataset, upload_taxi_data, transfer_taxi_data,
          upload_expectations_suite, ge_bigquery_validation, delete_dataset, end)
```

The above example DAG shows how Airflow can be used to orchestrate in-depth data quality checks with Great Expectations as part of a full ELT pipeline. When we run this DAG, we see how data can be loaded and checked with BigQuery and Great Expectations in a single pipeline. A next step is to configure the Great Expectations suite for your own use case, and let Airflow ensure your data quality checks run smoothly on any schedule.
