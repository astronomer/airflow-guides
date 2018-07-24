# Astronomer Platform Release Guide

The purpose of this guide is to describe the Astronomer Platform release process for platform maintainers.

## 1. Create a `v0.3-stable` branch off of master for each platform component

The [platform component repos](https://github.com/astronomerio/astronomer/tree/master/docker/platform) are:

1. [commander](https://github.com/astronomerio/commander)
1. [db-bootstrapper](https://github.com/astronomerio/db-bootstrapper)
1. [default-backend](https://github.com/astronomerio/default-backend)
1. [houston-api](https://github.com/astronomerio/houston-api)
1. [orbit-ui](https://github.com/astronomerio/orbit-ui)
1. [astronomer](https://github.com/astronomerio/astronomer) (second to last)
1. [helm.astronomer.io](https://github.com/astronomerio/helm.astronomer.io) (last)

## 2. For each repo, create a GitHub Release

- Tag version: `v0.3.0`
- Target: `v0.3-stable` (branch)
- Release title: `v0.3.0`

Creating a release will automatically create the `v0.3.0` tag as well.

## 3. Build and push the Docker images

1. Grab the latest code:

	```shell
	cd astronomer
	git checkout master
	git pull
	```

1. Bump the platform version.

	Adjust the version variables in the Makefile as needed:

	- `ASTRONOMER_MAJOR_VERSION`
	- `ASTRONOMER_MINOR_VERSION`
	- `ASTRONOMER_PATCH_VERSION`
	- `BUILD_NUMBER`

1. Build the Docker images:

	```shell
	make build
	make push
	```

## 5. Publish Helm charts

```shell
cd helm.astronomer.io
make build
make push
```
