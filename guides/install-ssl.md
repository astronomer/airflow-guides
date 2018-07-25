---
title: "Getting SSL certificate for Astronomer"
description: "Getting SSL certificate for Astronomer"
date: 2018-07-17T00:00:00.000Z
slug: "install-ssl"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["admin-docs"]
---

The recommended way to install the Astronomer Platform is on a subdomain and not on your root domain, or acquiring a new domain.  If you don't have a preference, a good default subdomain is `astro`.  (For the rest of this guide, we'll continue to use `astro.mycompany.com`.)

You'll need to obtain a wildcard SSL certificate for `*.astro.mydomain.com` not
only to protect the web endpoints (so it's `https://app.astro.mydomain.com`)
but is also used by Astronomer inside the platform to use TLS encryption between
pods.

* Buy a wildcard certificate from wherever you normally buy SSL
* Get a free 90-day wildcard certificate from letsencrypt

We recommend purchasing a TLS certificate signed by a Trusted CA. Alternatively you can follow the guide below to manually generate a trusted wildcard certificate via Let's Encrypt (90 day expiration).  This certificate generation process and renewal can be automated in a production environment with a little more setup.

> Note: Self-signed certificates are not supported on the Astronomer Platform.

Run:

```shell
docker run -it --rm --name letsencrypt -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot:latest certonly -d "*.astro.mycompany.com" --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory
```

Sample output:

```plain
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator manual, Installer None
Obtaining a new certificate
Performing the following challenges:
dns-01 challenge for astro.mycompany.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
NOTE: The IP of this machine will be publicly logged as having requested this
certificate. If you're running certbot in manual mode on a machine that is not
your server, please ensure you're okay with that.

Are you OK with your IP being logged?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name
_acme-challenge.astro.mycompany.com with the following value:

0CDuwkP_vNOfIgI7RMiY0DBZO5lLHugSo7UsSVpL6ok

Before continuing, verify the record is deployed.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue
```

Follow the directions in the output to perform the domain challenge by adding the DNS TXT record mentioned.  Follow your DNS provider's guidance for how to set the TXT record.

We recommend temporarily setting a short time to live (TTL) value for the DNS record should you need to retry creating the cert.
