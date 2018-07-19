---
title: "Astronomer Install Guide"
description: "Install the Astronomer Platform"
date: 2018-07-17T00:00:00.000Z
slug: "install"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/TheAirflowUI_preview.png"
tags: ["Astronomer Platform", "Airflow", "Getting Started"]
---

For the purpose of this doc, our installation domain is
`mercury.astronomer.io`.  You should set this value to your
desired installation domain name.

This is where we recommend getting started with the Astronomer Platform.

---

For the purpose of this doc, our application domain is `mercury.astronomer.io`.  You should set this value to your desired domain name.

## 1. Prerequisites

Please see the following doc for prerequisites based on your cloud:

- [AWS](/guides/install-aws)
- [GCP](/guides/install-gcp)

The GCP doc can serve as a requirements reference if your cloud is not yet listed.

## 2. Generate SSL/TLS certificates

The recommended way to install the Astronomer Platform is on a subdomain and not on your root domain.  If you don't have a preference, a good default subdomain is `astro`.  (For the rest of this guide, we'll continue to use `mercury.astronomer.io`.)

Note: We recommend following the process below to generate trusted certificates.  Self-signed certificates are not recommended for the Astronomer Platform.

We'll create two SSL/TLS certs:

1. A standard certificate for the base domain.
1. A wildcard certificate for dynamic dashboards like the Astronomer app, Airflow webserver, Flower, Grafana, etc.

Run:

```shell
$ docker run -it --rm --name letsencrypt -v ~/dev/letsencrypt/etc/letsencrypt:/etc/letsencrypt -v ~/dev/letsencrypt/var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot:latest certonly -d "mercury.astronomer.io" -d "*.mercury.astronomer.io" --manual --preferred-challenges dns --server https://acme-v02.api.letsencrypt.org/directory
```

Sample output:

```plain
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator manual, Installer None
Obtaining a new certificate
Performing the following challenges:
dns-01 challenge for mercury.astronomer.io
dns-01 challenge for mercury.astronomer.io

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
NOTE: The IP of this machine will be publicly logged as having requested this
certificate. If you're running certbot in manual mode on a machine that is not
your server, please ensure you're okay with that.

Are you OK with your IP being logged?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name
_acme-challenge.mercury.astronomer.io with the following value:

0CDuwkP_vNOfIgI7RMiY0DBZO5lLHugSo7UsSVpL6ok

Before continuing, verify the record is deployed.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue
```

Follow the directions in the output to perform the two domain challenges by adding the two DNS TXT records mentioned.  Follow your DNS provider's guidance for how to set two values under the same key.

We recommend temporarily setting a short time to live (TTL) value for the DNS records to expedite the setup process.

## 3. Create a Kubernetes secret with your PostgreSQL connection

If you do not already have a PostgreSQL cluster, we recommend using a service like Compose, Amazon RDS, or Google Cloud SQL.

This PostgreSQL user needs permissions to create users, schemas, databases, and tables.

Run:

```shell
$ kubectl create secret generic astronomer-bootstrap --from-literal connection="postgres://admin:${PASSWORD}@aws-us-east-1-portal.32.dblayer.com:27307" --namespace astronomer-ee
```

Note: Change user from `admin` if you're creating a user instead of using the default, it needs permission to create databases, schemas, and users.

## 4. Create a Kubernetes secret for the SSL/TLS certificates

```shell
$ kubectl create secret tls astronomer-mercury-tls --kubeconfig=/home/schnie/.kube/config --key /home/schnie/dev/letsencrypt/etc/letsencrypt/live/mercury.astronomer.io/privkey.pem --cert /home/schnie/dev/letsencrypt/etc/letsencrypt/live/mercury.astronomer.io/fullchain.pem --namespace astronomer-ee
```

## 5. Generate credentials for Google OAuth

See the [Google OAuth credentials guide](/guides/google-oauth-creds).

Note: We're also adding support for Auth0 very soon as an alternative OAuth provider.

## 6. Configure Astronomer

Now, we'll set the configuration values for the Astronomer Helm chart.

Create a `config.yaml` for your domain setting overrides by copying [config.tpl.yaml](https://github.com/astronomerio/helm.astronomer.io/blob/master/config.tpl.yaml) if you don't already have one.

Change the branch on GitHub to match your desired Astronomer Platform version.

In `config.yaml`, set the following values:

```yaml
global:
  baseDomain: ...
  tlsSecret: ...

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
$ helm install -f config.yaml . --namespace astronomer-ee
```

Click the link in the output notes to log in to the Astronomer app.
