---
title: "Config"
description: "Installing the Config for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "ee-installation-config"
---
Here, we'll set the configuration values for the Astronomer Helm chart.

`cd` to where you cloned `helm.astronomer.io`

Create a `config.yaml` for your domain setting overrides by copying [config.tpl.yaml](https://github.com/astronomerio/helm.astronomer.io/blob/master/config.tpl.yaml) if you don't already have one.

```
cp config.tpl.yaml config.yaml
```

Change the branch on GitHub to match your desired Astronomer Platform version.

In `config.yaml`, set the following values:

```yaml
global:
  baseDomain: <your-basedomain>
  tlsSecret: astronomer-tls

astronomer:
  auth:
    google:
      enabled: true
      clientId: <your-client-id>
      clientSecret: <your-client-secret>
```

Replace `<your-client-id>` and `<your-client-secret>` with the values from the previous step.