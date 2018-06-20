---
title: "The Astronomer CLI for Apache Airflow"
description: "Using our CLI to manage your instance of Apache Airflow"
date: 2018-05-23T00:00:00.000Z
slug: "cli"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/markus-spiske-207946-unsplash.jpg"
tags: ["Airflow", "CLI", "Product Documentation"]
---


The Astro CLI helps users create and test activities and deploy those activities and Astronomer/community pre-built activities in actual DAGs. Once DAGs have been tested locally, users can deploy them to our public cloud or their private installation.

## Prerequisites

If you want to run Airflow locally through the CLI you will need docker installed.

See [docker download](https://www.docker.com/community-edition#/download) to download docker for your specific operating system.

You should also make sure you Go installed (pip and Python too, but they're packaged with most operating systems).

```
brew install go
```
More info: https://golang.org/doc/install

## Setup

~~~
curl -o- https://cli.astronomer.io/install.sh | bash
~~~

**Note:** The above command only works on Mac & Linux. All other OS users will need to head [here](https://github.com/astronomerio/astro/releases/tag/v0.0.9) and download the binary manually.

## Usage

Create a project directory and navigate to it:

~~~
mkdir /path/to/project
cd /path/to/project
~~~


## Local Airflow

Run `astro airflow up` to start the local airflow cluster.

Once started, it can be accessed at `http://localhost:8080`.

This will start a local version of Astronomer Airflow on your machine along with a local Postgres database.
(Run `docker ps` to see the images)


Once finished you can run `astro airflow down` to stop the cluster.

The next time you run `astro airflow up`, the data from previous runs will still be available (i.e. you won't have to enter credentials again unless you rebuild the Postgres image).

---

## Deploying with the Astro CLI

Initialize a project:

`astro init`

Create a DAG:

~~~
nano /path/to/project/dags/hello_world.py
vi /path/to/project/dags/hello_word.py
~~~

Here's an easy sample DAG:

~~~ python
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


def print_hello():
    return 'Hello world!'


dag = DAG('hello', description='Simple tutorial DAG',
          schedule_interval='0 12 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

dummy_operator = DummyOperator(task_id='dummy_task', retries=3, dag=dag)

hello_operator = PythonOperator(task_id='hello_task', python_callable=print_hello, dag=dag)

dummy_operator >> hello_operator

~~~

Login:
`astro login`


And now we're ready to deploy (make sure your user belongs to an organization):


~~~
astro deploy
~~~

This will prompt you to select the organization, and confirms you are sure you want to deploy.
Once you do that, it will bundle all but a few blacklisted files and push to the API, and then to S3.

**Note**: Information in the `Connections` panel and metadata on local DAG runs will not get pushed up.


If you want to log out of your account:

~~~
astro logout
~~~

## Commands

Usage:

~~~
  astro [command]
~~~

Available Commands:

~~~
  airflow       Run a local Airflow cluster
  config        Get or set Astro configs
  deploy        Deploy to production Airflow cluster
  help          Help about any command
  info          List important CLI information
  init          Create an Astronomer project
  login         Authenticate with Astronomer servers
  logout        Logout of current session
  organization  Organization functions
  status        Airflow cluster status
~~~

Flags:

~~~
  -d, --debug   debug output
  -h, --Help    help for astro
  -v, --verbose verbose output
~~~

Use `astro [command] --help` for more information about a command.

## Developing

How to get started as a developer.

1. Build:

    ```
    $ git clone git@github.com:astronomerio/astro-cli.git
    $ cd astro-cli
    $ make build
    ```

1. (Optional) Install to `$GOBIN`:

    ```
    $ make install
    ```

1. Run:

    ```
    $ astro
    ```
### Old Deploys

In your project directory there will be a hidden `.astro` folder that contains past deploys (made from that machine).

### Metadata
When running/building locally you will need to generate the metadata file.  Running `make build-meta` or a `make build`
will build the meta data file. Once generated, you should be able to build/run without problem.
