---
title: Core Apache Airflow Concepts
sidebar: platform_sidebar
---

## Apache Airflow
Airflow is a platform to programmatically author, schedule and monitor workflows.

When workflows are defined as code, they become more maintainable, versionable, testable, and collaborative.

Airflow is **not** a data streaming solution. Airflow is not in the Spark Streaming or Storm space, it is more comparable to Oozie or Azkaban.

## DAGs
Workflows in Airflow are designed as  `DAGs` - or Directed Acyclic Graphs.
A `DAG` is a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies.

For example, a simple DAG could consist of 3 tasks: A, B, and C. It could say that A has to run successfully before B can run, but C can run anytime. It could also say that A times out after 5 minutes and that B can be restarted up to 5 times in case it fails. It might also say that the workflow will run every night at 10pm but shouldn't start until a certain date.

![alt_text](http://michal.karzynski.pl/images/illustrations/2017-03-19/airflow-example-dag.png)

_[An example Airflow Pipeline DAG](http://michal.karzynski.pl/blog/2017/03/19/developing-workflows-with-apache-airflow/)_

Notice that the DAG we just outlined only describes _how_ to carry out a workflow, not _what_ we want the workflow to actually do - A, B, and C could really be anything! DAGs aren't concerned with what its constituent tasks do, they just make sure the tasks happen at the right time, in the right order, and with the right handling of any unexpected issues. **Airflow DAGs are a framework to express how tasks relate to each other, regardless of the tasks themselves.**

## Hooks and Operators
Airflow DAGs are made up of `tasks`, which consist of `hooks` and `operators`.

## Hooks

`Hooks` are interfaces to external APIs (Google Analytics, SalesForce, etc.), databases (MySQL, Postgres, etc.), and other external platforms.

Whereas hooks are the interfaces, `Operators` determine what your DAG actually does.

## Operators
The atomic units of DAGs - while DAGs describe _how_ to run a workflow, `Operators` determine _what actually gets done._

Operators describe single tasks in a workflow and can usually stand on their own, meaning they don't need to share resources (or even a machine in some cases) with any other operators.

**Note:** In general, if two operators need to share information (e.g. a filename or a small amount of data), you should consider combining them into a single operator.

Here are some common operators and the tasks they accomplish:

* `BashOperator` - executes a bash command
* `EmailOperator` - sends an email
* `PythonOperator` - executes Python code

## Tasks
Once an operator is instantiated, it is referred to as a `task`. The instantiation defines specific values when calling the abstract operator, and the parameterized task becomes a node in a DAG. Each task must have a `task_id` that serves as a unique identifier and an `owner`.

**Note**: Be sure that `task_ids` aren't duplicated when dynamically generating DAGs - your DAG may not throw error if there is a duplicated `task_id`, but it definitely wont' execute properly.

### Task Instances
An executed task is called a `TaskInstance`. This represents a specific run of a task and is a combination of a DAG, at task, and a specific point in time.

Task instances also have indicative states, which could be "running", "success", "failed", "skipped", "up for retry", etc.

## Workflows
By stringing together operators and how they depend on each other, you can build workflows in the form of `DAGs`.

## Templating with Jinja
Imagine you want to reference a unique s3 file name that corresponds to the date of the DAG run, how would you do so without hardcoding any paths?

Jinja is a template engine for Python and Apache Airflow uses it to provide pipeline authors with a set of built-in parameters and macros.

A jinja template is simply a text file that contains the following:
 * **variables** and/or **expressions** - these get replaced with values when a template is rendered.
 * **tags** - these control the logic of the template.

In Jinja, the default delimiters are configured as follows:

{% raw %}
 * `{{% ... %}}` for Statements
 * `{{ ... }}` for Expressions
 * `{{# ... #}}` for Comments
 * `# ... ##` for Line Statements
 {% endraw %}

Head [here](http://jinja.pocoo.org/docs/2.9/) for more information about installing and using Jinja.

Jinja templating allows you to defer the rendering of strings in your tasks until the actual running of those tasks. This becomes particularly useful when you want to access certain parameters of a `task_run` itself (i.e. `run_date` or `file_name`).

Not all parameters in operators are templated, so you cannot use Jinja templates everywhere by default.
However, you can add code in your operator to add any fields you need to template:

**Note:** Your Jinja templates can be affected by other parts of your DAG. For example, if your DAG is scheduled to run '@once',  `next_execution_date` and `previous_execution_date` macros will be `None` since your DAG is defined to run just once.

```python
template_fields = ('mission', 'commander')
```


### Example

~~~ python
date = {% raw %}"{{ ds }}"{% endraw %}

t = BashOperator(
        task_id='test_env',
        bash_command='/tmp/test.sh',
        dag=dag,
        env={'EXECUTION_DATE: date}
)
~~~

In the example above, we passed the execution `date` as an environment variable to a Bash script. Since {% raw %} `{{ ds }}` {% endraw %} is a macro and the `env` parameter of the `BashOperator` is templated with Jinja, the execution date will be available as an environment variable named `EXECUTION_DATE` in the Bash script.

**Note:** Astronomer's architecture is built in a way so that a task's container is spun down as soon as the task is completed. So, if you're trying to do something like download a file with one task and then upload that same task with another, you'll need to create a combined Operator that does both.

## XComs
XComs (short for "cross-communication") can be used to pass information between tasks **that are not known at runtime**. This is a differentiating factor between XComs and Jinja templating. If the config you are trying to pass is available at run-time, then we recommend using Jinja templating as it is much more lightweight than XComs. On the flip-side, XComs can be stored indefinitely, give you more nuanced control and should be used when Jinja templating no longer meets your needs.

Functionally, XComs can almost be thought of as dictionaries. They are defined by a `key`, a `value`, and a `timestamp` and have associated metadata about the task/DAG run that created the XCom and when it should become visible.

As shown in the example below, XComs can be called with either `xcom_push()` or `xcom_pull()`. "Pushing" (or sending) an XCom generally makes it available for other tasks while "Pulling" retrieves an XCom. When pulling XComs, you can apply filters based on criteria like `key`, source `task_ids`, and source `dag_id`.

### Example XCom ([reference](https://github.com/apache/incubator-airflow/blob/master/airflow/example_dags/example_xcom.py)):

~~~ python
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

args = {
  'owner': 'airflow',
  'start_date': airflow.utils.dates.days_ago(2),
  'provide_context': True
}

dag = DAG(
    'example_xcom',
    schedule_interval='@once',
    default_args=args
)

value_1 = [1, 2, 3]
value_2 = {'a': 'b'}

def push(**kwargs):
    # pushes an XCom without a specific target
    kwargs['ti'].xcom_push(key='value from pusher 1', value=value_1)

def push_by_returning(**kwargs):
    # pushes an XCom without a specific target, just by returning it
    return value_2

def puller(**kwargs):
    ti = kwargs['ti']

    # get value_1
    v1 = ti.xcom_pull(key=None, task_ids='push')
    assert v1 == value_1

    # get value_2
    v2 = ti.xcom_pull(task_ids='push_by_returning')
    assert v2 == value_2

    # get both value_1 and value_2
    v1, v2 = ti.xcom_pull(key=None, task_ids=['push', 'push_by_returning'])
    assert (v1, v2) == (value_1, value_2)

push1 = PythonOperator(
    task_id='push', dag=dag, python_callable=push)

push2 = PythonOperator(
    task_id='push_by_returning', dag=dag, python_callable=push_by_returning)

pull = PythonOperator(
    task_id='puller', dag=dag, python_callable=puller)

pull.set_upstream([push1, push2])
~~~

A few things to note about XComs:
 * Any object that can be pickled can be used as an XCom value, so be sure to use objects of appropriate size.
 * If a task returns a value (either from its Operator's `execute()` method, or from a PythonOperator's `python_callable` function), than an XCom containing that value is automatically pushed. When this occurs, `xcom_pull()` automatically filters for the keys that are given to the XCom when it was pushed.
 *  If `xcom_pull` is passed a single string for `task_ids`, then the most recent XCom value from that task is returned; if a list of `task_ids` is passed, then a corresponding list of XCom values is returned.

## Other Core concepts

### Default Arguments
If a dictionary of `default_args` is passed to a DAG, it will apply them to any of its operators. This makes it easy to apply a common parameter (e.g. start_date) to many operators without having to retype it.

~~~ python
from datetime import datetime, timedelta
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2017, 3, 14),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
~~~

### Context Manager
DAGs can be used as context managers to automatically assign new operators to that DAG.

### DAG Assignment
Operators do not have to be assigned to DAGs immediately. DAG assignment can be done explicitly when the operator is created, through deferred assignment, or even inferred from other operators.

### Additional Functionality
In addition to these core concepts, Airflow has a number of more complex features. More detail on these functionalities is available [here](http://airflow.incubator.apache.org/concepts.html#additional-functionality).

Sources:

  * [Airflow Concepts](https://airflow.incubator.apache.org/concepts.html?highlight=core%20airflow%20concepts)
  * [Integrating Apache Airflow with Databricks](https://databricks.com/blog/2017/07/19/integrating-apache-airflow-with-databricks.html)
  * [Get started developing workflows with Apache Airflow](http://michal.karzynski.pl/blog/2017/03/19/developing-workflows-with-apache-airflow/)
