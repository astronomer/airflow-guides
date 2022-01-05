---
title: "Templating in Airflow"
description: "How to leverage the power of Jinja templating when writing your DAGs."
date: 2018-05-23T00:00:00.000Z
slug: "templating"
heroImagePath: null
tags: ["Templating", "Best Practices", "Basics"]
---

## Overview

Templating is a powerful concept in Airflow to pass dynamic information into task instances at runtime. For example, say you want to print the day of the week every time you run a task:

```python
BashOperator(
    task_id="print_day_of_week",
    bash_command="echo Today is {{ execution_date.format('dddd') }}",
)
```

In this example, the value in the double curly braces `{{ }}` is our templated code to be evaluated at runtime. If we execute this code on a Wednesday, the BashOperator will print "Today is Wednesday". Templating is important across many use cases. For example, we can use templating to create a new directory named after a task's execution date for storing daily data (e.g. `/data/path/20210824`), or we can select a specific partition (e.g. `/data/path/yyyy=2021/mm=08/dd=24`) so that we scan only the relevant data for a given execution date.

Airflow leverages [Jinja](https://jinja.palletsprojects.com), a templating framework in Python, as its templating engine. In this guide, we'll cover how to apply Jinja templates in your code, including:

- Which variables and functions are available when templating
- Which operator fields can be templated and which cannot
- How to validate templates
- How to apply custom variables and functions when templating
- How to render templates to strings and native Python code

## Runtime Variables in Airflow

Templating in Airflow works exactly the same as templating with Jinja in Python: define your to-be-evaluated code between double curly braces, and the expression will be evaluated at runtime. As we saw in the previous code snippet, `execution_date` is a variable available at runtime.

Airflow includes many variables which can be used for templating. Some of the most used variables are:

| Variable name  | Description                                                |
|----------------|------------------------------------------------------------|
| execution_date | Starting datetime of DAG run interval                      |
| ds             | `execution_date` formatted as "2021-08-27"                 |
| ds_nodash      | `execution_date` formatted as "20210827"                   |
| next_ds        | next `execution_date` (= end of current interval) datetime |

For a complete list of all available variables, refer to the [Apache Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html#default-variables).

## Templateable Fields and Scripts

Templates cannot be applied to all arguments of an operator. Two attributes in the BaseOperator define limitations on templating:

- `template_fields`: Defines which fields are templateable
- `template_ext`: Defines which file extensions are templateable

Let's look at a simplified version of the BashOperator:

```python
class BashOperator(BaseOperator):
    template_fields = ('bash_command', 'env')  # defines which fields are templateable
    template_ext = ('.sh', '.bash')  # defines which file extensions are templateable

    def __init__(
        self,
        *,
        bash_command,
        env: None,
        output_encoding: 'utf-8',
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.bash_command = bash_command  # templateable (can also give path to .sh or .bash script)
        self.env = env  # templateable
        self.output_encoding = output_encoding  # not templateable
```

The `template_fields` attribute holds a list of attributes that can be templated. You can also find this list in [the Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/bash/index.html#airflow.operators.bash.BashOperator.template_fields) or in the Airflow UI if you have a task run, under Instance Details --> `template_fields`:

![Rendered Template view](https://assets2.astronomer.io/main/guides/templating/taskinstancedetails.png)

`template_ext` contains a list of file extensions that can be read and templated at runtime. For example, instead of providing a Bash command to `bash_command`, you could provide a `.sh` script:

```python
run_this = BashOperator(
    task_id="run_this",
    bash_command="script.sh",  # .sh extension can be read and templated
)
```

This task reads the contents of `script.sh`, templates it, and executes it:

```bash
# script.sh
echo "Today is {{ execution_date.format('dddd') }}"
```

Templating from files makes it easier to develop (especially when your scripts grow larger) because an IDE can apply language-specific syntax highlighting on the script. This wouldn't be possible if your script was defined as a big string in Airflow code.

By default, Airflow searches for `script.sh` relative to the directory the DAG file is defined in. So if your DAG is stored in `/path/to/dag.py` and your script is stored in `/path/to/scripts/script.sh`, you would set the value of `bash_command` to `scripts/script.sh`.

If desired, additional "search paths" can be controlled at the DAG-level with the `template_searchpath` argument:

```python
with DAG(..., template_searchpath="/tmp") as dag:
    run_this = BashOperator(task_id="run_this", bash_command="script.sh")
```

Now you can store your Bash script in `/tmp` and Airflow will find it.

## Validating Templates

The output of templates can be checked in both the Airflow UI and CLI. One advantage of the CLI is that you don't need to run any tasks before seeing the result.

The Airflow CLI command `airflow tasks render` renders all templateable attributes of a given task. Given a `dag_id`, `task_id`, and dummy `execution_date`, the command outputs something like this:

```bash
$ airflow tasks render example_dag run_this 2021-01-01

# ----------------------------------------------------------
# property: bash_command
# ----------------------------------------------------------
echo "Today is Friday"

# ----------------------------------------------------------
# property: env
# ----------------------------------------------------------
None
```

For this command to work, Airflow must have access to a metastore. You can quickly set up a local SQLite metastore to achieve this:

```bash
cd [your project dir]
export AIRFLOW_HOME=$(pwd)
airflow db init  # generates airflow.db, airflow.cfg, and webserver_config.py in your project dir

# airflow tasks render [dag_id] [task_id] [execution_date]
```

For most templating, this will suffice. However, if any external systems (e.g. a variable in your production Airflow metastore) are reached in the templating logic, you must have connectivity to those systems.

In the Airflow UI, you can view the result of templated attributes after running a task. Click on a task instance --> **Rendered** button to see the result:

![Rendered button in the task instance popup](https://assets2.astronomer.io/main/guides/templating/renderedbutton.png)

Clicking this shows the Rendered Template view and the output of the templated attributes:

![Rendered Template view](https://assets2.astronomer.io/main/guides/templating/renderedtemplate.png)

<!-- markdownlint-disable MD033 -->
<ul class="learn-more-list">
    <p>You might also like:</p>
    <li data-icon="→"><a href="/events/webinars/dynamic-dags?banner=learn-more-banner-click">Dynamic DAGs Webinar</a></li>
    <li data-icon="→"><a href="https://registry.astronomer.io/dags/example-eks-templated?banner=learn-more-banner-click">Astronomer Registry: Eks_templated Example DAG</a></li>
    <li data-icon="→"><a href="/blog/data-pipelines-in-ecommerce?banner=learn-more-banner-click">How Data Pipelines Drive Improved Sales in E-commerce</a></li>
</ul>

## Using Custom Functions and Variables in Templates

As seen above, we have several variables (e.g. `execution_date` and `ds`) available during templating. For various reasons such as security, a Jinja environment is not the same as your Airflow runtime. You can view a Jinja environment as a very stripped-down Python environment. That, among other things, means modules cannot be imported. For example, this doesn't work in a Jinja template:

```python
from datetime import datetime

BashOperator(
    task_id="print_now",
    bash_command="echo It is currently {{ datetime.now() }}",  # raises jinja2.exceptions.UndefinedError: 'datetime' is undefined
)
```

However, it is possible to inject functions into your Jinja environment. In Airflow, several standard Python modules are injected by default for templating, under the name "macros". For example, the faulty code above can be fixed using `macros.datetime`:

```python
BashOperator(
    task_id="print_now",
    bash_command="echo It is currently {{ macros.datetime.now() }}",  # It is currently 2021-08-30 13:51:55.820299
)
```

For the full list of all available macros, refer to the [Apache Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html#id1).

Besides pre-injected functions, you can also use self-defined variables and functions in your templates. Airflow provides a convenient way to inject these into the Jinja environment. Say we wanted to print the number of days since May 1st, 2015 in our DAG and wrote a convenient function for that:

```python
def days_to_now(starting_date):
    return (datetime.now() - starting_date).days
```

To use this inside a Jinja template, you can pass a dict to `user_defined_macros` in the DAG:

```python
def days_to_now(starting_date):
    return (datetime.now() - starting_date).days


with DAG(
    dag_id="demo_template",
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,
    user_defined_macros={
        "starting_date": datetime(2015, 5, 1),  # Macro can be a variable
        "days_to_now": days_to_now,  # Macro can also be a function
    },
) as dag:
    print_days = BashOperator(
        task_id="print_days",
        bash_command="echo Days since {{ starting_date }} is {{ days_to_now(starting_date) }}",  # Call user defined macros
    )
    # Days since 2015-05-01 00:00:00 is 2313
```

It's also possible to inject functions as Jinja [filters](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment.filters) using `user_defined_filters`. You can use filters as pipe-operations. The following example completes the same work as the previous example, only this time using filters:

```python
with DAG(
    dag_id="bash_script_template",
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,
    user_defined_filters={"days_to_now": days_to_now},  # Set user_defined_filters to use function as pipe-operation
    user_defined_macros={"starting_date": datetime(2015, 5, 1)},
) as dag:
    print_days = BashOperator(
        task_id="print_days",
        bash_command="echo Days since {{ starting_date }} is {{ starting_date | days_to_now }}",  # Pipe value to function
    )
    # Days since 2015-05-01 00:00:00 is 2313
```

Functions injected via `user_defined_filters` and `user_defined_macros` are both useable in the Jinja environment. While they achieve the same result, we recommend using filters when you need to import multiple custom functions because the filter formatting improves the readability of your code. You can see this when comparing the two techniques side-to-side:

```python
"{{ name | striptags | title }}"  # chained filters are read naturally from left to right
"{{ title(striptags(name)) }}"  # multiple functions are more difficult to interpret because reading right to left
```

## Rendering Native Python Code

By default, Jinja templates always render to Python strings. This is fine in almost all situations in Airflow, but sometimes it's desirable to render templates to native Python code. If the code you're calling doesn't work with strings, you're in trouble. Let's look at an example:

```python
def sum_numbers(*args):
    total = 0
    for val in args:
        total += val
    return total

sum_numbers(1, 2, 3)  # returns 6
sum_numbers("1", "2", "3")  # TypeError: unsupported operand type(s) for +=: 'int' and 'str'
```

Consider a scenario where you're passing a list of values to this function by triggering a DAG with a config that holds some numbers:

```python
with DAG(dag_id="failing_template", start_date=datetime.datetime(2021, 1, 1), schedule_interval=None) as dag:
    sumnumbers = PythonOperator(
        task_id="sumnumbers",
        python_callable=sum_numbers,
        op_args="{{ dag_run.conf['numbers'] }}",
    )
```

We would trigger the DAG with the following JSON to the DAG run configuration:

```json
{"numbers": [1,2,3]}
```

The rendered value would be a string. Since the `sum_numbers` function unpacks the given string, it ends up trying to add up every character in the string:

```python
('[', '1', ',', ' ', '2', ',', ' ', '3', ']')
```

This is not going to work, so we must tell Jinja to return a native Python list instead of a string. Jinja supports this via _Environments_. The [default Jinja environment](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment) outputs strings, but we can configure a [NativeEnvironment](https://jinja.palletsprojects.com/en/3.0.x/nativetypes/#jinja2.nativetypes.NativeEnvironment) which renders templates as native Python code.

Support for Jinja's NativeEnvironment was added in [Airflow 2.1.0](https://github.com/apache/airflow/pull/14603) via the `render_template_as_native_obj` argument on the DAG class. This argument takes a boolean value which determines whether to render templates with Jinja's default Environment or NativeEnvironment. An example:

```python
def sum_numbers(*args):
    total = 0
    for val in args:
        total += val
    return total


with DAG(
    dag_id="native_templating",
    start_date=datetime.datetime(2021, 1, 1),
    schedule_interval=None,
    render_template_as_native_obj=True,  # Render templates using Jinja NativeEnvironment
) as dag:
    sumnumbers = PythonOperator(
        task_id="sumnumbers",
        python_callable=sum_numbers,
        op_args="{{ dag_run.conf['numbers'] }}",
    )
```

Passing the same JSON configuration `{"numbers": [1,2,3]}` now renders a list of integers which the `sum_numbers` function processes correctly:

```text
[2021-08-26 11:53:12,872] {python.py:151} INFO - Done. Returned value was: 6
```

On a final note, the Jinja environment must be configured on the DAG-level. This means that all tasks in a DAG render either using the default Jinja environment or using the NativeEnvironment.

## Final words

To summarize, you can use templating to give your tasks behaviour by evaluating expressions at runtime. There are several things to know about templating in Airflow:

- Airflow provides several convenience settings around Jinja, the Python templating engine
- Several variables are available at runtime which can be used in templating (see [documentation](https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html#default-variables))
- `template_fields` and `template_ext` define what is templateable on an operator
- Several Python libraries are injected into the Jinja environment (see [documentation](https://airflow.apache.org/docs/apache-airflow/stable/macros-ref.html#id1))
- Custom variables and functions can be injected using `user_defined_filters` and `user_defined_macros`
- By default Jinja templating returns strings but native Python code can be returned by setting `render_template_as_native_obj=True` on the DAG
- For all Jinja templating features, refer to the [Jinja documentation](https://jinja.palletsprojects.com/en/3.0.x/)
