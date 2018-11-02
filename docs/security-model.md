---
title: "Security Model"
description: "The Astronomer Security Model"
date: 2018-10-12T00:00:00.000Z
slug: "security-model"
menu: ["root"]
position: [4]
---


## Cloud Security

Since Astronomer Cloud is hosted entirely on our infrastructure, we often get questions about how data is received by our platform. In Cloud, we run a single NAT that all internet bound traffic flows through. We don't persist any of your data, and all computation runs in short lived containers that die after the task is finished.

If you're interested in having a dedicated NAT, you'll have to use our Enterprise product, which is hosted entirely on your infrastructure.

## Enterprise Security

Astronomer Enterprise is deployed and hosted in your cloud via Kubernetes, so it complies to your internal security specifications.

## User Access

