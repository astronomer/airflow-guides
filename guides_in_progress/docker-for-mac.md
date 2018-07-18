---
layout: page
title: Docker for Mac Guide
permalink: /guides/docker-for-mac/
hide: true
---



# Install Kubernetes Locally via Docker For Mac Edge

This guide details the steps to get Kubernetes installed locally on a machine running OSx. At the time of writing Docker Kube is only available on Docker For Mac Edge meaning that some features may not behave as fully intended.

## Requirements

- macOS
- [Docker for Mac Edge][1]

## Kubernetes For Mac Install

This section will walk you through the installation of Kubernetes on Docker. It is recommended that you use Kubernetes on Docker and not [minikube][2]{:target="_blank"} as several users have failed to get working installs via the minikube method.

### Installation Steps

1. [Download Docker For Mac Edge][1]{:target="_blank"}
1. [Enable Kubernetes Support on Docker Edge][3]{:target="_blank"}

### Verification

1. Verify install by running the `kubectl` command in terminal

### Note: Docker for Mac Edge stability

<!-- markdownlint-disable MD036 -->
*Warning: Docker for Mac Edge is somewhat unstable*
<!-- markdownlint-enable MD036 -->

While Kubernetes for Docker for Mac is in beta, you may see Kubernetes stop working after an upgrade, need to reset the Kubernetes cluster, reset Docker itself to factory defaults, or a full uninstall and reinstall.

Given this, we recommend *not* installing new releases right away if you are doing production work.  A more stable approach is to watch [the issues](https://github.com/docker/for-mac/issues){:target="_blank"} related to Kubernetes in the the days following a new release.

## Homebrew Install

Homebrew is a package manager that describes itself as installing `the stuff you need that Apple didn’t.'

### Installation Steps

1. [Install Homebrew][4]{:target="_blank"}

### Verification

1. Verify install by running the `homebrew` command in terminal

### Helm via Homebrew Install

Helm is a package manager for Kubernetes itself. In Helm a package is called a Chart. Under the hood a `Chart` is a collection of files definiting the configuration of Kubernetes resources. The [Kubernetes github organization][5]{:target="_blank"} provides a list of [stable Charts][6]{:target="_blank"}.

### Installation Steps

There are a couple of [helm installation options][7]{:target="_blank"}, for this install we will be using homebrew.

1. run `brew install kubernetes-helm`
1. run `helm init`
  - This command will deploy the helm server to your Docker Kubernetes cluster

### Verification

1. verify install by running the `helm version` command in terminal

## Kubernetes WebUI Dashboard Install

The Kubernetes dashboard is the command central of your Kubernetes cluster. From here you can graphically monitor the status of deployments as well as dive into the logs to troubleshoot failed deployments. We will be using the install from the [Kubernetes Githup][8]{:target="_blank"}.

### Installation Steps

1. `kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml`
  - This will pulldown and apply the official Kubernetes dashboard.
1. `kubectl proxy`
  - This will expose the dashboard to your localhost

### Verification

1. Verify successful deployment of dashboard by navigating to dashboard homepage found at
  - <http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/>

[1]: https://docs.docker.com/docker-for-mac/install/#download-docker-for-mac  "Docker For Mac Edge"
[2]: https://github.com/kubernetes/minikube                                   "MiniKube"
[3]: https://docs.docker.com/docker-for-mac/#kubernetes                       "Kubernetes on Docker"
[4]: https://docs.brew.sh/Installation.html                                   "Homebrew Package Manager"
[5]: https://github.com/kubernetes                                            "Kubernetes Github"
[6]: https://github.com/kubernetes/charts/tree/master/stable                  "Stable Helm Charts"
[7]: https://github.com/kubernetes/helm/blob/master/docs/install.md           "Helm Installation Instructions"
[8]: https://github.com/kubernetes/dashboard                                  "Kubernetes Dashboard Installation"
