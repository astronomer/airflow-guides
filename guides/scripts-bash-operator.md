---
title: "Running scripts using the BashOperator"
description: "Learn and troubleshoot how to run shell scripts using the Bash Operator in Airflow"
date: 2018-07-17T00:00:00.000Z
slug: "scripts-bash-operator"
heroImagePath: null
tags: ["DAGs", "Operators"]
---

The [`BashOperator`](https://registry.astronomer.io/providers/apache-airflow/modules/bashoperator) executes bash commands or a bash script from within your Airflow DAG.

In this guide we will cover:

- When to use the `BashOperator`.
- How to use the `BashOperator`.
- Using the `BashOperator` to execute bash commands.
- Executing a bash script with the `BashOperator`.
- Running a both a JavaScript file and a R script from a DAG using the `BashOperator`.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- Airflow operators. See [Operators 101](https://www.astronomer.io/guides/what-is-an-operator/).
- Basic bash commands. See the [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html).

## How to use the BashOperator

The BashOperator is part of core Airflow and can be used to execute a single bash command, a set of bash commands or a bash script ending in `.sh`.

- `bash_command`: Provide a single bash command, a set of commands or a bash script to be executed. This argument is required.
- `env`: Define environment variables in a dictionary for the bash process created. If left empty the `BashOperator` will inherit the environment variables from your Airflow environment.
- `append_env`: By default providing a dictionary to the `env` parameter will override all existing environment variables. If you instead want to append new environment variables to the environment variables existing in your airflow environment you need to set `append_env` to `True`.
- `output_encoding`: Define the output encoding of the bash command. The default is `'utf-8'`.
- `skip_exit_code`: Declare which bash exit code would leave the task defined by the `BashOperator` in 'skipped' state. The default is 99.
- `cwd`: Change the working directory where the bash command is run. By default this parameter is set to `None` and the bash command runs in a temporary directory.

The task defined by the `BashOperator` will be:

- marked as 'success' if the whole shell exits with an exit code of 0.
- skipped if the exit code is 99 (unless otherwise specified in `skip_exit_code`).
- fail in case of all other exit codes.

> **Note**: If you expect a non-zero exit from a sub-command you can add the prefix `set -e;` to your bash command to make sure that the exit is captured as a task failure.

Both the `bash_command` and the `env` parameters will render [Jinja templates](https://www.astronomer.io/guides/templating/). Please note that the input given through Jinja templates to `bash_command` are neither escaped nor sanitized. If you are concerned about potentially harmful user input you can use the setup shown in the [`BashOperator` documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/bash.html).

## When to use the BashOperator

You can use the `BashOperator` to execute:

- a single or multiple bash commands in your Airflow environment.
- a previously prepared bash script.
- scripts in many programming languages other than Python.

## Example: Execute two bash commands using one BashOperator

The `BashOperator` can execute any number of bash commands separated by `&&`.

In this example two commands are run:

- `echo Hello $MY_NAME!` prints the environment variable `MY_NAME` to the console.
- `echo $A_LARGE_NUMBER | rev  2>&1 | tee $AIRFLOW_HOME/include/my_secret_number.txt` takes the environment variable `A_LARGE_NUMBER`, pipes it to the `rev` command which reverses any input and saves the result in a file called `my_secret_number.txt` located in the `/include` directory. The reversed number will also be printed to the terminal.

Note that the second command uses an environment variable from the Airflow environment `AIRFLOW_HOME`. This is only possible if `append_env` has been set to `True`. Of course it would also be possible to use two separate `BashOperator`s to run the two commands, for example if you want to assign different dependencies to the tasks.

```Python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

with DAG(
    dag_id="bash_two_commands_example_dag",
    start_date=datetime(2022,8,1),
    schedule_interval=None,
    catchup=False
) as dag:

    say_hello_and_create_a_sectet_number = BashOperator(
        task_id="say_hello_and_create_a_sectet_number",
        bash_command="echo Hello $MY_NAME! && echo $A_LARGE_NUMBER | rev  2>&1\
                     | tee $AIRFLOW_HOME/include/my_secret_number.txt",
        env={
            "MY_NAME": "<my name>",
            "A_LARGE_NUMBER": "231942"
            },
        append_env=True
    )
```

## Example: Execute a bash script

The `BashOperator` can also be provided with a bash script (ending in `.sh`) to be executed.

For this example a bash script is created which iterates over all files in the `/include` folder and prints their name to the console.

```bash  
#!/bin/bash

echo "The script is starting!"
echo "The current user is $(whoami)"
files = $AIRFLOW_HOME/include/*

for file in $files
do
    echo "The include folder contains $(basename $file)"
done

echo "The script has run. Have an amazing day!"
```

Save the file above as `my_bash_script.sh` and make it available to your Airflow environment. Astro CLI users can place the file into the `/include` directory.

It is important to make the bash script executable by running:

```bash
chmod +x my_bash_script.sh
```

If you are an Astro CLI user you can either run the above command on the bash script before building the container from the Docker image or add the command to the Dockerfile itself as:

```Dockerfile
RUN chmod +x /usr/local/airflow/include/my_bash_script.sh
```

In the DAG code provide the script to the `bash_command` parameter of the `BashOperator`.

> **Note**: When running a bash script with the `BashOperator` it is crucial to add a space at the end of the command! Otherwise the task will fail with a Jinja exception.

```Python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

with DAG(
    dag_id="bash_script_example_dag",
    start_date=datetime(2022,8,1),
    schedule_interval=None,
    catchup=False
) as dag:

    execute_my_script = BashOperator(
        task_id="execute_my_script",
        # Note the space at the end of the command!
        bash_command="$AIRFLOW_HOME/include/my_bash_script.sh "
        # since the env argument is not specified, this instance of the
        # BashOperator has access to the environment variables of the Airflow
        # instance like AIRFLOW_HOME
    )
```

## Example: Run a JavaScript file and a R script

The `BashOperator` offers the possibility to run a script in any language provided it is possible to run it with a bash command.

In this example we will run a script written in JavaScript to query a public API [providing the current location of the international Space Station](http://open-notify.org/Open-Notify-API/ISS-Location-Now/). The query result will be pushed to XComs and in a second step we can extract the latitude and longitude information in a script written in R and print them to the console.

The following steps are required:

- Install the JavaScript and R language packages at the OS level
- Write a JavaScript file
- Write a R script file
- Make the scripts available to the Airflow environment
- Execute the files from within a DAG using the `BashOperator`

The languages packages can be installed at the OS level by providing them to `packages.txt`:

```text
r-base
nodejs
```

The JavaScript file below contains the code necessary to send a GET request to the `/iss-now` path at `api.open-notify.org` and returns the results at `stdout`, which will both be printed to the console and pushed to XCom by the `BashOperator`.

```JavaScript
// specify that an http API is queried
const http = require('http');

// define the API to query
const options = {
  hostname: 'api.open-notify.org',
  port: 80,
  path: '/iss-now',
  method: 'GET',
};

const req = http.request(options, res => {
  // log the status code of the API response
  console.log(`statusCode: ${res.statusCode}`);

  // write the result of the GET request to stdout
  res.on('data', d => {
    process.stdout.write(d);
  });
});

// in case of an error print the error statement to the console
req.on('error', error => {
  console.error(error);
});

req.end();
```

Save this JavaScript file as `my_java_script.js` and make it available to your Airflow environment. Astro CLI users can place the file into the `/include` directory.

The second task will be using a script written in R that uses a Regex to filter the longitude and latitude information from the API response and print them in a sentence.

```R
# print outputs to the console
options(echo = TRUE)

# read an argument provided to the R script from the command line
myargs <- commandArgs(trailingOnly = TRUE)

# split a string using : as a separator
set <- strsplit(myargs, ":")

# use Regex to extract the lat/long information and convert them to numeric
longitude <- as.numeric(gsub(".*?([0-9]+.[0-9]+).*", "\\1", set[3]))
latitude <- as.numeric(gsub(".*?([0-9]+.[0-9]+).*", "\\1", set[5]))

# print lat/long information in a sentence.
sprintf("The current ISS location: lat: %s / long: %s.", latitude, longitude)
```

Save this R file as `my_R_script.R` and make it available to your Airflow environment. Astro CLI users can place the file into the `/include` directory.

The DAG uses the `BashOperator` to execute both files defined above sequentially.

```Python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="print_ISS_info_dag",
    start_date=datetime(2022,8,1),
    schedule_interval=None,
    catchup=False
) as dag:

    # Use the node command to execute the JavaScript file from the command line
    get_ISS_coordinates = BashOperator(
        task_id="get_ISS_coordinates",
        bash_command="node $AIRFLOW_HOME/include/my_java_script.js"
    )

    # Use the Rscript command to execute the R file which is being provided
    # with the result from task one via an environment variable via XComs
    print_ISS_coordinates = BashOperator(
        task_id="print_ISS_coordinates",
        bash_command="Rscript $AIRFLOW_HOME/include/my_R_script.R $ISS_COORDINATES",
        env={
            "ISS_COORDINATES": "{{ task_instance.xcom_pull(\
                               task_ids='get_ISS_coordinates', \
                               key='return_value') }}"
            },
        # set append_env to True to be able to use env variables
        # like AIRFLOW_HOME from the Airflow environment
        append_env=True
    )

    get_ISS_coordinates >> print_ISS_coordinates
```

The logs from the second task will show the statement with the current ISS location:

```text
[2022-08-10, 18:54:30 UTC] {subprocess.py:92} INFO - [1] "The current ISS location: lat: 23.0801 / long: 163.5282."
```

## Conclusion

The `BashOperator` is a powerful tool to run bash commands and scripts from within Airflow DAGs. It also offers the possibility to leverage advantages of other programming languages by executing all scripts that can be run from the command line.
