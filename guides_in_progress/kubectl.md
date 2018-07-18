---
layout: page
title: Kubectl
permalink: /guides/kubectl/
hide: true
---


## Installation

Installing Kubectl is pretty simple.

### Linux
If you're running Ubuntu or Debian, install withthe native package manager:

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

### MiniKube

With Kubectl installed, you're ready to move on to [Installing MiniKube](/guides/minikube/) to run your own kubernetes instance locally.