---
title: "Managing your Connections in Apache Airflow"
description: "An overview of how connections work in the Airflow UI."
date: 2018-05-21T00:00:00.000Z
slug: "connections"
heroImagePath: null
tags: ["Connections", "Basics", "Hooks", "Operators"]
---

Connections in Airflow are sets of configurations used to connect with other tools in the data ecosystem. They are required by most hooks and operators, and can be created and modified in different ways.

In this guide we will cover:

- The basics of Airflow connections.
- How to define connections using the Airflow UI.
- How to define connections using environment variables.
- An example showing a Snowflake connection and a Slack Webhook connection being used in a DAG.

## Assumed knowledge

To get the most out of this guide, you should have knowledge of:

- What Airflow is and when to use it. See [Introduction to Apache Airflow](https://www.astronomer.io/guides/intro-to-airflow/).
- Airflow operators. See [Operators 101](https://www.astronomer.io/guides/what-is-an-operator).
- Airflow hooks. See [Hooks 101](https://www.astronomer.io/guides/what-is-a-hook/).

## Airflow connection essentials

A connection in Airflow is a set of configurations containing the information necessary to send requests to the API of an external tool. The information a connection needs to contain will vary based on which tool you are connecting to. In most cases a connection necessitates login credentials or a private key in order to authenticate Airflow to the external tool.

Airflow connections can be defined in multiple ways, using:

- **The Airflow UI**: The most straightforward way to add connections directly from the UI.
- **Environment variables**: Add connections that are completely hidden from the UI.
- **The [Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#tag/Connection)**: Add a connection using an API call.
- **A secrets backend**: Integrate Airflow with a secrets backend solution that can store credentials and sensitive values to be used by Airflow.
- The `airflow.cfg` file: Add connections by modifying a configuration file.
- The Airflow CLI: Add connections by running a CLI command.

In this guide we will cover adding connections using the Airflow UI and environment variables. For more in-depth information on configuring connections in other ways see the REST API documentation, as well as ['Managing Connections'](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html) and ['Secrets Backend'](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/secrets-backend/index.html) in the Airflow documentation.

To discover which information to provide to which field you can search for the relevant provider in the [Astronomer Registry](https://registry.astronomer.io/) and click on the `Docs` button to find documentation on a specific provider. Most common providers will have documentation on each of their associated `Connection types`. For example, you can find information on how to set up different connections to Azure on the [Connection Types page of the Azure provider](https://airflow.apache.org/docs/apache-airflow-providers-microsoft-azure/stable/connections/index.html).

> **Note**: If you cannot find the relevant information in the Apache Airflow documentation on the external tool you are trying to connect to, see if the documentation of the external tool offers guidance on how to authenticate to it or refer to the source code of the hook that is being used by your operator.

Under the hood, Airflow [hooks](https://www.astronomer.io/guides/what-is-a-hook/) use connections to authenticate to external systems in order to send API requests. Most hooks that require connections are part of provider packages.

For example, the `S3Hook`, which is part of the [Amazon provider](https://registry.astronomer.io/providers/amazon), requires a connection of the type `Amazon S3`.

Each connection is associated with a unique `conn_id`, which can be provided to operators and hooks requiring a connection.

## Define connections in the UI

The most common way of defining a connection is using the Airflow UI. Click on the **Admin** in the navigation bar and select **Connections**.

![Connections seen from the DAG view](https://assets2.astronomer.io/main/guides/connections/DAGview_connections.png)

The list of connections will be empty in a new Airflow instance. Click the blue `+` button to add a new connection.

![Empty Connection](https://assets2.astronomer.io/main/guides/connections/EmptyConnection.png)

The fields on the lefthand side may change depending on which 'Connection Type' you select.

> **Note**: Specific connection types will only be available in the dropdown menu if the relevant provider is installed in your Airflow environment.  

For most connections it is not necessary to specify all fields. The example below shows a connection made to an Amazon S3 bucket using the AWS access key ID as `login` and the AWS secret access key as `password` ([See AWS documentation for how to retrieve your AWS access key ID and AWS secret access key](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)).

![Example AWS S3 connection](https://assets2.astronomer.io/main/guides/connections/AWSS3connection.png)

It is possible to pass additional configuration parameters to a connection by providing them to the `Extra` field as a JSON. For example it would be possible to add the [ARN of a role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) to assume when logging into AWS by entering `{"role_arn":"arn:aws:iam::123456789012:role/my_role_name"}` in the `Extra` field. To learn about additional parameters for a specific connection type please refer to the documentation of the relevant provider package.

In Airflow version 2.2+ some connection types offer the possibility to test the connection from the Airflow UI. A message either confirming a successful connection or providing an error message will appear on top of the screen after running a connection test.

### Masking sensitive information

Connections often contain sensitive credentials. By default Airflow will hide the connection password, both in the UI and in the Airflow logs. Values from the Connection's `Extra` field will also be hidden if their key contains any of the words listed in the environment variable `AIRFLOW__CORE__SENSITIVE_VAR_CONN_NAMES`, as long as `AIRFLOW__CORE__HIDE_SENSITIVE_VAR_CONN_FIELDS` is set to `True`. You can find more information on masking including a list of the default values of this environment variable in the Airflow documentation on [Masking sensitive data](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/mask-sensitive-values.html).

## Define connections via environment variables

Connections can also be defined using environment variables. Astro CLI users can use the `.env` file for local development, or specify environment variables in the Dockerfile.

> **Note**: If you are synchronizing your project using a public remote repository, make sure not to save sensitive information in the Dockerfile. In this case using either a secrets backend, Airflow connections defined in the UI or `.env` locally is preferred as to not expose secrets in plain text.

The environment variable used for the connection needs to be in the form of `AIRFLOW_CONN_YOURCONNID` and can be provided either in URI or, starting with Airflow 2.3, in JSON format.

URI (Uniform Resource Identifier) is a format designed to contain all necessary connection information in one string, starting with the connection type followed by login, password and host. In many cases a specific port and schema, as well as additional parameters will be added.

```Dockerfile

# the general format of a URI connection
ENV AIRFLOW_CONN_MYCONNID='my-conn-type://login:password@host:port/schema?param1=val1&param2=val2'

# an example of a connection to snowflake defined as a URI
ENV AIRFLOW_CONN_snowflake_conn='snowflake://LOGIN:PASSWORD@/?account=xy12345&region=eu-central-1'

```

In Airflow 2.3+, connections can alternatively be provided as a JSON (in this example defined from `.env`).

```text
AIRFLOW_CONN_MYCONNID='{
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

Note that connections that are defined using environment variables will not show up in the list of connections in the Airflow UI and which parameters to specify can very for different connection types.

## Example: Configuring the SnowflakeToSlackOperator

In this example, we will configure the `SnowflakeToSlackOperator`, which requires connections to Snowflake and Slack. We will define the connections using the Airflow UI.

Before starting Airflow, we need to install both the [Snowflake](https://registry.astronomer.io/providers/snowflake) and the [Slack provider](https://registry.astronomer.io/providers/slack). Astro CLI users can add them to `requirements.txt`:

```text
apache-airflow-providers-snowflake
apache-airflow-providers-slack
```

In the Airflow UI, we can navigate to the list of connections and add a connection of the 'Connection Type' `Snowflake`. The following parameters are required:

- Connection Id: `snowflake_conn` (or another string that has not been used for a different connection already)
- Connection Type: `Snowflake`
- Account: Your Snowflake account in the format xy12345.region
- Login: Your Snowflake login name.
- Password: Your Snowflake login password.

You can leave the other fields empty. Test the connection by clicking on the `Test` button.

The screenshot below shows the confirmation that the connection to Snowflake was successful.

![Successful Connection to Snowflake](https://assets2.astronomer.io/main/guides/connections/SuccessfulSnowflakeConn.png)

Next we set up a connection to Slack. To post a message to a Slack channel, you will need to create a Slack app for your server and configure incoming webhooks. A step-by-step explanation of this process can be found in the [Slack Documentation](https://api.slack.com/messaging/webhooks).

To connect to Slack from Airflow, you only have to provide a few parameters:

- Connection Id: `slack_conn` (or another string that has not been used for a different connection already)
- Connection Type: `Slack Webhook`
- Host: `https://hooks.slack.com.services` (the first part of the Webhook URL)
- Password: The second part of the Webhook URL. It will have the format `T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`

Test the connection by clicking on the `Test` button.

The last step is writing the DAG using the `SnowflakeToSlackOperator` to run a SQL query on a Snowflake table and post the result as a message to a Slack channel. The `SnowflakeToSlackOperator` needs both, the connection id pointing towards the snowflake connection `snowflake_conn_id` and the connection id for the Slack connection `slack_conn_id`.

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

        # the two connections are passed to the operator here:
        snowflake_conn_id="snowflake_conn",
        slack_conn_id="slack_conn",

        params={
            "table_name": "ORDERS",
            "col_to_sum": "O_TOTALPRICE"
        },
        sql="""
            SELECT
              COUNT(*) AS row_count,
              SUM({{ params.col_to_sum }}) AS sum_price
            FROM {{ params.table_name }}
        """,
        slack_message="""The table {{ params.table_name }} has
            => {{ results_df.ROW_COUNT[0] }} entries
            => with a total price of {{results_df.SUM_PRICE[0]}}"""
    )
```
