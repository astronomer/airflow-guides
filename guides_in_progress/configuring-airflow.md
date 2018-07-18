---
layout: page
title: Configuring Airflow
permalink: /guides/configuring-airflow/
hide: true
---

## Objective

Configure Airflow specific settings via Helm charts and Kubernetes Secrets or modification of your Airflow image `Dockerfile`.

## Prerequisites

* General familiarity with Kubernetes Secrets
* A clone of the [Astronomer Platform Helm charts](https://github.com/astronomerio/helm.astronomer.io){:target="_blank"}

## Configuration File

_Note - If you have completed the [Google Cloud Platform Guide](/guides/google-cloud/) you can skip this step._

Once you have cloned the Helm repository, change into that directory. The Helm charts are built to be customizable and tailored to your unique environment. The way we customize an installation is through a YAML configuration file. This file can contain global configurations that are used in multiple charts, or chart specific configurations. Global configurations are underneath the top-level `global` key. Chart specific configurations will be nested under top-level keys that correspond to the chart name. For example, to override values in the `airflow` chart, you will need to create a top-level key, `airflow`, and nest configurations under it.

All charts are located under the `charts` directory and each chart contains a default `values.yaml` file that contains every possible configuration as well as the default value. The charts repository also contains a `values.yaml` file in the root of the project that overrides several values and sets up some default values. You should not edit these files directly. Instead, let's create a new YAML file where you can override these configurations, and provide some of the required configurations for the installation.

```bash
cp config.tpl.yaml config.yaml
```

You now have a file named `config.yaml` where you can make any configuration changes you need to. This file will contain keys for required fields, but any configuration can be overridden. Check out the root `values.yaml` file to get a feel for the structure of this file.

## Airflow Configuration via Helm Charts

### Airflow Configuration Overview

Immediately after deploying your first cluster, you probably want to begin to customize your deployment for your production needs. This is where Airflow configurations come into play. Airflow stores these configurations in [airflow.cfg](https://github.com/apache/incubator-airflow/blob/master/airflow/config_templates/default_airflow.cfg){:target="_blank"}. In this file, you will find a full list of configurable settings.

Note that this file is broken out into sections denoted by the square bracket syntax ([example]). This section syntax is important when we go to define environment variables that map to configurations in `airflow.cfg`. The standard template for this mapping is `$AIRFLOW__{SECTION}__KEY` (note the double underscores).

For example, if we want to change `airflow_home` (the first setting in `airflow.cfg`), we look above the setting to find what section of the document it is in. In this case `airflow_home` is under the `[core]` configuration section. Using the above configuration mapping template would yield `$AIRFLOW__CORE__AIRFLOW_HOME` environment variable.

### Passing ENVs into Helm Charts

With the environment variables created, we are now ready to pass configuration overrides into the Astronomer platform Helm charts. In your `config.yaml` you find a section for Airflow overrides, under which you will see two more sections.

* `airflow.env`
  * This section can be used to override general configurations. The name and value of each env can be passed in plain text directly into this file.
* `airflow.secret`
  * There will be some configurations you do not want to store in plain text. This section allows you to specify an ENV that points to a Kubernetes Secret.

### Creating Secrets

If you have chosen to store any sensitive information in Kubernetes secrets you will also need to create those secrets before your next deploy. We demo what that looks like below.

## Example

In this example, we will assume I want to configure my deployment to point to an SMTP server for sending out alerts on DAG failures.

### Airflow ENVs

Looking at `airflow.cfg` I see that there is a relevant section titled `[smtp]` as well as 7 configurations under this section. Using the variable to env mapping template above, I will convert then to ENVs

* `$AIRFLOW__SMTP__SMTP_HOST`
* `$AIRFLOW__SMTP__SMTP_USER`
* `$AIRFLOW__SMTP__SMTP_MAIL_FROM`
* `$AIRFLOW__SMTP__SMTP_SSL`
* `$AIRFLOW__SMTP__SMTP_PORT`
* `$AIRFLOW__SMTP__SMTP_HOST`
* `$AIRFLOW__SMTP__SMTP_PASSWORD`

### Helm Chart Passthrough

Now that we have our relevant SMTP environment variables, we can pass them into our `config.yaml` overrides file.

```yaml
airflow:
  env:
      # Airflow SMTP Settings
    - name: AIRFLOW__SMTP__SMTP_STARTTLS
      value: "True"
    - name: AIRFLOW__SMTP__SMTP_USER
      value: "demo@example.com"
    - name: AIRFLOW__SMTP__SMTP_MAIL_FROM
      value: "demo@example.com"
    - name: AIRFLOW__SMTP__SMTP_SSL
      value: "False"
    - name: AIRFLOW__SMTP__SMTP_PORT
      value: "587"
    - name: AIRFLOW__SMTP__SMTP_HOST
      value: "example.smtp-host.com"
  secret:
    - name: AIRFLOW__SMTP__SMTP_PASSWORD
      value: smtp-password
```

### Creating A Secret

In the above example, our secret is an ENV pointing to a secret named `smtp-password`.

```bash
kubectl create secret generic smtp-password --from-literal value='123456password' --namespace astronomer
```

### Deployment and Testing

Depending on whether or not you are performing a first time deploy or upgrade you will need to run a `helm install` or a `helm upgrade` to push your latest configuration.

After deployment we can test to make sure your configurations were pushed successfully.

First, get the name of your webserver pod

```bash
kubectl get pods --namespace astronomer | grep webserver
```

Next you can exec into the webserver pod

```bash
kubectl exec -it [WEBSERVER POD NAME] --namespace astronomer /bin/bash
```

Once inside of your Airflow webserver pod's shell you can check ENVs configured on that pod

```bash
printenv
```

## Airflow Configuration via Dockerfile

Depending on your specific permissions to your Kubernetes cluster, it may not always be possible to modify and deploy the Helm Charts. In this case you can modify the `Dockerfile` which is created in your project root when when you run `astro airflow init` from the [astro-cli](https://github.com/astronomerio/astro-cli). When running your Airflow project locally, this has the benefit of allowing you modify and test Airflow configuration changes that you could not test without a deployment to your cluster. When deploying your Airflow project to the cluster this method gives you the ability to set project level (as opposed to cluster level) configurations.

### Example: Override an airflow.cfg config setting via environment variable

You can override settings in the airflow.cfg config file by providing environment variables that match the following format: `AIRFLOW__<GROUP>__<SETTING>`.

For example, to override `donot_pickle` setting in the `[core]` group, setting it to true, add the following line to your Dockerfile:

```docker
ENV AIRFLOW__CORE__DONOT_PICKLE True
```

Settings modified in this way will apply to the scheduler, webserver, and task nodes the next time the cluster is started.

## Airflow Configuration via airflow.cfg

One other way to supply defaults is to provide your own [airflow.cfg](https://github.com/apache/incubator-airflow/blob/master/airflow/config_templates/default_airflow.cfg). This will allow you to provide a default configuration to your Airflow instance without specifying any environment variables. To do this, place an `airflow.cfg` tied to your current version of Airflow in your Astronomer project directory. This file will be injected into your image at build time. Please note that any configurations passed in through the  `airflow.cfg` will be overwritten by ENVs passed in via a `Dockerfile` or Helm charts.
