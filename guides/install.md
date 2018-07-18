---
title: "Astronomer Platform v0.3.0 Install Guide"
description: "Install the Astronomer Platform"
date: 2018-07-17T00:00:00.000Z
slug: "install"
heroImagePath: "https://cdn.astronomer.io/website/img/guides/datastores.png"
tags: ["Astronomer Platform", "Airflow", "Getting Started"]
---

The purpose of this guide is to describe the Astronomer Platform installation process for platform owners and end users.

This is where we recommend getting started with Astronomer.

---

Upgrade process overview:

1. Pause active DAGs
1. Create new Astronomer cluster
1. Deploy to new cluster
1. Unpause DAGs that were paused in (1) and test new cluster
1. Tear down old Astronomer cluster

---

For the purpose of this doc, our application domain is `mercury.astronomer.io`.  You should set this value to your desired domain name.

1. **Generate the SSL/TLS certificates.**

	We'll create two SSL certs:

	1. A standard certificate for the base domain.
	1. A wildcard certificate to support dynamic dashboards like the Astronomer app (app.<your base domain>), Airflow webserver, Flower, and Grafana.

	This requires performing two domain challenges.  Add the two DNS TXT records mentioned in the output.

	Follow your DNS provider's guidance for how to set two values under the same key.

	We recommend temporarily setting a short time to live (TTL) value for the DNS records to expedite the setup process.

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

1. **Create a Kubernetes secret with your PostgreSQL connection.**

	If you do not already have a PostgreSQL database, we recommend using a service like Compose, Amazon RDS, or Google Cloud SQL.

	This PostgreSQL user needs permissions to create users, schemas, databases, and tables.

	Run:

	```shell
	$ kubectl create secret generic astronomer-bootstrap --from-literal connection="postgres://admin:${PASSWORD}@aws-us-east-1-portal.32.dblayer.com:27307" --namespace astronomer-ee
	```

1. **Generate a static IP and create an A record for it.**

	```shell
	$ gcloud compute addresses create astronomer-mercury-external-ip --region us-east4 --project astronomer-prod
	$ gcloud compute addresses describe astronomer-mercury-external-ip --region us-east4 --project astronomer-prod --format 'value(address)'
	```

	- A record details: *.<base domain> pointing to the static IP

1. **Create a Kubernetes secret for the SSL/TLS certificates.**

	```shell
	$ kubectl create secret tls astronomer-mercury-tls --kubeconfig=/home/schnie/.kube/config --key /home/schnie/dev/letsencrypt/etc/letsencrypt/live/mercury.astronomer.io/privkey.pem --cert /home/schnie/dev/letsencrypt/etc/letsencrypt/live/mercury.astronomer.io/fullchain.pem --namespace astronomer-ee
	```

1. **Generate credentials for Google OAuth.**

	- TODO: CJ

1. **Set the Astronomer config values.**

	Create a `config.yaml` for your domain setting overrides by copying [config.tpl.yaml](https://github.com/astronomerio/helm.astronomer.io/blob/master/config.tpl.yaml) if you don't already have one.

	Change the branch on GitHub to match your desired Astronomer Platform version.

	In `config.yaml`, set the following values:

	```yaml
	global:
	  baseDomain: ...
	  tlsSecret: ...
	```

	[TODO: CJ] Add the oauth clientId and clientSecret

1. **Deploy / Install the Astronomer chart.**

	```shell
	helm install -f config.yaml . --namespace=foo
	```

	Click the link in the output notes to log in to the Astronomer app.
