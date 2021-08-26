---
title: "Native Jinja templating in Airflow"
description: "How to return native Python types instead of strings when templating in Airflow."
date: 2021-08-25T00:00:00.000Z
slug: "airflow-native-jinja-templating"
tags: ["Templating", "Jinja"]
---

Templating is a powerful concept in Airflow to insert runtime variables in tasks. For example, say you want to print the
day of the week every time you run a task:

```python
BashOperator(
    task_id="print_day_of_week",
    bash_command="echo Today is {{ execution_date.format('dddd') }}",
)
```

Which will print for example "Today is Wednesday".

## Default Jinja templating

Rendering Python expressions at runtime using
[Jinja templating](https://jinja.palletsprojects.com/en/3.0.x/) allows you to construct tasks with different behaviour,
depending on the runtime variables. While this is a powerful concept, it does have a limitation (until recently). By
default, Jinja renders templates to strings. For example, say you add two integers, the result is always a string:

```python
from jinja2 import Template

template = Template("{{ a + b }}")
result = template.render(a=1, b=2)

print(result)  # "3"
print(type(result))  # <class 'str'>
```

## Rendering Jinja templates to native Python code

Rendering Jinja templates to strings is fine in almost all situations in Airflow, but in a few cases it's desirable to
render templates to native Python code. If the code you're calling doesn't work with strings, you're in trouble. Let's
look at an example:

```python
def sum_numbers(*args):
    total = 0
    for val in args:
        total += val
    return total

sum_numbers(1, 2, 3)  # returns 6
sum_numbers("1", "2", "3")  # TypeError: unsupported operand type(s) for +=: 'int' and 'str'
```

Say we would pass a list of values to this function by triggering a DAG with a config that holds some numbers:

```python
with DAG(dag_id="failing_template", start_date=datetime.datetime(2021, 1, 1), schedule_interval=None) as dag:
    sumnumbers = PythonOperator(
        task_id="sumnumbers",
        python_callable=sum_numbers,
        op_args="{{ dag_run.conf['numbers'] }}",
    )
```

And trigger the DAG with the following JSON to the DAG run configuration:

```json
{"numbers": [1,2,3]}
```

The rendered value would be a string and since the `sum_numbers` function unpacks the given string it ends up trying to
add up every character in the string, which is:

```python
('[', '1', ',', ' ', '2', ',', ' ', '3', ']')
```

This is not going to work, so we must tell Jinja to return a native Python list instead of a string. Jinja
supports this via _Environments_. The [default Jinja environment](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment)
outputs strings, but we can configure a so-called [NativeEnvironment](https://jinja.palletsprojects.com/en/3.0.x/nativetypes/#jinja2.nativetypes.NativeEnvironment)
which renders templates as native Python code. In Airflow 2.1.0 support for Jinja's NativeEnvironment was [added](https://github.com/apache/airflow/pull/14603)
via an argument `render_template_as_native_obj` on the DAG class. This argument takes a boolean value which determines
whether to render templates with Jinja's default Environment or NativeEnvironment. An example:

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

Passing the same JSON configuration `{"numbers": [1,2,3]}` now renders a list of integers which the `sum_numbers`
function processes correctly:

```text
[2021-08-26 11:53:12,872] {python.py:151} INFO - Done. Returned value was: 6
```

On a final note, the Jinja environment must be configured on the DAG-level. That means all tasks in the DAG render
either using the default Jinja environment or using the NativeEnvironment.
