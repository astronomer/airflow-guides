---
layout: page
title: Deploying DAGs with CI/CD
permalink: /guides/deploying-dags-with-cicd/
hide: true
---

# Deploying DAGS with CI/CD

You can deploy DAGs with continuous integration/continuous
deployment via the Astronomer CLI.

For the most part, you can refer to your own CI/CD tools docs.
There isn't much that is Astronomer specific here, just standard
docker stuff.

While this guide focuses on CircleCI, a similar setup can be
accomplished using Travis CI, Jenkins, Codeship, TeamCity,
GitLab CI/CD, or any other CI/CD system.

For background information and best practices on CI/CD, we
recommend reading the article
[An Introduction to CI/CD Best Practices][0] from DigitalOcean.

1. Install the astronomer platform, using EE docs. One component of
  the installation is a private docker registry. The registry is
  exposed at registry.baseDomain, where baseDomain is the domain
  the user launched the platform at. When new images are pushed
  to this registry, they get deployed to the cluster (this is how
  the CLI works under the hood).

1. Set up a CI/CD pipeline using whatever tool you'd like. Most
  tools will have some sort of documentation on how to trigger the
  pipeline from an event from github, like a new tag/release, or
  push to a branch. In this pipeline, after any tests have been
  executed, you just need to run a few docker commands. A couple
  examples:

    * <https://circleci.com/docs/2.0/building-docker-images/>
    * <https://documentation.codeship.com/pro/builds-and-configuration/image-registries/#custom--self-hosted-registry>

    Images should be tagged with this format
    `registry.baseDomain/<release_name>/airflow:<version>`, and the
    user/password will be generated when the platform is initially
    installed.

NOTE: It's probably best to download the CLI in your CI build as
the registry is currently password protected, and will eventually
have checks if the user has permission to deploy.

```bash
astro auth login -d {domain}
astro airflow deploy {release_name}
```

Where `{domain}` is your base domain, and `{release_name}` is
your kubernetes release name. The CLI will handle the rest.

[0]: https://www.digitalocean.com/community/tutorials/an-introduction-to-ci-cd-best-practices
