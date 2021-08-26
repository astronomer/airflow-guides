---
title: "Integrating Airflow and dbt"
description: "Running dbt models in your Airflow DAGs."
date: 2021-08-17T00:00:00.000Z
slug: "airflow-dbt"
heroImagePath: "https://assets2.astronomer.io/main/guides/airflow-dbt.png"
tags: ["DAGs", "Integrations"]
---

## Overview

This guide is a summary of our blog posts with Updater where you’ll learn how to use dbt in Airflow. Check parts [1](https://www.astronomer.io/blog/airflow-dbt-1), [2](https://www.astronomer.io/blog/airflow-dbt-2), and [3](https://www.astronomer.io/blog/airflow-dbt-3) of those posts for more details and discussions.

A tool that often comes up in conversation is [dbt](https://getdbt.com/), an open-source library for analytics engineering that helps users build interdependent SQL models for in-warehouse data transformation. The portion of the modern data engineering workflow that dbt addresses is significant; as ephemeral compute becomes more readily available in the data warehouse itself thanks to tools like [Snowflake](https://snowflake.com/), data engineers have embraced an ETL—>ELT paradigm shift that encourages loading raw data directly into the warehouse and doing transformations on top of the aforementioned ephemeral compute. dbt helps users write, organize, and run these in-warehouse transformations.

Given the complementary strengths of both tools, it's common to see teams use Airflow to orchestrate and execute dbt models within the context of a broader ELT pipeline that runs on Airflow and exists as a DAG. Running dbt with Airflow ensures a reliable, scalable environment for models and the ability to trigger those models only after every prerequisite task is met. Airflow also allows for fine-grained control over dbt tasks, so teams can have observability over every step in their dbt models.

The following two use cases show how to use the dbt with Airflow via the `BashOperator`, first at the project level then at the model level. Two bonus sections show how to extend the second use case to automate changes to the dbt model.

## Setup

See the [demo repo](https://github.com/astronomer/airflow-dbt-demo) for complete set-up instructions. It includes a sample dbt project used in this guide and complete versions of each DAG.

## Use Case 1: dbt + Airflow at the Project Level

The Task is the smallest unit in Airflow that does work, and Tasks together form a DAG. Tasks typically come as Operators or Sensors. The former execute some bit of code or set command, while the latter wait for an operation to succeed or fail. Using dbt, we have a few options to choose from when it comes to Airflow DAG writing: a [community-contributed Airflow plugin](https://github.com/dwallace0723/dbt-cloud-plugin/) to farm out execution to dbt Cloud, pre-existing dbt Airflow operators in the [community-contributed airflow-dbt python package](https://pypi.org/project/airflow-dbt/), or running dbt commands directly through the [`BashOperator`](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/bash.html). This guide chooses to use the `BashOperator`, as it demystifies what the dbt operator does under the hood and allows very specific dbt commands to be run.

In Airflow, a task that invokes the `BashOperator` simply executes a shell command. Because the primary dbt interface is the command line, the `BashOperator` proves to be a useful tool to interact with the library; the familiar `dbt run` or `dbt test` commands can be executed directly in Airflow the same way they would be executed in any other shell.

This use case assumes you have followed the steps in the demo repo to set up an environment with a dbt project.

```python
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import datetime
from airflow.utils.dates import timedelta


dag = DAG(
    'dbt_dag',
    start_date=datetime(2021, 12, 23),
    description='An Airflow DAG to invoke simple dbt commands',
    schedule_interval=timedelta(days=1),
)

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='dbt run',
    dag=dag
)

dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='dbt test',
    dag=dag
)

dbt_run >> dbt_test
```

If we were to just use the `BashOperator` to run `dbt run` and `dbt test` as above, then we do have a working solution, but one without much visibility into what is going on. Failures are absolute, and the whole `dbt` group of models must be run again, which is potentially costly. The whole DAG is only two Tasks, though, which is great when you want to keep things simple.

![Beginner dbt DAG](https://www.astronomer.io/static/157f41a5426d04fd477a1a8b8c4c61ad/4ef49/dbt-basic-dag.png)

## Use Case 2: dbt + Airflow at the Model Level

What if we want more visibility into the steps dbt is running in each task? Instead of having a single Airflow DAG that contains a single task to run a group of dbt models, we can have an Airflow DAG run a single task for each model. This means that our entire dbt workflow is available at a much more granular level in the Airflow UI and, most importantly, we have fine-grained control of the success, failure, and retry of each dbt model as a corresponding Airflow task. If a model near the end of our dbt pipeline fails, we can simply fix the broken model and retry that individual task without having to rerun the entire workflow. Plus, we no longer have to worry about defining Sensors to configure interdependency between Airflow DAGs since we've consolidated our work into a single DAG.

In order to make this work, you need a file that's generated by dbt called `manifest.json`. This file is generated in the target directory of your `dbt` project ([see docs here](https://docs.getdbt.com/reference/dbt-artifacts/)) and contains a full representation of your dbt project, which gives you all the information you need to create your dbt Airflow DAG.

In short, this DAG file will read your `manifest.json` file, parse it, create the necessary `BashOperator` Airflow tasks, and then set the dependencies to match those of your dbt project. The end result is that each model in your dbt project maps to two tasks in your Airflow DAG — one task to run the model and another task to run the tests associated with that model. To top it all off, all of these models will run in the appropriate order thanks to the task dependencies we've set. The file below shows how we can do this.

```python
import datetime
import json

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import datetime
from airflow.utils.dates import timedelta


dag = DAG(
    'dbt_dag',
    start_date=datetime(2020, 12, 23),
    description='A dbt wrapper for airflow',
    schedule_interval=timedelta(days=1),
)

def load_manifest():
    local_filepath = "/usr/local/airflow/dags/dbt/target/manifest.json"
    with open(local_filepath) as f:
        data = json.load(f)

    return data

def make_dbt_task(node, dbt_verb):
    """Returns an Airflow operator either run and test an individual model"""
    DBT_DIR = "/usr/local/airflow/dags/dbt"
    GLOBAL_CLI_FLAGS = "--no-write-json"
    model = node.split(".")[-1]

    if dbt_verb == "run":
        dbt_task = BashOperator(
            task_id=node,
            bash_command=f"""
            cd {DBT_DIR} &&
            dbt {GLOBAL_CLI_FLAGS} {dbt_verb} --target prod --models {model}
            """,
            dag=dag,
        )

    elif dbt_verb == "test":
        node_test = node.replace("model", "test")
        dbt_task = BashOperator(
            task_id=node_test,
            bash_command=f"""
            cd {DBT_DIR} &&
            dbt {GLOBAL_CLI_FLAGS} {dbt_verb} --target prod --models {model}
            """,
            dag=dag,
        )

    return dbt_task

data = load_manifest()

dbt_tasks = {}
for node in data["nodes"].keys():
    if node.split(".")[0] == "model":
        node_test = node.replace("model", "test")

        dbt_tasks[node] = make_dbt_task(node, "run")
        dbt_tasks[node_test] = make_dbt_task(node, "test")

for node in data["nodes"].keys():
    if node.split(".")[0] == "model":

        # Set dependency to run tests on a model after model runs finishes
        node_test = node.replace("model", "test")
        dbt_tasks[node] >> dbt_tasks[node_test]

        # Set all model -> model dependencies
        for upstream_node in data["nodes"][node]["depends_on"]["nodes"]:

            upstream_node_type = upstream_node.split(".")[0]
            if upstream_node_type == "model":
                dbt_tasks[upstream_node] >> dbt_tasks[node]
```

Now we have a solution that allows Airflow to orchestrate a dbt project in detail, giving data engineers visibility into each dbt model without affecting the dependencies each model has. In the next section, we will see how to make this DAG resilient to change.

## Bonus 1: Productionizing With CI/CD

Now that we know how to split dbt out into tasks and orchestrate dbt models at a fine-grained level, our next three questions to tackle are:

1. How do I automatically update my `manifest.json` file so that I don't need to manually copy it, paste it into my Airflow project, and redeploy my Airflow environment every time a model changes or is added?
2. How do I extend my workflow beyond a monodag approach and accommodate multiple schedule intervals?
3. How do I contextualize this approach in the case of a broader ELT pipeline?

Because all of our dbt models are still running on the schedule of a single Airflow DAG, there exist some inherent limitations in the extensibility of our approach. For instance, the solution so far cannot handle running different groups of dbt models on different schedules. To add this functionality, we can take a group of models defined by some selector, e.g. `dbt run --models tag:hourly`, and deploy that set of models as their own Airflow DAG with its own defined schedule. Leveraging the `manifest.json` file to correctly set these dependencies between an arbitrary set of models allows us to build out a robust CI process:

1. Leverage the `selectors.yml` file ([introduced in dbt 0.18](https://docs.getdbt.com/reference/node-selection/yaml-selectors/)) in order to define a set of model selectors for each Airflow DAG schedule we want to create. Then use dbt's tagging feature to tag every model with a desired schedule interval.
2. Use a CI/CD provider to run a Python script that:
  1. Runs `dbt compile` to create a fresh copy of `manifest.json`
  2. Reads the model selectors defined in the YAML file
  3. Uses the `dbt ls` command to list all of the models associated with each model selector in the YAML file
  4. Turns the dbt DAG from `manifest.json` into a `Graph` object via the `networkx` library
  5. Uses the methods available on the `Graph` object to figure out the correct set of dependencies for each group of models defined in the YAML file
  6. Writes the dependencies for each group of models (stored as a list of tuples) as a pickle file to local storage

Here is what that script looks like in practice:

```python
import yaml
import os
import json
import networkx as nx
import pickle

# README
# This file is a utility script that is run via CircleCI in the deploy
# step. It is not run via Airflow in any way. The point of this script is
# to generate a pickle file that contains all of the dependencies between dbt models
# for each dag (usually corresponding to a different schedule) that we want
# to run.

def load_manifest():
   """Load manifest.json """
   local_filepath = f"{DBT_DIR}/target/manifest.json"
   with open(local_filepath) as f:
       data = json.load(f)
   return data

def load_model_selectors():
   """Load the dbt selectors from YAML file to be used with dbt ls command"""
   with open(f"{DBT_DIR}/selectors.yml") as f:
       dag_model_selectors = yaml.full_load(f)
   selected_models = {}
   for selector in dag_model_selectors["selectors"]:
       selector_name = selector["name"]
       selector_def = selector["definition"]
       selected_models[selector_name] = selector_def
   return selected_models

def parse_model_selector(selector_def):
   """Run the dbt ls command which returns all dbt models associated with a particular
   selection syntax"""
   models = os.popen(f"cd {DBT_DIR} && dbt ls --models {selector_def}").read()
   models = models.splitlines()
   return models

def generate_all_model_dependencies(all_models, manifest_data):
   """Generate dependencies for entire project by creating a list of tuples that
   represent the edges of the DAG"""
   dependency_list = []
   for node in all_models:
       # Cleaning things up to match node format in manifest.json
       split_node = node.split(".")
       length_split_node = len(split_node)
       node = split_node[0] + "." + split_node[length_split_node - 1]
       node = "model." + node
       node_test = node.replace("model", "test")
       # Set dependency to run tests on a model after model runs finishes
       dependency_list.append((node, node_test))
       # Set all model -> model dependencies
       for upstream_node in manifest_data["nodes"][node]["depends_on"]["nodes"]:
           upstream_node_type = upstream_node.split(".")[0]
           upstream_node_name = upstream_node.split(".")[2]
           if upstream_node_type == "model":
               dependency_list.append((upstream_node, node))
   return dependency_list

def clean_selected_task_nodes(selected_models):
   """Clean up the naming of the "selected" nodes so they match the structure what
   is coming out generate_all_model_dependencies function. This function doesn't create
   a list of dependencies between selected nodes (that happens in generate_dag_dependencies)
   it's just cleaning up the naming of the nodes and outputting them as a list"""
   selected_nodes = []
   for node in selected_models:
       # Cleaning things up to match node format in manifest.json
       split_node = node.split(".")
       length_split_node = len(split_node)
       node = split_node[0] + "." + split_node[length_split_node - 1]
       # Adding run model nodes
       node = "model." + node
       selected_nodes.append(node)
       # Set test model nodes
       node_test = node.replace("model", "test")
       selected_nodes.append(node_test)
   return selected_nodes

def generate_dag_dependencies(selected_nodes, all_model_dependencies):
   """Return dependencies as list of tuples for a given DAG (set of models)"""
   G = nx.DiGraph()
   G.add_edges_from(all_model_dependencies)
   G_subset = G.copy()
   for node in G:
       if node not in selected_nodes:
           G_subset.remove_node(node)
   selected_dependencies = list(G_subset.edges())
   return selected_dependencies

def run():
   """Get list of all models in project and create dependencies.
   We want to load all the models first because the logic to properly set
   dependencies between subsets of models is basically the process of
   removing nodes from the complete DAG. This logic can be found in the
   generate_dag_dependencies function. The networkx graph object is smart
   enough that if you remove nodes with remove_node method that the dependencies
   of the remaining nodes are what you would expect.
   """
   manifest_data = load_manifest()
   all_models = parse_model_selector("updater_data_model")
   all_model_dependencies = generate_all_model_dependencies(all_models, manifest_data)
   # Load model selectors
   dag_model_selectors = load_model_selectors()
   for dag_name, selector in dag_model_selectors.items():
       selected_models = parse_model_selector(selector)
       selected_nodes = clean_selected_task_nodes(selected_models)
       dag_dependencies = generate_dag_dependencies(selected_nodes, all_model_dependencies)
       with open(f"{DBT_DIR}/dbt_dags/data/{dag_name}.pickle", "wb") as f:
           pickle.dump(dag_dependencies, f)

# RUN IT
DBT_DIR = "./dags/dbt"
run()
```

3. Finally, we create an Airflow DAG file for each group of models that reads the associated pickle file, creates the required dbt model run/test tasks, and then sets dependencies between them as specified in the pickle file.

```python

with DAG(
   f"dbt_dag",
   schedule_interval="@daily",
   max_active_runs=1,
   catchup=False,
   start_date=datetime(2021, 1, 1)
) as dag:
    # Load dependencies from configuration file
    dag_def = load_dag_def_pickle(f"{DAG_NAME}.pickle")

    # Returns a dictionary of bash operators corresponding to dbt models/tests
    dbt_tasks = create_task_dict(dag_def)

    # Set dependencies between tasks according to config file
    for edge in dag_def:
       dbt_tasks[edge[0]] >> dbt_tasks[edge[1]]
```

Note that the functions in the DAG file above have been split out for simplicity, but the logic can be found in the [dbt_advanced.py DAG](https://github.com/astronomer/airflow-dbt-demo/blob/master/dags/dbt_advanced.py).

Putting all of this together, we end up with multiple Airflow DAGs, each running on its own defined schedule, with a specified group of interdependent dbt models running as individual tasks within each DAG. With this system, running a production dbt model in Airflow is dead-simple: all we need to do is tag a model with the appropriate schedule interval and it will automatically get picked up and executed by the corresponding Airflow DAG.
Ultimately, this gives us a fully robust, end-to-end solution that captures the ideal scheduling, execution, and observability experience for our dbt models with Apache Airflow.
For a discussion of limitations, please refer to the [second blog post](https://www.astronomer.io/blog/airflow-dbt-2).

## Bonus 3: dbt Parser Utility

The sample code we provided in the previous section demonstrates how to loop through the `manifest.json` file of your dbt DAG to parse out the individual models and dependencies and map them to Airflow tasks. In order to simplify the DAG code when using this pattern, we can use a small convenience utility method that takes care of the parsing. The `DbtDagParser` utility works as follows:

- The parser takes the dbt project path containing the `dbt_project.yml` file, as well as the path to the `profiles.yml` file as inputs. Note that this setup assumes a "mono repo" with the dbt project being collocated with the Airflow code.
- By providing a "dbt_tag" parameter, a user can select a subset of models to run. This allows specifying multiple DAGs for different subsets of the dbt models, for example to run them on different schedules, as described in [this blog post](https://www.astronomer.io/blog/airflow-dbt-2).
- The utility returns a task group containing all `dbt run` tasks for the models in the specified dbt DAG, and optionally another task group for all test tasks.

When used as shown in the sample code below, the utility provides a convenient shortcut to creating Airflow task groups with the respective dbt models that can be triggered in a DAG run. Note that this code snippet only shows part of the DAG file; you can find the whole file in [the demo repo](https://github.com/astronomer/airflow-dbt-demo).

```python
with dag:

    start_dummy = DummyOperator(task_id='start')
    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command=f'dbt {DBT_GLOBAL_CLI_FLAGS} seed --profiles-dir {DBT_PROJECT_DIR} --project-dir {DBT_PROJECT_DIR}'
    )
    end_dummy = DummyOperator(task_id='end')

    dag_parser = DbtDagParser(dag=dag,
                              dbt_global_cli_flags=DBT_GLOBAL_CLI_FLAGS,
                              dbt_project_dir=DBT_PROJECT_DIR,
                              dbt_profiles_dir=DBT_PROJECT_DIR,
                              dbt_target=DBT_TARGET
                              )
    dbt_run_group = dag_parser.get_dbt_run_group()
    dbt_test_group = dag_parser.get_dbt_test_group()

    start_dummy >> dbt_seed >> dbt_run_group >> dbt_test_group >> end_dummy
```

Using the jaffleshop demo dbt project, the parser creates the following DAG including two [task groups](https://www.astronomer.io/guides/task-groups) for the `dbt_run` and `dbt_test` tasks:

![DAG including two task groups from "dbt_run" and "dbt_test"](https://www.astronomer.io/static/202d5a37d1059b83deb4d6a6a1b55b8a/1df5b/image1.png)

One important fact to note here is that the `DbtDagParser` does not include a `dbt compile` step that updates the `manifest.json` file. Since the Airflow scheduler parses the DAG file periodically, having a compile step as part of the DAG creation could potentially incur some unnecessary load for the scheduler. We recommend adding a `dbt compile` step either as part of a CI/CD pipeline, or as part of a pipeline run in production before the Airflow DAG is run.

There are two small differences between the previous examples in dbt_advanced.py and elt.py in the demo repo and this example with regards to the “dbt test” runs:
1. The test runs are optional. You can simply skip the tests by not using `getdbttest_group()`.
2. The `dbt test` task group depends entirely on the `dbt run` group instead of each test running right after the corresponding model. This means that in this example, the DAG will run all models first, then all tests.

Which pattern you choose for your tests most likely depends on the kind of alerting or DAG run termination you add to your test tasks; we’re just suggesting one possible option here.

## Conclusion
To recap, in this guide we have learned about dbt, how to create dbt tasks in Airflow, and how to productionize those tasks to automatically create tasks based on a manifest. For a more detailed discussion on trade-offs, limitations, and adding dbt to a full ELT pipeline, see our blog posts. To see more examples of how to use dbt and Airflow to build pipelines, check out our [dbt DAGs on the Registry](https://registry.astronomer.io/dags/?query=dbt&badges=certified).
