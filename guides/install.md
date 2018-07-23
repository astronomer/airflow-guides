---
title: "Astronomer Install Guide"
description: "Install the Astronomer Platform"
date: 2018-07-17T00:00:00.000Z
slug: "install"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Astronomer Platform", "Airflow", "Getting Started"]
---

*For the purpose of this doc, our application domain is
`astro.mycompany.com`.  You should set this value to your
desired domain name.*

## 1. Prerequisites

Please see the following doc for prerequisites based on your cloud:

- [AWS](https://www.astronomer.io/guides/install-aws)
- [GCP](https://www.astronomer.io/guides/install-gcp)

The GCP doc can serve as a requirements reference if your cloud is not yet listed.

## 2. Generate a wildcard TLS certificate

The recommended way to install the Astronomer Platform is on a subdomain and not on your root domain, or aquiring a new domain.  If you don't have a preference, a good default subdomain is `astro`.  (For the rest of this guide, we'll continue to use `astro.mycompany.com`.)

We recommend purchasing a TLS certificate signed by a Trusted CA. Alternatively you can follow the guide below to manually generate a trusted wildcard certificate via Let's Encrypt (90 day expiration).  This certificate generation process and renewal can be automated in a production environment with a little more setup.

Note: Self-signed certificates are not supported on the Astronomer Platform.

Run:

```shell
$ docker run -it --rm --name letsencrypt -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot:latest certonly -d "*.astro.mycompany.com" --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory
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

## 3. Create a Kubernetes secret with your PostgreSQL connection

If you do not already have a PostgreSQL cluster, we recommend using a service like Compose, Amazon RDS, or Google Cloud SQL.

This PostgreSQL user needs permissions to create users, schemas, databases, and tables.

For testing purposes, you can quickly get started using the PostgreSQL helm chart.

Run:
```shell
$ helm install --name astro-db stable/postgresql --namespace astronomer
```

Depending on where your Postgres cluster is running, you may need to adjust the connection string in the next step to match your environment. If you installed via the helm chart, you can run the command that was output by helm to set the `${PGPASSWORD}` environment variable, which can be used in the next step. Once that variable is set, you can run this command directly to create the bootstrap secret.


Run:

```shell
$ kubectl create secret generic astronomer-bootstrap --from-literal connection="postgres://postgres:${PGPASSWORD}@astro-db-postgresql:5432" --namespace astronomer
```

Note: Change user from `postgres` if you're creating a user instead of using the default, it needs permission to create databases, schemas, and users.

## 4. Create a Kubernetes secret for the TLS certificates

```shell
$ kubectl create secret tls astronomer-tls --key /etc/letsencrypt/live/astro.mycompany.com/privkey.pem --cert /etc/letsencrypt/live/astro.mycompany.com/fullchain.pem --namespace astronomer
```

## 5. Generate credentials for Google OAuth

See the [Google OAuth credentials guide](/guides/install-google-oauth).

Note: We're also adding support for Auth0 very soon as an alternative OAuth provider to simplify installation.

## 6. Configure Astronomer

Now, we'll set the configuration values for the Astronomer Helm chart.

Create a `config.yaml` for your domain setting overrides by copying [config.tpl.yaml](https://github.com/astronomerio/helm.astronomer.io/blob/master/config.tpl.yaml) if you don't already have one.

Change the branch on GitHub to match your desired Astronomer Platform version.

In `config.yaml`, set the following values:

```yaml
global:
  baseDomain: <your-basedomain>
  tlsSecret: astronomer-tls

astronomer:
  auth:
    google:
      enabled: true
      clientId: <your-client-id>
      clientSecret: <your-client-secret>
```

Replace `<your-client-id>` and `<your-client-secret>` with the values from the previous step.

## 7. Install Astronomer

```shell
$ helm install -f config.yaml . --namespace astronomer
```

Click the link in the output notes to log in to the Astronomer app.
