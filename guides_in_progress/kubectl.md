---
layout: page
title: Kubectl
permalink: /guides/kubectl/
hide: true
---


## Installation

Installing Kubectl is pretty simple.

### Linux
If you're running Ubuntu or Debian, install with the native package manager:

```
apt-get update && apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF
apt-get update
apt-get install -y kubectl
```
### OSX
Install Kubectl using Homebrew on mac

```
brew install kubectl
```

Verify kubectl is installed and up-to-date

```
kubectl version
```

### Windows
Install kubectl on windows using cURL

```
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.10.3/bin/windows/amd64/kubectl.exe
```
Add the binary to your environment PATH and you're all set.

For more installation options, visit the official Kubectl install guide:[https://kubernetes.io/docs/tasks/tools/install-kubectl/](https://kubernetes.io/docs/tasks/tools/install-kubectl/){:target="_blank"}

### Debugging Astronomer Airflow with kubectl.


#### Optional
_Kubectx_
Download kubectx for an easy way to switch between namespaces and clusters. This will prevent you from having to specify a namespace with each command.

### Basic Commands

```
bash
kubectl get pods
```
This will return a list of pods and their current status.


To delete a pod, run:

```
bash
kubectl delete po/POD_NAME 
```
To restart any particular component of your Airflow setup, you can simply delete the pod and it will spin back up.
**Note: Do not delete the database pod**

If you are seeing unexpected behavior in your Airflow deployment, the answer might lie in the scheduler or webserver logs:
```
bash
kubectl logs po/POD_NAME -f
```
This will follow the logs on your terminal. The scheduler and webserver logs tend to pile up quickly, so it might be best to run this after restarting either of those pods.
