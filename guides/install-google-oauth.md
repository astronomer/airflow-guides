---
title: "Getting Create Google OAuth Creds"
description: "How to create Google OAuth Creds for Enterprise installs"
date: 2018-07-18T00:00:00.000Z
slug: "install-google-oauth"
heroImagePath: null
tags: ["Astronomer EE", "Install", "OAuth"]
---

As of Astronomer v0.3, it uses Google OAuth to authenticate users. In order to get this setup you will need to create credentials to securely communicate with Google services

> Note: We're also adding support for Auth0 very soon as an alternative OAuth provider to simplify installation.

## Create OAuth Credentials

### Prerequisites:

- A Google Account for accessing the GCP console
- Know the `baseDomain` you are installing Astronomer EE to.  (ie. astro.yourdomain.com)

### Step 1: Navigate to Google Cloud Platform

Visit the Google [cloud console](https://console.cloud.google.com/)

### Step 2: Create a project

If you already have an existing project you want to use, you can skip to Step 3

In the top nav, you will have a dropdown with a label of either a currently selected project or `Select a project`.  

![select-project](https://cdn.astronomer.io/website/img/guides/google-oauth-creds/select-project.png)

Click this dropdown, which will open a project selection window.  In this window, click the `Create project` button in the top right.

This will direct you to a page to create a new project.  Fill in the `Project Name` field and click `Create`

![create-project](https://cdn.astronomer.io/website/img/guides/google-oauth-creds/create-project.png)

Now you should have a new project and it should automatically be selected as your active project.

### Step 3: Navigate to Credentials page

In the main menu, hover over the `APIs & Services` item, and click on the sub-menu item of `Credentials`.

### Step 4: Update "OAuth consent screen"

On the `Credentials` page there will be three tabs.  Click the center tab `OAuth consent screen`.  In this form, fill out the `Product name shown to users` field.  The value doesn't matter, but it must be set to create credentials.

![update-consent](https://cdn.astronomer.io/website/img/guides/google-oauth-creds/update-consent.png)

Hit save in the bottom left of the form, and you should be ready to create your credentials

### Step 5: Create "OAuth client ID"

On the `Credentials` page, click the left tab labeled `Credentials`.  Down the page will be a button labeled `Create credentials`.  Click this, which will open a dropdown.  Hit the option labeled `OAuth client ID`

![create-creds](https://cdn.astronomer.io/website/img/guides/google-oauth-creds/create-creds.png)

### Step 6: Create the OAuth credentials

You'll need to fill out some information to create the credentials. The important fields are outlined below:

#### Application type

Select `Web application`

#### Name

Enter any name you want to give the credentials.  This is just a label for the Google console to use.

#### Authorization redirect URIs

You need to whitelist the page in our Orbit UI your users will be redirected to after authenticating.  This value should be: `https://app.[baseDomain]/oauth/google`.

So for instance, if your `baseDomain` is `astro.yourdomain.com`, the value should be `https://app.astro.yourdomain.com/oauth/google`.

Once these fields have been filled out, click the `Create` button in the bottom left of the form.

### Step 7: Copy your "clientID" and "clientSecret"

After creating your credentials, Google will redirect you back to the credentials page and popup a window with your newly created OAuth client credentials.  

![copy-client-id-secret](https://cdn.astronomer.io/website/img/guides/google-oauth-creds/copy-client-id-secret.png)

If you accidentally close this, or need to refer to them at a later date, clicking the name of the credentials you just created in the list of credentials on this page will display them.

You'll want to copy the clientID and clientSecret into the helm config file you are prepping for the Astronomer Helm install.  

That's it!
