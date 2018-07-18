---
layout: page
title: Upgrade Astronomer
permalink: /guides/upgrade/
hide: true
---

## Upgrade Astronomer

Once the Astronomer umbrella chart is installed, you may want to make config changes, or upgrade to a newer release.

Helm makes it easy to update a Kubernetes cluster.

Most updates can be installed by running:

```bash
cd astronomer-ee
helm upgrade -f config.yaml --namespace astronomer <release name> .
```

There are some cases where Helm cannot do an automatic upgrade which can be resolved by doing a fresh install.
