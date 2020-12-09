---
layout: page
title: Minikube Guide
permalink: /guides/minikube/
hide: true
---


# Installing Minikube
Installing minikube requires a Hypervisor to run the MiniKube VM.

## Prerequisites
* Ensure [Kubectl](/guides/kubectl/) is installed on your machine
* HomeBrew for Mac
* A VM Hypervisor, Minikube has driver support for the following hypervisors:
    * virtualbox
    * vmwarefusion
    * kvm (driver installation)
    * hyperkit (driver installation)
    * xhyve (driver installation) (deprecated)

<!-- markdownlint-disable MD036 -->
*Note: It is possible to run Minikube directly on the host machine, without a VM. This can be done by setting the driver flag to 'none' as `–vm-driver=none`. Docker is required if not using a hypervisor.*
<!-- markdownlint-enable MD036 -->

### OSX
There are a number of hypervisor options for Mac:
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads) <!--  Good virtual hardware support, low CPU impact, requires Intel or AMD architecture, Free! -->
* [VMware Fusion](https://www.vmware.com/products/fusion.html?ClickID=dshcox0obyhsmnnboyxx2ssmwt0oyhzcxybk)
* [HyperKit](https://github.com/moby/hyperkit)

In terminal run `brew cask install minikube`


### Linux
* [VirtualBox](https://www.virtualbox.org/wiki/Linux_Downloads)
* [KVM](https://www.linux.com/learn/intro-to-linux/2017/5/creating-virtual-machines-kvm-part-1)

In terminal run:
 `curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/`

This command will install the latest version of MiniKube and add a PATH for minikube.

### Windows
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Hyper-V](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v)


The windows installer is currently experimental, you can download it here: [minikube-windows-amd64](https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe). Once downloaded, rename the file to `minikube.exe` and manually add it to your environment PATH.

For help setting the environment path in Windows 10, see [this guide](https://www.computerhope.com/issues/ch000549.htm).


## Kubernetes Quickstart
For more minikube resources, check out the [Kubernetes Quickstart Guide](https://kubernetes.io/docs/getting-started-guides/minikube/)