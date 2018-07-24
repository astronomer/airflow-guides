# Using Kerberos in Apache Airflow

An overview of the support for Kerberos in Airflow today and how you can use Kerberized hooks.

tags: Airflow, Kerberos

## Support for Kerberos in Airflow

Core support for Kerberos in Airflow is there including a ticket renewer service in the CLI.  Some of its limitations are described in [Airflow - Security](https://airflow.readthedocs.io/en/latest/security.html?highlight=kerberos#kerberos).

## Install

For Kerberos support in Airflow, install it with the `kerberos` install option:

```shell
$ pip install apache-airflow[kerberos]
```

## Kerberized Hooks

As far as hook support goes, each hook has to implement the Kerberos ticket renewal to support it.  Most hooks don't have this yet, but Kerberizing a hook isn't particularly difficult.

A few hooks for services that people commonly use Kerberos for like Spark clusters have the support built-in already.  SparkSubmitHook is one that already has Kerberos support.

We recommend using built-in hooks with Kerberos support if they work for your use case.  If that's not an option, we recommend, contributing support to a particular hook.  You can also reach out to us for Airflow services work.

## Config

Settings for Kerberos can be configured via the `[kerberos]` group in `airflow.cfg`:

```cfg
[kerberos]
ccache = /tmp/airflow_krb5_ccache
# gets augmented with fqdn
principal = airflow
reinit_frequency = 3600
kinit_path = kinit
keytab = airflow.keytab
```

As well as via the `security` setting in `[core]` group.

If you want to use Kerberos authentication via Airflow's experimental REST API, you'll also want to set `auth_backend` under the `[api]` group.  See the [Authentication](https://airflow.readthedocs.io/en/latest/api.html?highlight=kerberos#authentication) section in Airflow's Experimental REST API doc.

## CLI

You can start the Kerberos ticket renewer service via the Airflow CLI

```shell
$ airflow kerberos ...
```

See [Airflow CLI - Kerberos](https://airflow.readthedocs.io/en/latest/cli.html#kerberos) for more info.
