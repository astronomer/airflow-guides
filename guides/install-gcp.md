---
title: "Astronomer Install Guide - Google Cloud Platform Prerequisites"
description: "Setup the Astronomer Platform prerequisites on GCP"
date: 2018-07-17T00:00:00.000Z
slug: "install-gcp"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Astronomer Platform", "Getting Started"]
---

This guide describes the prerequisite steps to install Astronomer on Google Cloud Platform (GCP).  After completing it, return to the main [install guide](/guides/install) to complete the process.

## 1. Generate a static IP and create an A record for it

```shell
$ gcloud compute addresses create astronomer-mercury-external-ip --region us-east4 --project astronomer-prod
$ gcloud compute addresses describe astronomer-mercury-external-ip --region us-east4 --project astronomer-prod --format 'value(address)'
```

The A record should be `*.<base domain>` pointing to the static IP.

---

Now return to the [install guide](/guides/install) to install Astronomer.
