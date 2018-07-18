---
layout: page
title: Google Cloud DNS
permalink: /guides/google-cloud-dns/
hide: true
---

# Cloud DNS

Enabling the Google Cloud DNS

Enabling the Google Cloud DNS is pretty straight forward, however, we ran into some issues that we'll help troubleshoot below.

When first attempting to enable the Cloud DNS via the Google Cloud Console, we came accross a persistent 'Enabling API...' message which never resolved and we were left waiting on the page endlessly. 

### Option 1
Start by logging into and selecting your google cloud project. From the top left hamburger menu scroll down to 'Network Services' and click on 'Cloud DNS'. Click 'Enable API'

If this worked, congratulations, you came move on to next steps.

If that didn't work we'll try this next.

### Option 2
From the top left hamburger menu select 'APIs & Services' then click on 'Library'. In the search field type 'Cloud DNS'. Select the cloud dns card and click to enable the API. Cross your fingers.

If this worked you can move on to next steps.

If neither of those options worked, we can move on to the final solution which worked for us. 

### Option 3
API services can be enabled through the Gcloud SDK. 

From your terminal, start by listing your current cloud projects
```
gcloud projects list
```

Now set your default project
```
gcloud config set project [YOUR_PROJECT_ID]
```

Now list the services available to your project
```
gcloud services list --available
```

Find the Cloud DNS service on the list and note the service name
```
gcloud services enable [SERVICE_NAME]
```

In our case the command would look like this
```
gcloud services enable dns.googleapis.com
```

In our case, we received an asychronise responce that the service was being enabled, however this message never fully resolved. Checking in our GCP UI however, we now see that the Cloud DNS API has been enabled.


## Creating A name records

With the Clound DNS service enabled, we need to add our A name record for our subdomains to point them at our load balancer. 

Start by creating a new DNS zone, name this some cool.Leave DNSSEC off and enter your domain name.

With your zone created, we can now create our wildcard A name record. Grab your static IP address which is currently in use by the load balancer setup through the Astronomer EE installation via Helm.

Click 'Add record set' and in DNS Name enter an asterisk to route any inbound traffice for our domain to this load balancer IP.

Enter your load balancer IP and click 'Create'

You can monitor the DNS propogation from a DNS loookup site such as [DNS Checker](https://dnschecker.org/)

Or by using nslookup in your terminal window as
```
nslookup airflow.[SUB-DOMAIN]
```

Verify that the IP address response matches your static IP address in use by the load balancer. 


### Updating Domain Name Service

Now that our DNS is routing traffic to our load balancer, we need to point our domain to the DNS records.
In this example we obtained our domain through Google's Domain service which is in Beta at the time of writting this guide.

From the 'Configre DNS' section of our [Domain manager portal](https://domains.google.com/) we need to select to use our customer domain servers. 

Note: You will see a warning that all domain services are disabled when using custom name servers, this is fine.

From the Cloud DNS service page in your GCP, copy all of the NS records over to your domain records. Your domain will now direct all requests to Cloud DNS, which will route requests to your load blanacer.




