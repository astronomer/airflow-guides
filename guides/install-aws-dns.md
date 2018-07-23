---
title: "Setting up DNS for AWS"
description: "Setting up DNS for AWS"
date: 2018-07-17T00:00:00.000Z
slug: "install-aws-dns"
heroImagePath: null
tags: ["admin-docs"]
---

Once you've deployed the Astronomer platform in your AWS VPC, you will need to create a new CNAME record in your DNS to route traffic to the ELB.

Navigate to your newly created load balancer:

![aws-elb](/assets/img/elb_storage.png)

Copy the `DNS name:` route and use this to create a new wildcard CNAME record in you DNS. If your base domain is `organization.io` your wildcard record should be `*.organization.io` and will route traffic to your ELB using that DNS name.
