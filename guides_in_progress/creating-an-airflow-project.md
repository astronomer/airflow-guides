---
layout: page
title: Setting Up An Airflow Project
permalink: /guides/creating-an-airflow-project/
hide: true
---



# Objective 
We have built a CLI to get you up and running with Airflow as quickly as possible. This guide details how to create, setup and run your Airflow project.

## Requirements
Guide requirements are
- [astro-cli](https://github.com/astronomerio/astro-cli){:target="_blank"} installed
- an [Airflow DAG](https://airflow.incubator.apache.org/concepts.html#dags){:target="_blank"} you wish to run
    - If you don't have a DAG at this time, that's okay, we suggest picking out an [example-dag](https://github.com/airflow-plugins/Example-Airflow-DAGs){:target="_blank"} from our [airflow-plugins](https://github.com/airflow-plugins){:target="_blank"} repository.

## Creating Your Project
Before running your first DAG you will need to initialize your Astronomer EE Airflow project.

### Creating A Project Directory
Create a project directory in your desired root directory. 

Change into the root development directory on your machine. This is often the directory where you have chose to house various development repositories on your computer. If you don't have one yet, we suggest creating a "dev" directory in your home path `~/dev/`.

```bash
cd [EXAMPLE_ROOT_DEV_DIR]
```

Create a project directory. This directory name will become the name of your Astronomer EE Project. The best project names will indicate the department (or if you're lean like us, the organization) and the purpose of the project. Using this example, Astronomer may then name their project `astronomer-airflow`. 

```bash
mkdir [EXAMPLE_PROJECT_NAME]
```

Change into the newly created project directory
```bash
cd [EXAMPLE_PROJECT_NAME]
```

### Project Initialization
Now that you are in your project directory, you will need to initialize the project. This command will scaffold out the needed files and default configuration for your project.

```bash
astro airflow init
```

You will now see the following files and folders

```
- .astro/
- .dockerignore
- Dockerfile
- dags/
- include/
- packages.txt
- plugins/
- requirements.txt
```

## Importing Your Project

You have initialized your Astronomer Airflow project and now you can begin to build your project from scratch or import and existing one.

### DAGs
Directed acyclic graphs (DAG) are the configuration for your workflows and a core component of an Airflow Project. If you are migrating an existing Airflow project you likely have several DAG files you wish to import. You can place all DAG files into the `dags/` directory. They will be imported to your Docker image when you deploy or test locally. This directory gets added to your Docker image in the `$AIRFLOW_HOME` directory.

### Plugins
The [Airflow Plugin](https://airflow.apache.org/plugins.html){:target="_blank"} system can be used to make managing workflow logic easier or even expand the functionality of Airflow itself. If you have any plugin requirements or would like to bring in a plugin from [airflow-plugins](https://github.com/airflow-plugins){:target="_blank"}, they can be put into the `plugins/` project directory. As in the case of the `dags/` directory, this directory will get added to your docker image in the `$AIRFLOW_HOME` directory.

### Requirements
In order to keep our images lightweight, we ship with only the [Python standard lib](https://docs.python.org/3/library/index.html){:target="_blank"}. When you find yourself needing modules not included in the standard lib, you can modify `requirements.txt`. Your requirements file can be used to add additional Python requirements in the same way a standard [Python requirements](https://pip.readthedocs.io/en/1.1/requirements.html){:target="_blank"} file works.

## Running Your Project Locally
We have built tooling to make development and testing of your Airflow projects as simple as possible. From your root project directory you can start your Airflow project.

```bash
astro airflow start
```

This command will inject any dependencies discussed above into the Docker image and then run that Docker image locally. After a successful build you will see hyperlinks to your local Airflow resources.


