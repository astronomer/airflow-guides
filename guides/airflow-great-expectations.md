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

[Great Expectations](https://greatexpectations.io) is an open source Python-based data validation framework. It allows you to test your data by expressing what you “expect” from it as simple declarative statements in Python, then run validation using those “expectations” against datasets. The [Great Expectations team maintains an Airflow provider](https://registry.astronomer.io/providers/great-expectations) that gives users a convenient method for running validation directly from their DAGs. This guide will walk you through the usage of the [official GreatExpectationsOperator](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsoperator), usage of the [official GreatExpectationsBigQueryOperator](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsbigqueryoperator), and provide some guidance on how to configure an Airflow DAG containing Great Expectations tasks to work with Airflow.

## PreRequisites

Typically, using Great Expectations is a two-step process:

1. Expectation Suite creation
2. Validation

First, a user creates test suites, or “Expectation Suites”, using [Great Expectations methods](https://docs.greatexpectations.io/en/0.12.0/reference/core_concepts/expectations/expectations.html?highlight=methods#methods-for-creating-and-editing-expectations). These suites are usually stored in JSON and can be checked into version control, just like regular tests. The suites are then loaded by the Great Expectations framework at test runtime, e.g. when processing a new batch of data in a pipeline. If you are using the [demo repository](https://github.com/astronomer/airflow-data-quality-demo/great-expectations) with this guide, then the example suite can be found under `include/great_expectations/expectations/taxi/demo.json`.

> For a step-by-step guide on how to configure a simple Great Expectations project, please see the [“Getting started” tutorial](https://docs.greatexpectations.io/en/latest/guides/tutorials.html).

This walkthrough assumes that you have either:

1. Initialized a Great Expectations project
2. Configured at least one Datasource `my_datasource`
3. Created at least one Expectation Suite `my_suite`
4. Optional: Created a Checkpoint `my_checkpoint`

or that you have downloaded the code from the [demo repository](https://github.com/astronomer/airflow-data-quality-demo/great-expectations), which contains a sample Great Expectations project already.

If you set up a project manually, you will see a `great_expectations` directory which contains several sub-directories, as well as the `great_expectations.yml` configuration file.


> Note: If you are running Airflow 2.0 and beyond, you will need to also change the value of `enable_xcom_pickling` to `true` in your airflow.cfg. If you are using an Astronomer project structure, add `ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True` to your Dockerfile.

## Use Case: Great Expectations Operator

The `GreatExpectationsOperator` provides a convenient method for loading an existing Expectation Suite and using it to validate a batch of data. You can point the operator to any location by setting the `data_context_root_dir` parameter-- more that below. This guide assumes you are using the [demo repository](https://github.com/astronomer/airflow-data-quality-demo/great-expectations), which has the following configuration:

1. The `great_expectations` directory is accessible by your DAG, as it is loaded under the `include` directory and accessed via the variable `ge_root_dir = os.path.join(base_path, "include", "great_expectations")`. Ideally, in any case, it should be located in the same project as your DAG, but you can point the operator at any location.

2. The Great Expectations provider is installed when you run `astro dev start`, as it is part of `requirements.txt`. Otherwise, install Great Expectations and the Great Expectations provider in your environment manually:

    ```bash
    pip install great_expectations airflow-provider-great-expectations
    ```

3. Import the operator in your DAG file.

    ```python
    from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
    ```

4. Create a task using the `GreatExpectationsOperator`.

5. When deploying with Astronomer, it's important to note that Great Expectations needs to know where to find the Data Context by setting the `data_context_root_dir`, which you can then access in the DAG. We recommend adding this variable to your Dockerfile, but you can use [any of the methods described in our docs](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables/) to set environment variables for your deployment.

  ```shell
  ENV GE_DATA_CONTEXT_ROOT_DIR=/usr/local/airflow/include/great_expectations
  ```

The `GreatExpectationsOperator` supports multiple ways of invoking validation with Great Expectations:

- Using an Expectation Suite name and `batch_kwargs`.
- Using a list of Expectation Suite names and `batch_kwargs`.
- Using a Checkpoint.

This means that the parameters you pass to the operator depend on how you would like to invoke Great Expectations validation. The example DAG below shows several different cases of using the operator as variations on the three cases listed above.

```python
with DAG(
    dag_id="example_great_expectations_dag",
    schedule_interval=None,
    default_args=default_args
) as dag:

    # This runs an expectation suite against a sample data asset.
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(
        base_path, "include", "data/yellow_tripdata_sample_2019-01.csv"
    )

    ge_root_dir = os.getenv("GE_DATA_CONTEXT_ROOT_DIR")

    # This runs an expectation suite as a list against a data asset that passes the tests.
    ge_batch_kwargs_list_pass = GreatExpectationsOperator(
        task_id="ge_batch_kwargs_list_pass",
        assets_to_validate=[
            {
                "batch_kwargs": {"path": data_file, "datasource": "data__dir"},
                "expectation_suite_name": "taxi.demo",
            }
        ],
    )

    # This runs a checkpoint and passes in a root dir.
    ge_checkpoint_pass_root_dir = GreatExpectationsOperator(
        task_id="ge_checkpoint_pass_root_dir",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.pass.chk",
    )

    # This runs an expectation suite against a data asset that passes the tests.
    ge_batch_kwargs_pass = GreatExpectationsOperator(
        task_id="ge_batch_kwargs_pass",
        expectation_suite_name="taxi.demo",
        batch_kwargs={"path": data_file, "datasource": "data__dir"},
    )

    # This runs a checkpoint that will fail, but we set a flag to exit the task successfully.
    ge_checkpoint_fail_but_continue = GreatExpectationsOperator(
        task_id="ge_checkpoint_fail_but_continue",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.fail.chk",
        fail_task_on_validation_failure=False,
    )

    # This runs a checkpoint that will pass.
    ge_checkpoint_pass = GreatExpectationsOperator(
        task_id="ge_checkpoint_pass",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.pass.chk",
    )

    # This runs a checkpoint that will fail.
    ge_checkpoint_fail = GreatExpectationsOperator(
        task_id="ge_checkpoint_fail",
        run_name="ge_airflow_run",
        checkpoint_name="taxi.fail.chk",
    )

    (
        ge_batch_kwargs_list_pass
        >> ge_checkpoint_pass_root_dir
        >> ge_batch_kwargs_pass
        >> ge_checkpoint_fail_but_continue
        >> ge_checkpoint_pass
        >> ge_checkpoint_fail
    )
```

> Note: If your `great_expectations` directory is not located in the same directory as your DAG file, you will need to provide the `data_context_root_dir` parameter.

By default, a Great Expectations task will run validation and raise an `AirflowException` if any of the tests fail. To override this behavior and continue running even if tests fail, set the `fail_task_on_validation_failure` flag to `false`.

For more information about possible parameters and examples, see the [README in the repository](https://github.com/great-expectations/airflow-provider-great-expectations), and the [example DAG in the provider package](https://registry.astronomer.io/dags/example-great-expectations-dag).

## Use Case: Great Expectations BigQuery Operator

To set up a BigQuery connection with Airflow, and to make sure the `example_great_expectations_bigquery_dag` runs with an Astronomer deployment, a Google Application Credentials and an Airflow GCP connection are needed.

Under `Admin -> Connections` in the Airflow UI, add a new connection with Conn ID as `google_cloud_default`. The connection type is `Google Cloud`; this connection comes with the Astronomer Airflow distribution. A GCP key associated with a service account that has access to BigQuery is needed. For more information generating a key, [follow the instructions in this guide](https://cloud.google.com/iam/docs/creating-managing-service-account-keys). The key can either be added via a path via the Keyfile Path field, or the JSON can be directly copied and pasted into the Keyfile JSON field. In the case of the Keyfile Path, a relative path is allowed, and if using Astronomer, the recommended path is under the `include/` directory, as Docker will mount all files and directories under it. Make sure the file name is included in the path. Finally, add the project ID to the Project ID field. No scopes should be needed.

For more on configuring environment variables for any credentials required for external data connections, see the [Great Expectations documentation](https://docs.greatexpectations.io/en/latest/guides/how_to_guides/configuring_data_contexts/how_to_use_a_yaml_file_or_environment_variables_to_populate_credentials.html?highlight=environment%20variables), which provides an explanation on using environment variables for Datasource credentials in your `great_expectations.yml` configuration.

3. Finally, you will need to add the environment variables to your local `.env` file and as [secret environment variables in the Astronomer Cloud settings](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables/).
