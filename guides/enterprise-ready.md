---
title: "Are you Astronomer Enterprise ready?"
description: "Ensure you meet the pre-requisites to run the Astronomer Enterprise platform"
date: 2018-11-01T00:00:00.000Z
slug: "enterprise-ready"
heroImagePath: null
tags: ["Astronomer Platform", "admin-docs"]
---

The Astronomer platform is Kubernetes agnostic. This means that any Kubernetes management solution should support the installation, and management of the Astronomer platform. To ensure the platform can be effectively installed and managed, ensure your team can meet the following requirements.


* A kubernetes cluster managed by one of these solutions: https://kubernetes.io/docs/setup/pick-right-solution/
* Admin level access to the Kubernetes cluster
* Ability to provision a Tiller service account for use with Helm
* A base domain
* A CA signed wildcard for your base domain. This cannot be a self-signed certificate
* A postgres database
* A wildcard DNS A record


Need help installing the Astronomer platform? [Reach out](https://www.astronomer.io/contact/?from=/) to discuss install solutions. 
