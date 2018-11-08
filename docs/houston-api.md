---
title: "The Houston API"
description: "Official documentation for the API that powers Astronomer."
date: 2018-10-12T00:00:00.000Z
slug: "houston-api"
menu: ["root"]
position: [7]
---

Houston is a GraphQL API and serves as the source of truth for the Astronomer Platform.

Once authenticated, you can access the API @ https://houston.astronomer.cloud/playground or at whatever URL your Enterprise installation of Astronomer is installed to.

## Queries

* `authConfig` — Fetch configuration information about available authentication methods ('state' is deprecated)
* `deployments` — Fetches one or more deployments based on input. If a deploymentUuid is return, it will return at most one deployment Fetches all deployments by users UUID if no parameters are specified.
deploymentConfig — Fetches config needed to create a module deployment
* `groups` — Fetch groups by groupUuid or workspaceUuid
* `invites` — Fetch a list of invites
* `self` — Fetches info about the authenticated requesting user
* `workspaces` — Fetch workspace by userUuid or workspaceUuid
* `users` — Fetches a user by username or email
* `serviceAccounts` — Fetch Service Accounts by apiKey, serviceAccountUuid, or entityType and entityUuid

## Mutations

* `confirmEmail` — Confirm email added on signup or from the user profile page
* `createToken` — Verify a User's credentials and issues a token if valid. Adding an orgId validates a User's credentials and access to that Organization, failing if a User does not have access to that Organization
* `createUser` — Creates a new user
* `forgotPassword` — Trigger forgot password processs
* `resendConfirmation` — Confirm email added on signup or from the user profile page
* `resetPassword` — Takes a password reset token and new password, updates password credentials, and authenticates user
* `updateUser` — Update an existing user
* `createDeployment` — Creates a new Airflow deployment
* `updateDeployment` — Updates an existing deployment
* `deleteDeployment` — Deletes an existing deployment
* `migrateDeployment` — Creates a new deployment
* `createWorkspace` — Create a workspace and add authenticated user as owner
* `deleteWorkspace` — Deletes an existing workspace
* `updateWorkspace` — Update an existing workspace
* `workspaceAddUser` — Add user to a workspace
* `workspaceRemoveUser` — Remove user from a workspace
* `createServiceAccount` — Create a Service Account
* `updateServiceAccount` — Update the Label or Category of a Service Account
* `deleteServiceAccount` — Delete a Service Account by it's uuid, will return uuid if successful
* `groupAddUser` — Add user to a group
* `groupRemoveUser` — Remove user from a group
* `createInviteToken` — Invite a user into the platform
* `deleteInviteToken` — Deletes an invitation

## Subscriptions

* `deploymentLogStream` — Streams deployment logs from a start time, at specified interval, optionally scoped to a component
