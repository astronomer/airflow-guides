---
title: "Astro CLI Commands"
description: "Command reference for the Astronomer CLI"
date: 2018-10-12T00:00:00.000Z
slug: "cli-command-reference"
menu: ["Astro CLI"]
position: [4]
---

# Available Commands:

At the highest level running `astro` will give you the following options:
```

  airflow     Manage airflow projects and deployments
  auth        Mangage astronomer identity
  cluster     Manage Astronomer EE clusters
  config      Manage astro project configurations
  deployment  Manage airflow deployments
  help        Help about any command
  upgrade     Check for newer version of Astronomer CLI
  user        Manage astronomer user
  version     Astronomer CLI version
  workspace   Manage Astronomer workspaces
```

Running `astro airflow`:
```
  deploy      Deploy an airflow project
  init        Scaffold a new airflow project
  kill        Kill a development airflow cluster
  logs        Output logs for a development airflow cluster
  ps          List airflow containers
  start       Start a development airflow cluster
  stop        Stop a development airflow cluster
```

Running `astro auth`
```
  login       Login to Astronomer services
  logout      Logout of Astronomer services
  ```

Running `astro cluster`:
```
    list        List known Astronomer Enterprise clusters
    switch      Switch to a different cluster context
```

Running `astro config`:
```
  get         Get astro project configuration
  set         Set astro project configuration
```

Running `astro deployment`:
```
  create      Create a new Astronomer Deployment
  delete      Delete an airflow deployment
  list        List airflow deployments
  update      Update airflow deployments
```

Running `astro user`:
```
  create      Create a user in the astronomer platform
```

Running `astro workspace`:
```
  create      Create an astronomer workspaces
  delete      Delete an astronomer workspace
  list        List astronomer workspaces
  switch      Switch to a different astronomer workspace
  update      Update an Astronomer workspace
  user        Manage workspace user resources
```
