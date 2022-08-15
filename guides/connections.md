---
title: "Managing your Connections in Apache Airflow"
description: "An overview of how connections work in the Airflow UI."
date: 2018-05-21T00:00:00.000Z
slug: "connections"
heroImagePath: null
tags: ["Connections", "Basics", "Hooks", "Operators"]
---

Connections in Airflow are sets of configurations used to connect with other tools in the data ecosystem. They can be created and modified in different ways

In this guide we will cover:

- The basics on Airflow connections.
- How to define connections using the Airflow UI.
- How to define connections via environment variables.
- An example showing a Snowflake connection and a Slack Webhook connection being used in a DAG.
- Programmatically creating and modifying connections.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- What Airflow is and when to use it. See [Introduction to Apache Airflow](https://www.astronomer.io/guides/intro-to-airflow/).
- Airflow operators. See [Operators 101](https://www.astronomer.io/guides/what-is-an-operator).

## Airflow connection essentials

A connection in Airflow is a set of configurations containing the information necessary to send requests to the API of an external tool. Which information a connection needs to contain will vary based on which tool you are connecting to.

Each connection is associated with a unique `conn_id`, which can be provided to operators needing a connection.

Under the hood connections use Airflow [hooks](https://www.astronomer.io/guides/what-is-a-hook/) to send API requests. Many hooks to connect to external tools will have to be added to core Airflow by installing a provider package. The easiest way to find provider packages is by browsing the [Astronomer Registry](https://registry.astronomer.io/).

For example to be able to use a connection of the 'Connection Type' `Amazon S3` Airflow will need to be able to use the `S3Hook` which is part of the [Amazon provider](https://registry.astronomer.io/providers/amazon).

Astro CLI users can simply add the provider to the `packages.txt` file as shown in the example below.

> **Note**: You can use hooks directly within your DAG code as shown in [Hooks 101](https://www.astronomer.io/guides/what-is-a-hook/).

## Define connections in the UI

To define a connection using the Airflow UI click on the **Admin** in the navigation bar and select **Connections**.

![Connections seen from the DAG view](https://assets2.astronomer.io/main/guides/connections/DAGview_connections.png)

The list of connections will be empty in a new Airflow instance. Click the blue `+` button to add a new connection.

![Empty Connection](https://assets2.astronomer.io/main/guides/connections/EmptyConnection.png)

The fields on the lefthand side will change depending on which 'Connection Type' you select.

> **Note**: If the connection type you are looking for is not available in the dropdown menu, make sure you correctly installed the relevant provider.  

For most connections it is not necessary to specify all fields. The example below shows a connection made to an Amazon S3 bucket using the AWS access key ID as `login` an the AWS secret access key as `password` ([See AWS documentation for how to retrieve your AWS access key ID and AWS secret access key](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)).

![Example AWS S3 connection](https://assets2.astronomer.io/main/guides/connections/AWSS3connection.png)

Some connection types offer the possibility to test the connection from the Airflow UI. A message either confirming a successful connection or providing an error message will appear on top of the screen after running a connection test.

> **Note**: Passwords are treated as a secret by Airflow and will be hidden from the user after saving the connection.

## Define connections via environment variables

Connections can also be defined using environment variables. Where you can define environment variables depends on your Airflow setup. Astro CLI users can use the `.env` file for local development or specify environment variables in the Dockerfile.

The connection can be provided in URI format (in this example defined from a Dockerfile).

```Dockerfile
ENV AIRFLOW_CONN_MY_CONN_ID='my-conn-type://login:password@host:port/schema?param1=val1&param2=val2'
```

Starting in Airflow version 2.3.0+ connections can be provided as a JSON (in this example defined from `.env`).

```text
AIRFLOW_CONN_MY_CONN_ID='{
    "conn_type": "my-conn-type",
    "login": "my-login",
    "password": "my-password",
    "host": "my-host",
    "port": 1234,
    "schema": "my-schema",
    "extra": {
        "param1": "val1",
        "param2": "val2"
    }
}'
```

Connections that are defined using environment variables will not show up in the list of connections in the Airflow UI.

> **Note**: There are more ways to add connections to Airflow, for example by modifying airflow.cfg or via the CLI. It is also possible to create custom connection fields. For more in-depth information on configuring connections see ['Managing Connections'](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html) in the Airflow documentation.

> **Note**: Astro CLI users can also define connections for local development by adding them to the `airflow_settings.yaml` file.

## Example: Configuring the SnowflakeToSlackOperator

In this example we will configure the `SnowflakeToSlackOperator`, which necessitates a connection to Snowflake, as well as a connection to Slack. We will define the connections using the Airflow UI.

Before starting Airflow, install both the [Snowflake](https://registry.astronomer.io/providers/snowflake) and the [Slack provider](https://registry.astronomer.io/providers/slack). Astro CLI users can add them to `requirements.txt`:

```text
apache-airflow-providers-snowflake
apache-airflow-providers-slack
```

In the Airflow UI navigate to the list of connections and a connection of the 'Connection Type' `Snowflake`. You will need to provide the following parameters:

- Connection Id: `snowflake_conn` (or another string that has not been used for a different connection already)
- Connection Type: `Snowflake`
- Schema: The schema of your database that you want to query.
- Login: Your Snowflake login name.
- Password: Your Snowflake login password.
- Account: Your Snowflake account in the format xy12345.region
- Database: The database you want to query

You can leave the other fields empty. Test the connection by clicking on the `Test` button.

The screenshot below shows the confirmation that the connection to Snowflake was successful. The example queries a schema in the Snowflake example database.

![Successful Connection to Snowflake](https://assets2.astronomer.io/main/guides/connections/SuccessfulSnowflakeConn.png)

Next the connection to Slack is set up. To post a message to a slack channel you will need to create a Slack app for your server and configure Incoming Webhooks. A step-by-step explanation of this process can be found in the [Slack Documentation](https://api.slack.com/messaging/webhooks).

To connect to Slack from the Airflow UI you only have to provide a few parameters:

- Connection Id: `slack_conn` (or another string that has not been used for a different connection already)
- Connection Type: `Slack Webhook`
- Host: `https://hooks.slack.com.services` (the first part of the Webhook URL)
- Password: The second part of the Webhook URL. It will have the format `T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`

Test the connection by clicking on the `Test` button.

The last step is writing the DAG using the `SnowflakeToSlackOperator`. This operator queries the provided Snowflake database using a SQL statement and can directly post parts of the query to Slack.

In the example the `ORDERS` table from the `TPCH_SF1` schema in the `SNOWFLAKE_SAMPLE_DATA` database is queried for its total count of rows and the sum of the `O_TOTALPRICE` column. The name of the table and of the column are provided using the operator's params argument and [Jinja templating](https://www.astronomer.io/guides/templating/).

The result of the query provided to the `sql` parameter is accessible as a Pandas dataframe called `results_df`. In the `slack_message` we index into the `results_df` by providing the column name. Note that the operator will save the column names in upper case even if they were provided as lower case in the SQL statement.


```Python
from airflow import DAG
from datetime import datetime
from airflow.providers.snowflake.transfers.snowflake_to_slack import (
    SnowflakeToSlackOperator
)

with DAG(
    dag_id="snowflake_to_slack_dag",
    start_date=datetime(2022, 7, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    transfer_task = SnowflakeToSlackOperator(
        task_id="transfer_task",
        snowflake_conn_id="snowflake_conn",
        slack_conn_id="slack_conn",

        # params can be access within the operator using Jinja templating
        params={
            "table_name": "ORDERS",
            "col_to_sum": "O_TOTALPRICE"
        },

        # the SQL statement retrieves row_count of the table
        # and the total sum of one column
        sql="""
            SELECT
              COUNT(*) AS row_count,
              SUM({{ params.col_to_sum }}) AS sum_price
            FROM {{ params.table_name }}
        """,

        # the message to be printed to Slack can use Jinja templating as well
        slack_message="""The table {{ params.table_name }} has
            => {{ results_df.ROW_COUNT[0] }} entries
            => with a total price of {{results_df.SUM_PRICE[0]}}"""
    )
```

Running the DAG results in the message being printed to Slack.

![Slack Message](https://assets2.astronomer.io/main/guides/connections/SlackMessage.png)

## Programmatically creating and modifying connections

Connections can be created and modified programmatically to sync with an external secrets manager.

To access connection information from within your DAG you will need to provide the session information to a Python function by using the `provide_session` function from the `airflow.utils.db` module as a decorator.

The DAG below shows the steps necessary to print out the host parameter of an existing connection.

- Import the `provide_session` function and the `Connection` object.
- Provide the name of the connection to examine. In this example the name is `my_database_connection`.
- Create a function using the `provide_session` function as a decorator.
- In that function query the `session` object for any `Connection` objects and filters for connections with the `conn_id` `my_database_connection` and use the `one_or_none()` method on the query to extract the search results. The last line of the function prints the `host` information from this result.
- Provide the function to a PythonOperator in order to run it within a DAG.

```Python
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.utils.db import provide_session
from airflow.models import Connection

CONN_ID = "my_database_connection"

@provide_session
def print_conn_host(conn_id=None, session=None):
    conn_query = session.query(Connection).filter(
        Connection.conn_id == conn_id,)

    conn_query_result = conn_query.one_or_none()

    print(conn_query_result.host)

with DAG(
    dag_id="print_host_from_connection_id_dag",
    start_date=datetime(2022, 8, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    print_result = PythonOperator(
        task_id="print_result",
        python_callable=print_conn_host,
        op_kwargs={"conn_id": CONN_ID}
    )
```

Knowing that connection information is programmatically accessible it is possible to build functions which are able to modify connection information. A possible use case is to synchronize information with an external secrets manager.

The function below show a possible implementation of such a synchronization.

- `sources` are connections with their information stored in a secrets manager.
- Looping through each `source` the `port` property will be checked to be numeric.
- The current session is queried to check if a connection with the same `conn_id` as the connection from the `source` already exists.
- If no connection of the same id exists a new connection is created.
- If a connection of the same id exists it will be overwritten with the new information from the `source`.

```Python
from airflow.utils.db import provide_session
from airflow.models import Connection
import logging

# get the airflow.task logger
task_logger = logging.getLogger('airflow.task')

@provide_session
def create_connections(session=None):

    # query the API of your secrets manager here
    sources = {"Connection information from the secrets manager"}

    # iterating over sources from the secrets manager
    for source in sources:

        # check that the port property of the sources are numeric
        try:
            int(source['port'])
        except:
            task_logger.info("Port is not numeric for source")
            continue

        # get properties of the source connection, you may need to adjust this
        # for different connection types
        host = source.get("host", "")
        port = source.get("port", "5439")
        db = source.get("db", "")
        user = source.get("user", "")
        password = source.get("pw", "")
​
        # the code below attempts to either modify an existing connection or
        # create a new one
        try:
            # query connection information from the current session
            # to see if a connection with the conn_id source['name'] already
            # exists
            connection_query = session.query(Connection).filter(
                Connection.conn_id == source['name'],)
            connection_query_result = connection_query.one_or_none()

            # if the result of the query is None, this conn_id has not been
            # used before and the new connection can be created from the
            # information pulled from the source in the secrets manager
            if not connection_query_result:                    
                connection = Connection(
                                 conn_id=source['name'],
                                 conn_type='postgres',
                                 host=host,
                                 port=port,
                                 login=user,
                                 password=password,
                                 schema=db
                             )
                # add and commit the new connection to the session
                session.add(connection)
                session.commit()

            # if the conn_id already exists the connection is modified
            # with the information from the source in the secrets manager
            else:
                connection_query_result.host = host
                connection_query_result.login = user
                connection_query_result.schema = db
                connection_query_result.port = port
                connection_query_result.set_password(password)
                session.add(connection_query_result)
                session.commit()

        # in case creating the connection fails, log the error message
        except Exception as e:
            task_logger.info(
                "Failed creating connection"
            task_logger.info(e)
```
