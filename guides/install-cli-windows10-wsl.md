---
title: "The Astronomer CLI on the Windows Subsystem for Linux"
description: "Using our CLI on the Windows Subsystem for Linux"
date: 2018-05-23T00:00:00.000Z
slug: "install-cli-windows10-wsl"
heroImagePath: "https://assets.astronomer.io/website/img/guides/markus-spiske-207946-unsplash.jpg"
tags: ["Airflow", "CLI", "Product Documentation"]
---

## Astronomer CLI in WSL

This guide will walk you through the setup and configuration process for using the Astronomer CLI in the Windows Subsystem for Linux (WSL) on Windows 10. At this point, you should be running in the bash terminal and have the [the WSL enabled](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

(*Note:* We're using Ubuntu as our Linux flavor of choice,but this giude should work for other distrubutions as well).

Much of the setup process is borrowed from a guide written by Nick Janetakis. Find the full guide here: [Setting Up Docker for Windows and WSL to Work Flawlessly](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

## Step 1. Install Docker ce for windows

Follow the docker for windows install guide here: [Install Docker for windows](https://docs.docker.com/docker-for-windows/install/)

## Step 2. Expose the Docker Daemon

In your docker settings, under general, enable the `Expose daemon on tcp://localhost:2375 without TLS` setting. This will allow the docker daemon running on windows to act as a remote docker service for our WSL instance.

## Step 3. Install Docker for Linux in WSL

In your WSL termninal, follow the Docker CE for Ubuntu install guide here: [Install Docker CE for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

Docker wil lnot run in the WSL instance, however this will give us access to the docker cli through our linux environment. 

## Step 4. Connect your WSL instance to Docker on Windows

We now need to point our docker host route to the remote docker daemon running in Windows. To do this we need to add an export path to our `~/.bashrc` file.

Run: `echo "export DOCKER_HOST=tcp://0.0.0.0:2375" >> ~/.bashrc && source ~/.bashrc` to add a new line to your bashrc file pointing the docker host to your exposed  daemon and re-source your bashrc file. 

## Step 5. Custom mount points

To ensure docker can properly mount volumes, we need to create custom mount paths that work in the WSL instance.

(*Note:* The process differs depending on the version of Windows 10 you're running. In our case we're running build 1709. See the full guide for more details about later builds).

Create a new mount point directory:

`sudo mkdir /c`

Then bind this mount point:

`sudo  mount --bind /mnt/c /c`

You're all set. You can now run `docker run hello-world` through your WSL instance to ensure everything works as expected. Keep in mind you will need to bind your mount point each time you start up a new WSL instance. 

You can now setup the Astronomer CLI and begin deploying DAGs following our guide here: [Astronomer CLI](/guides/cli)

### Potential Postgres Error

- As a WSL user, you might see the following error when trying to call `astro airflow start` on your newly created workspace:

```
Sending build context to Docker daemon  8.192kB
Step 1/1 : FROM astronomerinc/ap-airflow:latest-onbuild
# Executing 5 build triggers
 ---> Using cache
 ---> Using cache
 ---> Using cache
 ---> Using cache
 ---> Using cache
 ---> f28abf18b331
Successfully built f28abf18b331
Successfully tagged hello-astro/airflow:latest
INFO[0000] [0/3] [postgres]: Starting
Pulling postgres (postgres:10.1-alpine)...
panic: runtime error: index out of range
goroutine 52 [running]:
github.com/astronomerio/astro-cli/vendor/github.com/Nvveen/Gotty.readTermInfo(0xc4202e0760, 0x1e, 0x0, 0x0, 0x0)
....
```

This is an issue pulling Postgres that should be fixed by running the following:

```
Docker pull postgres:10.1-alpine
```
