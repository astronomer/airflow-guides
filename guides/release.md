# Astronomer Platform Release Guide

The purpose of this guide is to describe the Astronomer Platform release process for platform maintainers.

1. **Create a `v0.3.0` branch off of master for each [platform component repos](https://github.com/astronomerio/astronomer/tree/master/docker/platform).**

	1. [commander](https://github.com/astronomerio/commander)
	1. [db-bootstrapper](https://github.com/astronomerio/db-bootstrapper)
	1. [default-backend](https://github.com/astronomerio/default-backend)
	1. [houston-api](https://github.com/astronomerio/houston-api)
	1. [orbit-ui](https://github.com/astronomerio/orbit-ui)
	1. [astronomer](https://github.com/astronomerio/astronomer) (second to last)
	1. [helm.astronomer.io](https://github.com/astronomerio/helm.astronomer.io) (last)

1. **For each repo above, create a release on GitHub.**

	- Tag version: `v0.3.0`
	- Target: `v0.3.0` (branch)
	- Release title: `v0.3.0`

	Creating a release will automatically create the `v0.3.0` tag as well.

1. **Build and push Docker images.**

	TODO

	```shell
	git clone ...
	... code changes? ...
	make build
	make push
	```

1. **Publish Helm charts.**

	TODO
