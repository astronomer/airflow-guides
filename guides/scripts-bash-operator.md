---
title: "Running scripts using the BashOperator"
description: "Learn and troubleshoot how to run shell scripts using the Bash Operator in Airflow"
date: 2018-07-17T00:00:00.000Z
slug: "scripts-bash-operator"
heroImagePath: null
tags: ["DAGs", "Operators"]
---
<!-- markdownlint-disable-file -->
[Apache Airflow's BashOperator](https://registry.astronomer.io/providers/apache-airflow/modules/bashoperator) is an easy way to execute bash commands in your workflow. If the DAG you wrote executes a bash command or script, this is the operator you will want to use to define the task.

However, running shell scripts can always run into trouble with permissions, particularly with `chmod`.

This guide will walk you through what to do if you are having trouble executing bash scripts using the `BashOperator` in Airflow.

## Executing Shell Scripts

Typically, you are able to write a shell script, such as `test.sh`, and then run `chmod +x test.sh` to make the script executable.

In short, you are giving the script permission to execute as a program.

Let's enter the Docker container bash terminal, using `docker exec -it container_name bash`.

If we write a simple script, `test.sh` with only one command, `echo $(whoami)`, we would expect it to output our name, as the user.

However, what we get is:

```shell
bash: ./test.sh: Permission denied.
```

If we try to `chmod +x test.sh` inside of the container's bash terminal, we get:

```shell
chmod: test.sh: Read-only file system.
```

Looking at a snippet of the `execute` function for the `BashOperator`, we see that operator searches for the script in a temporary directory. That exact line in the source code is [here](https://github.com/apache/airflow/blob/b658a4243fb5b22b81677ac0f30c767dfc3a1b4b/airflow/hooks/subprocess.py#L62). The `cwd` argument of the `Popen` function allows the child process to change its working directory. In Airflow, this parameter is set to `None` by default. To work around this, we need to specify the full file path within the `Dockerfile`, which we'll come back to below.

[Access the full `BashOperator` source code](https://airflow.apache.org/docs/apache-airflow/1.10.3/_modules/airflow/operators/bash_operator.html)

## Solution

There are two possible solutions.

1. Chmod before building the container from the docker image.

[The entire project directory is already copied over here in the Dockerfile.](https://github.com/astronomerio/astronomer/blob/a2b0936a96344ee8762572c27498dc1dd5955176/docker/platform/airflow/onbuild/Dockerfile#L32)

Before we run `docker exec -it container_name bash`, we can chmod the shell script. Then, once we're in the bash terminal in the docker container, we can run the script no problem.

2. The RUN command.

If you don't want to run chmod from the command line, you can add the command to the `Dockerfile` in one line.

In the `Dockerfile`, add the line:

```shell
RUN chmod +x /full/file/path/test.sh
```

The full file path is required, as specified above. You can type `pwd` inside the Docker container to get the file path to the directory where the `test.sh` script is located. An example of this may be:

```shell
RUN chmod +x /usr/local/airflow/test.sh
```

The RUN command will execute every time the container builds, and every time it is deployed, so keeping the container as lean as possible is advantageous.
