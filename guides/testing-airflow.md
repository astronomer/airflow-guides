---
title: "Testing Airflow DAGs"
description: "How to apply test-driven development practices to your Airflow DAGs."
date: 2021-05-25T00:00:00.000Z
slug: "testing-airflow"
heroImagePath: "https://assets2.astronomer.io/main/guides/testing-airflow-dags.png"
tags: ["DAGs", "Best Practices", "Testing"]
---

## Overview

One of the core principles of Airflow is that your DAGs are defined as Python code. Because you can treat data pipelines like you would any other piece of code, you can integrate them into a standard software development lifecycle using source control, CI/CD, and automated testing. 

Although DAGs are 100% Python code, effectively testing DAGs requires accounting for their unique structure and relationship to other code and data in your environment.  In this guide, we'll discuss a couple of types of tests that we would recommend to anybody running Airflow in production, including DAG validation testing, unit testing, and data and pipeline integrity testing.

### Before you begin

If you are newer to test-driven development, or CI/CD in general, we'd recommend the following resources to get started:

- [Getting Started with Testing in Python](https://realpython.com/python-testing/)
- [Continuous Integration with Python](https://realpython.com/python-continuous-integration/)
- [The Challenge of Testing Data Pipelines](https://medium.com/slalom-build/the-challenge-of-testing-data-pipelines-4450744a84f1)
- [Deploying to Astro via CI/CD](https://docs.astronomer.io/software/ci-cd)

We also recommend checking out [Airflow's documentation on testing DAGs](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#testing-a-dag) and [testing guidelines for contributors](https://github.com/apache/airflow/blob/main/TESTING.rst); we'll walk through some of the concepts covered in those docs in more detail below.

### Note on test runners

Before we dive into different types of tests for Airflow, we have a quick note on test runners. There are multiple test runners available for Python, including `unittest`, `pytest`, and `nose2`. The OSS Airflow project uses `pytest`, so we will do the same in this guide. However, Airflow doesn't require using a specific test runner. In general, choosing a test runner is a matter of personal preference and experience level, and some test runners might work better than others for a given use case.

## DAG Validation Testing

DAG validation tests are designed to ensure that your DAG objects are defined correctly, acyclic, and free from import errors. 

These are things that you would likely catch if you were starting with local development of your DAGs. But in cases where you may not have access to a local Airflow environment, or you want an extra layer of security, these tests can ensure that simple coding errors don't get deployed and slow down your development. 

DAG validation tests apply to all DAGs in your Airflow environment, so you only need to create one test suite.

To test whether your DAG can be loaded, meaning there aren't any syntax errors, you can simply run the Python file:

```bash
python your-dag-file.py
```

Or to test for import errors specifically (which might be syntax related, but could also be due to incorrect package import paths, etc.), you can use something like the following:

```python
import pytest
from airflow.models import DagBag

def test_no_import_errors():
  dag_bag = DagBag()
  assert len(dag_bag.import_errors) == 0, "No Import Failures"
```

You may also use DAG validation tests to test for properties that you want to be consistent across all DAGs. For example, if your team has a rule that all DAGs must have two retries for each task, you might write a test like this to enforce that rule:

```python
def test_retries_present():
  dag_bag = DagBag()
  for dag in dag_bag.dags:
      retries = dag_bag.dags[dag].default_args.get('retries', [])
      error_msg = 'Retries not set to 2 for DAG {id}'.format(id=dag)
      assert retries == 2, error_msg
```

To see an example of running these tests as part of a CI/CD workflow, check out [this repo](https://github.com/astronomer/airflow-testing-guide), which uses GitHub Actions to run the test suite before deploying the project to an Astronomer Airflow deployment.

## Unit Testing

[Unit testing](https://en.wikipedia.org/wiki/Unit_testing) is a software testing method where small chunks of source code are tested individually to ensure they function as intended. The goal is to isolate testable logic inside of small, well-named functions, for example:

```python
def test_function_returns_5():
	assert my_function(input) == 5
```

In the context of Airflow, you can write unit tests for any part of your DAG, but they are most frequently applied to hooks and operators. All official Airflow hooks, operators, and provider packages have unit tests that must pass before merging the code into the project. For an example, check out the [AWS `S3Hook`](https://registry.astronomer.io/providers/amazon/modules/s3hook), which has many accompanying [unit tests](https://github.com/apache/airflow/blob/main/tests/providers/amazon/aws/hooks/test_s3.py). 

If you have your own custom hooks or operators, we highly recommend using unit tests to check logic and functionality. For example, say we have a custom operator that checks if a number is even:

```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class EvenNumberCheckOperator(BaseOperator):
    @apply_defaults
    def __init__(self, my_operator_param, *args, **kwargs):
        self.operator_param = my_operator_param
        super(EvenNumberCheckOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
				if self.operator_param % 2:
						return True
        else:
						return False
```

We would then write a `test_evencheckoperator.py` file with unit tests like the following:

```python
import unittest
import pytest
from datetime import datetime
from airflow import DAG
from airflow.models import TaskInstance
from airflow.operators import EvenNumberCheckOperator

DEFAULT_DATE = datetime(2021, 1, 1)

class EvenNumberCheckOperator(unittest.TestCase):

	def setUp(self):
      super().setUp()
      self.dag = DAG('test_dag', default_args={'owner': 'airflow', 'start_date': DEFAULT_DATE})
			self.even = 10
			self.odd = 11

	def test_even(self):
      """Tests that the EvenNumberCheckOperator returns True for 10."""
      task = EvenNumberCheckOperator(my_operator_param=self.even, task_id='even', dag=self.dag)
      ti = TaskInstance(task=task, execution_date=datetime.now())
      result = task.execute(ti.get_template_context())
      assert result is True

	def test_odd(self):
      """Tests that the EvenNumberCheckOperator returns False for 11."""
      task = EvenNumberCheckOperator(my_operator_param=self.odd, task_id='odd', dag=self.dag)
      ti = TaskInstance(task=task, execution_date=datetime.now())
      result = task.execute(ti.get_template_context())
      assert result is False
```

Note that if your DAGs contain `PythonOperators` that execute your own Python functions, it is a good idea to write unit tests for those functions as well. 

The most common way of implementing unit tests in production is to automate them as part of your CI/CD process. Your CI tool executes the tests and stops the deployment process if any errors occur.

### Mocking

Sometimes unit tests require mocking: the imitation of an external system, dataset, or other object. For example, you might use mocking with an Airflow unit test if you are testing a connection, but don't have access to the metadata database. Another example could be if you are testing an operator that executes an external service through an API endpoint, but you don't want to actually wait for that service to run a simple test. 

Many [Airflow tests](https://github.com/apache/airflow/tree/master/tests) have examples of mocking. [This blog post](https://godatadriven.com/blog/testing-and-debugging-apache-airflow/) also has a useful section on mocking Airflow that may be helpful for getting started.

## Data Integrity Testing

Data integrity tests are designed to prevent data quality issues from breaking your pipelines or negatively impacting downstream systems. These tests could also be used to ensure your DAG tasks produce the expected output when processing a given piece of data. They are somewhat different in scope than the code-related tests described in previous sections, since your data is not static like a DAG. 

One straightforward way of implementing data integrity tests is to build them directly into your DAGs. This allows you to make use of Airflow dependencies to manage any errant data in whatever way makes sense for your use case.

There are many ways you could integrate data checks into your DAG. One method worth calling out is using [Great Expectations](https://greatexpectations.io/) (GE), an open source Python framework for data validations. You can make use of the [Great Expectations provider package](https://registry.astronomer.io/providers/great-expectations) to easily integrate GE tasks into your DAGs. In practice, you might have something like the following DAG, which runs an Azure Data Factory pipeline that generates data, then runs a GE check on the data before sending an email.

```python
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.microsoft.azure.hooks.azure_data_factory import AzureDataFactoryHook
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

#Get yesterday's date, in the correct format
yesterday_date = '{{ yesterday_ds_nodash }}'

#Define Great Expectations file paths
data_dir = '/usr/local/airflow/include/data/'
data_file_path = '/usr/local/airflow/include/data/'
ge_root_dir = '/usr/local/airflow/include/great_expectations'

def run_adf_pipeline(pipeline_name, date):
    '''Runs an Azure Data Factory pipeline using the AzureDataFactoryHook and passes in a date parameter
    '''
    
    #Create a dictionary with date parameter 
    params = {}
    params["date"] = date

    #Make connection to ADF, and run pipeline with parameter
    hook = AzureDataFactoryHook('azure_data_factory_conn')
    hook.run_pipeline(pipeline_name, parameters=params)

def get_azure_blob_files(blobname, output_filename):
    '''Downloads file from Azure blob storage
    '''
    azure = WasbHook(wasb_conn_id='azure_blob')
    azure.get_file(output_filename, container_name='covid-data', blob_name=blobname)
    

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

with DAG('adf_great_expectations',
         start_date=datetime(2021, 1, 1),
         max_active_runs=1,
         schedule_interval='@daily', 
         default_args=default_args,
         catchup=False
         ) as dag:

         run_pipeline = PythonOperator(
            task_id='run_pipeline',
            python_callable=run_adf_pipeline,
            op_kwargs={'pipeline_name': 'pipeline1', 'date': yesterday_date}
         )

         download_data = PythonOperator(
            task_id='download_data',
            python_callable=get_azure_blob_files,
            op_kwargs={'blobname': 'or/'+ yesterday_date +'.csv', 'output_filename': data_file_path+'or_'+yesterday_date+'.csv'}
         )

         ge_check = GreatExpectationsOperator(
            task_id='ge_checkpoint',
            expectation_suite_name='azure.demo',
            batch_kwargs={
                'path': data_file_path+'or_'+yesterday_date+'.csv',
                'datasource': 'data__dir'
            },
            data_context_root_dir=ge_root_dir
        )

         send_email = EmailOperator(
            task_id='send_email',
            to='noreply@astronomer.io',
            subject='Covid to S3 DAG',
            html_content='<p>The great expectations checks passed successfully. <p>'
        )

         run_pipeline >> download_data >> ge_check >> send_email
```

If the GE check fails, any downstream tasks will be skipped. Implementing checkpoints like this allows you to either conditionally branch your pipeline to deal with data that doesn't meet your criteria, or potentially skip all downstream tasks so problematic data won't be loaded into your data warehouse or fed to a model. For more information on conditional DAG design, check out the documentation on [Airflow Trigger Rules](https://airflow.apache.org/docs/apache-airflow/2.0.0/concepts.html#trigger-rules) and our guide on [branching in Airflow](https://www.astronomer.io/guides/airflow-branch-operator).

It's also worth noting here that data integrity testing will work better at scale if you design your DAGs to load or process data incrementally. We talk more about incremental loading in our [Airflow Best Practices guide](https://www.astronomer.io/guides/dag-best-practices), but in short, processing smaller, incremental chunks of your data in each DAG Run ensures that any data quality issues have a limited blast radius and are easier to recover from.
