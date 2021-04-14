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

[Great Expectations](https://greatexpectations.io) is an open source Python-based data validation framework. It allows you to test your data by expressing what you “expect” from it as simple declarative statements in Python, then run validation using those “expectations” against datasets. The [Great Expectations team maintains an Airflow provider](https://registry.astronomer.io/providers/great-expectations) that gives users a convenient method for running validation directly from their DAGs. This guide will walk you through the usage of the [official GreatExpectationsOperator](https://registry.astronomer.io/providers/great-expectations/modules/greatexpectationsoperator) and provide some guidance on how to configure an Airflow DAG containing a Great Expectations task to work with Airflow.


## PreRequisites

Typically, using Great Expectations is a two-step process:

1. Expectation Suite creation
2. Validation

First, a user creates test suites, or “Expectation Suites”, using [Great Expectations methods](https://docs.greatexpectations.io/en/0.12.0/reference/core_concepts/expectations/expectations.html?highlight=methods#methods-for-creating-and-editing-expectations). These suites are usually stored in JSON and can be checked into version control, just like regular tests. The suites are then loaded by the Great Expectations framework at test runtime, e.g. when processing a new batch of data in a pipeline.

> For a step-by-step guide on how to configure a simple Great Expectations project, please see the [“Getting started” tutorial](https://docs.greatexpectations.io/en/latest/guides/tutorials.html).

This walkthrough assumes that you have:

1. Initialized a Great Expectations project
2. Configured at least one Datasource `my_datasource`
3. Created at least one Expectation Suite `my_suite`
4. Optional: Created a Checkpoint `my_checkpoint`

After setting up the project, you will see a `great_expectations` directory which contains several sub-directories, as well as the `great_expectations.yml` configuration file. Once that’s done, you can move on to invoking validation from Airflow, as described in the next section.


> Note: If you are running Airflow 2.0 and beyond, you will need to also change the value of `enable_xcom_pickling` to `true` in your airflow.cfg.

## Using the Great Expectations Airflow Operator

The `GreatExpectationsOperator` provides a convenient method for loading an existing Expectation Suite and using it to validate a batch of data. You can point the operator to any location by setting the `data_context_root_dir` parameter-- more that below. In order to use the operator in your DAG, follow these steps:

1. Ensure that the `great_expectations` directory is accessible by your DAG. Ideally, it should be located in the same project as your DAG, but you can point the operator at any location.

2. Install Great Expectations and the Great Expectations provider in your environment.

    ```bash
    pip install great_expectations airflow-provider-great-expectations
    ```

3. Import the operator in your DAG file.

    ```python
    from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
    ```

4. Create a task using the `GreatExpectationsOperator`.

The `GreatExpectationsOperator` supports multiple ways of invoking validation with Great Expectations:

- Using an Expectation Suite name and `batch_kwargs`.
- Using a list of Expectation Suite names and `batch_kwargs`.
- Using a Checkpoint.

This means that the parameters you pass to the operator depend on how you would like to invoke Great Expectations validation. As a simple example, assuming you have a single Expectation Suite `my_suite` and a simple batch of data, such as a database table called `my_table`, you can use the following parameters:

```python
my_ge_task = GreatExpectationsOperator(
    task_id=’my_task’,
    expectation_suite_name='my_suite',
    batch_kwargs={
        'table': ‘my_table’,=
        'datasource': ‘my_datasource’
    },
    dag=dag
)
```

> Note: If your `great_expectations` directory is not located in the same directory as your DAG file, you will need to provide the `data_context_root_dir` parameter.

By default, a Great Expectations task will run validation and raise an `AirflowException` if any of the tests fail. To override this behavior and continue running even if tests fail, set the `fail_task_on_validation_failure` flag to `false`.

For more information about possible parameters and examples, see the [README in the repository](https://github.com/great-expectations/airflow-provider-great-expectations), and the [example DAG in the provider package](https://github.com/great-expectations/airflow-provider-great-expectations/tree/main/great_expectations_provider/examples).

## Using the Great Expectations Operator in an Astronomer Airflow Deployment

There are only few additional requirements to deploy a DAG with the Great Expectations operator with Astronomer. Most importantly, you will need to set relevant environment variables.

1. Great Expectations needs to know where to find the Data Context  by setting the `data_context_root_dir`, which you can then access in the DAG. We recommend adding this variable to your Dockerfile, but you can use [any of the methods described in our docs](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables/) to set environment variables for your deployment.

    ```shell
    ENV GE_DATA_CONTEXT_ROOT_DIR=/usr/local/airflow/include/great_expectations
    ```

2. You will need to configure environment variables for any credentials required for external data connections. See the [Great Expectations documentation](https://docs.greatexpectations.io/en/latest/guides/how_to_guides/configuring_data_contexts/how_to_use_a_yaml_file_or_environment_variables_to_populate_credentials.html?highlight=environment%20variables) for an explanation on using environment variables for Datasource credentials in your `great_expectations.yml` configuration.

3. Finally, you will need to add the environment variables to your local `.env` file and as [secret environment variables in the Astronomer Cloud settings](https://www.astronomer.io/docs/cloud/stable/deploy/environment-variables/).
