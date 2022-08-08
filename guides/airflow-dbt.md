---
title: "Integrating Airflow and dbt"
description: "Running dbt models in your Airflow DAGs."
date: 2021-08-17T00:00:00.000Z
slug: "airflow-dbt"
heroImagePath: "https://assets2.astronomer.io/main/guides/airflow-dbt.png"
tags: ["DAGs", "Integrations"]
---

## Overview

[dbt](https://getdbt.com/) is an open-source library for analytics engineering that helps users build interdependent SQL models for in-warehouse data transformation. As ephemeral compute becomes more readily available in data warehouses thanks to tools like [Snowflake](https://snowflake.com/), dbt has become a key component of the modern data engineering workflow. Now, data engineers can use dbt to write, organize, and run in-warehouse transformations of raw data.

Teams can use Airflow to orchestrate and execute dbt models as DAGs. Running dbt with Airflow ensures a reliable, scalable environment for models, as well as the ability to trigger models only after every prerequisite task is met. Airflow also gives you fine-grained control over dbt tasks such that teams have observability over every step in their dbt models.

In this guide, we'll walk through:

- Using the [dbt Cloud Provider](https://registry.astronomer.io/providers/dbt-cloud) to orchestrate dbt Cloud with Airflow.
- Two common use cases for orchestrating dbt Core with Airflow via the `BashOperator`: 
    - At the [project](https://docs.getdbt.com/docs/building-a-dbt-project/projects) level and, 
    - At the [model](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) level. 
- How to extend the model-level use case by automating changes to a dbt model.

> The dbt Core sections of this guide summarize some of the key practices and findings from our blog series with [Updater](https://updater.com/) and [Sam Bail](https://sambail.com/) about using dbt in Airflow. For more information, check out [Part 1](https://www.astronomer.io/blog/airflow-dbt-1), [Part 2](https://www.astronomer.io/blog/airflow-dbt-2), and [Part 3](https://www.astronomer.io/blog/airflow-dbt-3) of the series.

## dbt Cloud

To orchestrate [dbt Cloud](https://www.getdbt.com/product/what-is-dbt/) jobs with Airflow, you can use the [dbt Cloud Provider](https://registry.astronomer.io/providers/dbt-cloud), which contains the following useful modules:

- **`DbtCloudRunJobOperator`:** Executes a dbt Cloud job.
- **`DbtCloudGetJobRunArtifactOperator`:** Downloads artifacts from a dbt Cloud job run.
- **`DbtCloudJobRunSensor`:** Waits for a dbt Cloud job run to complete.
- **`DbtCloudHook`:** Interacts with dbt Cloud using the V2 API.

In order to use the dbt Cloud Provider in your DAGs, you will need to complete the following steps:

1. Add the `apache-airflow-providers-dbt-cloud` package to your Airflow environment. If you are working in an Astro project, you can add the package to your `requirements.txt` file.
2. Set up an [Airflow connection](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html) to your dbt Cloud instance. The connection type should be `dbt Cloud`, and it should include an API token from your dbt Cloud account. If you want your dbt Cloud Provider tasks to use a default account ID, you can add that to the connection, but it is not required.

In the DAG below, we show a simple implementation of the dbt Cloud Provider. This example showcases how to run a dbt Cloud job from Airflow, while adding an operational check to ensure the dbt Cloud job is not running prior to triggering. The `DbtCloudHook` provides a `list_job_runs()` method which can be used to retrieve all runs for a given job. The operational check uses this method to retrieve the latest triggered run for a job and check its status. If the job is currently not in a state of 10 (Success), 20 (Error), or 30 (Cancelled), the pipeline will not try to trigger another run.

```python
from pendulum import datetime

from airflow.decorators import dag
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.dbt.cloud.hooks.dbt import DbtCloudHook, DbtCloudJobRunStatus
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.utils.edgemodifier import Label

DBT_CLOUD_CONN_ID = "dbt"
JOB_ID = "{{ var.value.dbt_cloud_job_id }}"

def _check_job_not_running(job_id):
    """
    Retrieves the last run for a given dbt Cloud job and checks to see if the job is not currently running.
    """
    hook = DbtCloudHook(DBT_CLOUD_CONN_ID)
    runs = hook.list_job_runs(job_definition_id=job_id, order_by="-id")
    latest_run = runs[0].json()["data"][0]

    return DbtCloudJobRunStatus.is_terminal(latest_run["status"])

@dag(
    start_date=datetime(2022, 2, 10),
    schedule_interval="@daily",
    catchup=False,
    default_view="graph",
    doc_md=__doc__,
)
def check_before_running_dbt_cloud_job():
    begin, end = [DummyOperator(task_id=id) for id in ["begin", "end"]]

    check_job = ShortCircuitOperator(
        task_id="check_job_is_not_running",
        python_callable=_check_job_not_running,
        op_kwargs={"job_id": JOB_ID},
    )

    trigger_job = DbtCloudRunJobOperator(
        task_id="trigger_dbt_cloud_job",
        dbt_cloud_conn_id=DBT_CLOUD_CONN_ID,
        job_id=JOB_ID,
        check_interval=600,
        timeout=3600,
    )

    begin >> check_job >> Label("Job not currently running. Proceeding.") >> trigger_job >> end

dag = check_before_running_dbt_cloud_job()
```

Note that in the `DbtCloudRunJobOperator` you must provide the dbt connection ID as well as the `job_id` of the job you are triggering.

> **Note:** The full code for this example, along with other DAGs that implement the dbt Cloud Provider, can be found on the [Astronomer Registry](https://registry.astronomer.io/dags?providers=dbt+Cloud&page=1).

## dbt Core

When orchestrating dbt Core with Airflow, a straightforward DAG design is to run dbt commands directly through the [`BashOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/bashoperator). In this section we'll show a couple examples for how to do so.

### Use Case 1: dbt Core + Airflow at the Project Level

For this example we'll use the `BashOperator`, which simply executes a shell command, because it lets us run specific dbt commands. The primary dbt interface is the command line, so the `BashOperator` is one of the best tools for managing dbt. You can execute `dbt run` or `dbt test` directly in Airflow as you would with any other shell.

> **Note:** The code for this example can be found on [the Astronomer Registry](https://registry.astronomer.io/dags/dbt-basic).

The DAG below uses the `BashOperator` to run a dbt project and the models' associated tests, each in a single Task:

```python
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import datetime
from airflow.utils.dates import timedelta


with DAG(
    dag_id='dbt_dag',
    start_date=datetime(2021, 12, 23),
    description='An Airflow DAG to invoke simple dbt commands',
    schedule_interval=timedelta(days=1),
) as dag:

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run'
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test'
    )

    dbt_run >> dbt_test
```

Using the `BashOperator` to run `dbt run` and `dbt test` is a working solution for simple use cases or when you would rather have dbt manage dependencies between models. If you need something quick to develop and deploy that has the full power of dbt behind it, then this is the solution for you. However, running dbt at the project-level has several issues:

- Low observability into what execution state the project is in.
- Failures are absolute and require the whole `dbt` group of models to be run again, which can be costly.

### Use Case 2: dbt Core + Airflow at the Model Level

What if we want more visibility into the steps dbt is running in each task? Instead of running a group of dbt models on a single task, we can write a DAG that runs a task for each model. Using this method, our dbt workflow is more controllable because we can see the successes, failures, and retries of each dbt model in its corresponding Airflow task. If a model near the end of our dbt pipeline fails, we can simply fix the broken model and retry that individual task without having to rerun the entire workflow. Plus, we no longer have to worry about defining Sensors to configure interdependency between Airflow DAGs because we've consolidated our work into a single DAG. Our friends at Updater came up with this solution.

To make this work, you need a file that's generated by dbt called `manifest.json`. This file is generated in the target directory of your `dbt` project and contains a full representation of your dbt project. For more information on this file, see the [dbt documentation](https://docs.getdbt.com/reference/dbt-artifacts/).

Our DAG will read the `manifest.json` file, parse it, create the necessary `BashOperator` Airflow tasks, and then set the dependencies to match those of your dbt project. The end result is that each model in your dbt project maps to two tasks in your Airflow DAG: one task to run the model, and another task to run the tests associated with that model. All of these models will run in the appropriate order thanks to the task dependencies we've set. We implement this exact workflow using the following DAG:

```python
import datetime
import json

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import datetime
from airflow.utils.dates import timedelta


dag = DAG(
    dag_id='dbt_dag',
    start_date=datetime(2020, 12, 23),
    description='A dbt wrapper for Airflow',
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

> **Note:** The code for this example can be found on [the Astronomer Registry](https://registry.astronomer.io/dags/dbt-advanced).

Now we have a solution that orchestrates a dbt project in detail, giving data engineers visibility into each dbt model without affecting each model's dependencies. In the next section, we will see how to make this DAG resilient to change.

## Bonus 1: Productionizing with CI/CD

For the team at Updater, splitting the dbt models into tasks was only the first step. The next questions they tackled are:

- How do we automatically update `manifest.json` so that we don't need to manually copy it, paste it into our Airflow project, and redeploy our Airflow environment every time our dbt project changes?
- How do we extend our workflows to accommodate multiple DAGs and schedule intervals?
- How do we contextualize this approach in the case of a broader ELT pipeline?

Running our dbt models on a single DAG has some limitations. Specifically, this implementation cannot handle running different groups of dbt models on different schedules.

To add this functionality, we can take a group of models defined by some selector, such as `dbt run --models tag:hourly`, and deploy that set of models as their own Airflow DAG with its own defined schedule. We can then use our `manifest.json` file to set dependencies between these groups of models and build out a robust CI process. To do this, we can:

1. Use the `selectors.yml` file ([introduced in dbt 0.18](https://docs.getdbt.com/reference/node-selection/yaml-selectors/)) to define a set of model selectors for each Airflow DAG schedule we want to create. We can then use dbt's [tagging feature](https://docs.getdbt.com/reference/resource-configs/tags) to tag every model with a desired schedule interval.

2. Use a CI/CD provider to run a Python script that:
   1. Runs `dbt compile` to create a fresh copy of `manifest.json`
   2. Reads the model selectors defined in the YAML file
   3. Uses the `dbt ls` command to list all of the models associated with each model selector in the YAML file
   4. Turns the dbt DAG from `manifest.json` into a `Graph` object via the `networkx` library
   5. Uses the methods available on the `Graph` object to figure out the correct set of dependencies for each group of models defined in the YAML file
   6. Writes the dependencies for each group of models (stored as a list of tuples) as a pickle file to local storage.

    Here is what that Python script looks like in practice:

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
    # for each DAG (usually corresponding to a different schedule) that we want
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
       """Clean up the naming of the "selected" nodes so they match the structure of what
       is coming out of the generate_all_model_dependencies function. This function doesn't create
       a list of dependencies between selected nodes (that happens in generate_dag_dependencies), rather
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
       """Gets a list of all models in the project and creates dependencies.
       We want to load all the models first because the logic to properly set
       dependencies between subsets of models is basically
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

3. Create an Airflow DAG file for each group of models. Each DAG reads the associated pickle file, creates the required dbt model run/test tasks, and sets dependencies between them as specified in the pickle file. One of those DAGs might look something like this:

  ```python
    with DAG(
       dag_id="dbt_dag",
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

  > **Note:** The functions in the DAG file above have been split out for simplicity, but the logic can be found in the [dbt_advanced.py DAG](https://github.com/astronomer/airflow-dbt-demo/blob/master/dags/dbt_advanced.py).

Putting all of this together, we end up with multiple Airflow DAGs, each running on its own defined schedule, with a specified group of interdependent dbt models running as individual tasks. With this system, running a production dbt model in Airflow is simple: all we need to do is tag a model with the appropriate schedule interval, and it will automatically get picked up and executed by the corresponding Airflow DAG.

Ultimately, this gives us a robust, end-to-end solution that captures the ideal scheduling, execution, and observability experience for running dbt models with Airflow.

With that said, this implementation still has some limitations. For a more in-depth consideration of the benefits and downsides of each implementation, see [Part 2](https://www.astronomer.io/blog/airflow-dbt-2) of our Airflow/dbt blog series.

## Bonus 2: dbt Parser Utility

The sample code we provided in the previous section demonstrates how to loop through the `manifest.json` file of your DAG to parse out individual models and map them to Airflow tasks. To simplify the DAG code when using this pattern, we can use a convenient utility method that takes care of the parsing. The `DbtDagParser` utility, developed and explained by Sam Bail,  works as follows:

- The parser takes the dbt project path containing the `dbt_project.yml` file, as well as the path to the `profiles.yml` file, as inputs. Note that this setup assumes that you have a single repo that contains both your dbt project and Airflow code.
- By providing a "dbt_tag" parameter, you can select a subset of models to run. This means you can specify multiple DAGs for different subsets of the dbt models, for example to run them on different schedules, as described in [Part 2](https://www.astronomer.io/blog/airflow-dbt-2) of our blog series.
- The utility returns a [task group](https://www.astronomer.io/guides/task-groups) containing all `dbt run` tasks for the models in the specified dbt DAG, and optionally another task group for all test tasks.

When used as shown in the sample code below, the utility provides a shortcut to creating Airflow task groups for dbt models. Note that this code snippet only shows part of the DAG file; you can find the whole file in [the demo repo](https://github.com/astronomer/airflow-dbt-demo).

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

Using the jaffleshop demo dbt project, the parser creates the following DAG including two task groups for the `dbt_run` and `dbt_test` tasks:

<!-- markdownlint-disable MD033 -->
<video class="mt-2 mb-2" width="100%" autoplay muted loop><source src="https://videos.ctfassets.net/bsbv786nih7n/31n2GTyVE9DhhNcAqlITQr/2ceb24022a324a11a05e2b5f41a8fc62/taskgroup.mp4" type="video/mp4"></video>

One important fact to note here is that the `DbtDagParser` does not include a `dbt compile` step that updates the `manifest.json` file. Since the Airflow Scheduler parses the DAG file periodically, having a compile step as part of the DAG creation could incur some unnecessary load for the scheduler. We recommend adding a `dbt compile` step either as part of a CI/CD pipeline, or as part of a pipeline run in production before the Airflow DAG is run.

With regards to the `dbt test` runs:

- The test runs are optional. You can simply skip the tests by not using `getdbttest_group()`.
- The `dbt test` task group depends entirely on the `dbt run` group. In this example, the DAG will run all models first, then all tests.

## Conclusion

To recap, in this guide we have learned about dbt Cloud and dbt Core, how to create and productionize dbt tasks in Airflow, and how to automatically create dbt Core tasks based on a manifest. For a more detailed discussion on trade-offs, limitations, and adding dbt Core or dbt Cloud to a full ELT pipeline, see our blog posts. To see more examples of how to use dbt and Airflow to build pipelines, check out our [dbt DAGs on the Registry](https://registry.astronomer.io/dags/?query=dbt&badges=certified).
