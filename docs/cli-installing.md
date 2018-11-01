---
title: "Installing"
description: "How to get started using the Astro CLI on Mac, Linux, and Windows."
date: 2018-10-12T00:00:00.000Z
slug: "cli-installing"
menu: ["Astro CLI"]
position: [1]
---
# Installing the CLI

To install the most recent version of our CLI on your machine, run the following command.

Via `curl`:
  ```
   curl -sSL https://install.astronomer.io | sudo bash
   ```

## Previous Versions

If you'd like to install a previous version of our CLI, the following command should do the trick.

Via `curl`:
   ```
    curl -sSL https://install.astronomer.io | sudo bash -s -- [TAGNAME]
   ```
   
For example:
   ```
curl -sSL https://install.astronomer.io | sudo bash -s -- v0.3.1
   ```


**Note:** If you get mkdir error during installation please download and run [godownloader](https://raw.githubusercontent.com/astronomerio/astro-cli/master/godownloader.sh) script locally. 

    $ cat godownloader.sh | bash -s -- -b /usr/local/bin