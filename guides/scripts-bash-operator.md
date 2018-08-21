---
title: "Running scripts using the BashOperator"
description: "Learn and troubleshoot how to run shell scripts using the Bash Operator in Airflow"
date: 2018-07-17T00:00:00.000Z
slug: "scripts-bash-operator"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Building DAGs", "BashOperator", "Airflow"]
---

[Apache Airflow's BashOperator](https://airflow.apache.org/code.html#operator-api) is an easy way to execute bash commands in your workflow. This is the method of choice if the DAG you wrote executes a bash command or script.

However, running shell scripts can always run into trouble with permissions, particularly with `chmod`.

This guide will walk you through what to do if you are having trouble executing bash scripts using the BashOperator in Airflow.

## Executing Shell Scripts

Typically, you are able to write a shell script, such as `test.sh`, and then run `chmod +x test.sh` to make the script executable.

In short, you are giving the script permission to execute as a program.

Let's enter the Docker container bash terminal, using `docker exec -it container_name bash`.

If we write a simple script, `test.sh` with only one command, `echo $(whoami)`, we would expect it to output our name, as the user.

However, what we get is:

```
bash: ./test.sh: Permission denied.
```

If we try to `chmod +x test.sh` inside of the container's bash terminal, we get:

```
chmod: test.sh: Read-only file system.
```

## Solution

There are two possible solutions.

1. Chmod before building the container from the docker image.

Before we run `docker exec -it container_name bash`, we can chmod the shell script. Then, once we're in the bash terminal in the docker container, we can run the script no problem.

2. The Run command

If you don't want to run chmod from the command line, you can add the command to the `Dockerfile` in one line.

In the `Dockerfile`, add the line:

```
RUN chmod +x /full/file/path/test.sh
```

The full file path is required, but it needs to be within the Docker container itself. You can type `pwd` inside the Docker container to get the file path to the directory where the `test.sh` script is located. An example of this may be:

```
RUN chmod +x /usr/local/airflow/test.sh
```
