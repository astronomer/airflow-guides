---
title: "Custom Airflow versions on Astronomer"
description: "How to run custom Airflow versions on the Astronomer Platform"
date: 2018-07-25T00:00:00.000Z
slug: "airflow-versions"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Airflow", "Astronomer Platform"]
---

The purpose of this guide is to provide a quick reference for running an alternate version of Airflow on the Astronomer Platform.  Astronomer allows you to run any Airflow version you'd like.

Use cases

- You can use this to run older versions of Airflow such as 1.8 or newer versions such as release candidates.
- You can also use this guide for a custom build of Airflow, for example, with commits that aren't upstreamed yet.

## Prerequisites

- To run a custom version of Airflow, you'll need to be able to build and publish Docker images to a Docker registry such as Docker Hub.

## 1. Fork Airflow

Fork [the Airflow repo](https://github.com/apache/incubator-airflow).

*Note: You can skip this step if your desired tag / branch already exists on apache/incubator-airflow.*

## 2. Fork Astronomer

Fork [the Astronomer repo](https://github.com/astronomerio/astronomer).

TODO: alternatively could probably just pass the docker args without forking

## 3. Change the Airflow version

```
git clone <your-astronomer-fork-url>
cd astronomer
```

In the [Airflow Dockerfile](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/Dockerfile), change:

- `ORG` to be your GitHub organization name or username depending on where you forked Airflow.  If you're using the Apache repo, set it to `"apache"`.
- `VERSION` to be your desired Airflow tag or branch to install from.  For example, `"1.10.0rc2"`.

## 4. Build and push the custom Docker image

```shell
docker build -t my-org/my-airflow -t my-org/my-airflow:my-tag .
docker push my-org/my-airflow:my-tag
```

## 5. Update your `config.yaml` for Astronomer

```yaml
airflow:
  images:
    airflow:
      name: my-org/my-airflow
      tag: my-tag
```

## 6. Install the chart

Finally, continue in the [Install Guide](https://www.astronomer.io/guides/install/) from the `helm install ...` step.

## Future

In the future, we plan to offer the ability to set the Airflow version when creating a new deployment in our Orbit UI web app.
