---
title: "Choosing a Base Domain for Astronomer"
description: "Choosing a Base Domain for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-base-domain"
heroImagePath: "https://assets.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

You need to choose a base domain for your Astronomer installation, something like
`astro.mydomain.com`. Each Airflow cluster you install will be accessible at
a URL like `unique-name-airflow.astro.mydomain.com` and the admin application
will be installed to `app.astro.mydomain.com`, the Grafana dashboard will be
installed to `grafana.astro.mydomain.com` etc.

You will need to edit the DNS for this domain. If you work for a big
company it might be easier to just register a new domain like `astro-mycompany.com`
that you'll have full control of, and Astronomer can be installed on that root
domain (`app.astro-mycompany.com` etc).

Note: For the purpose of our tutorial, our application domain is
`astro.mycompany.com`.
