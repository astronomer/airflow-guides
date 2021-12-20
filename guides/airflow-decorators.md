---
title: "Introduction to Airflow Decorators"
description: "An overview of Airflow decorators and how they can improve the DAG authoring experience."
date: 2022-01-10T00:00:00.000Z
slug: "airflow-decorators"
heroImagePath: null
tags: ["DAGs", "Basics", "astro"]
---

## Overview

Since Airflow 2.0, decorators have been available for some functions as an alternative DAG authoring experience to traditional operators. In Python, [decorators](https://realpython.com/primer-on-python-decorators/) are functions that take another function as an argument and extend the behavior of that function. In the context of Airflow, decorators provide a simpler, cleaner way to define your tasks and DAG. 

In this guide, we'll cover when and why to use decorators, the decorators available in Airflow, and decorators provided in Astronomer's open source `astro` package. We'll show examples throughout and address common questions, like whether you *should* use decorators in certain scenarios, and how to combine decorators with traditional operators in a DAG.

## When and Why To Use Decorators

The goal of decorators in Airflow is to simplify the DAG authoring experience and allow the developer to focus on implementing execution logic without having to think about orchestration logic. The result can be cleaner DAG files that are easier to read and require less code.

Take the following DAG with a simple `PythonOperator` as an example. Using traditional operators, our DAG looks like this:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import random

def _my_function():
    animals = ['dog', 'cat', 'guinea pig']
    return random.choice(animals)

with DAG('classic_dag', 
        schedule_interval='@daily', 
        default_args={
            'start_date': datetime(2021, 12, 31),
        }, 
        catchup=False) as dag:
    
    run_my_function = PythonOperator(
        task_id='run_my_function',
        python_callable=_my_function
    )
```

In this classic DAG authoring style, we have to define our Python function separately from our `PythonOperator` instantiation, meaning we have to write more code and explicitly define orchestration logic (the operator). Rewriting this same DAG using decorators, we can eliminate much of this code:

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule_interval='@daily', default_args={'start_date': datetime(2021, 12, 31),}, catchup=False)
def decorator_dag():

    @task
    def _my_function():
        animals = ['dog', 'cat', 'guinea pig']
        return random.choice(animals)

    _my_function()

dag = decorator_dag()
```

In general, whether to use decorators is a matter of developer preference and style. Generally, a decorator and the corresponding traditional operator will have the same functionality. One exception to this is Astro Project decorators (more on these below), which do not have equivalent traditional operators. You can also easily mix decorators and traditional operators within your DAG if needed to implement your use case.

## Using Airflow Decorators

link to taskflow api webinar
[Taskflow API tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html#tutorial-on-the-taskflow-api)

Marc's example with before/after

### List of Available Decorators

### Mixing Decorators with Traditional Operators

## Astro Project Decorators

Animal adoptions example
