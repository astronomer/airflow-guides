# Astronomer Platform Release Guide

The purpose of this guide is to describe the Astronomer Platform release process for platform maintainers.

In the examples below, the desired version is `v0.3.0`.  Replace this anywhere with the version you're releasing.

## 1. Create a `v0.3-stable` branch off of master for each platform component

The [platform component repos](https://github.com/astronomerio/astronomer/tree/master/docker/platform) are:

1. [commander](https://github.com/astronomerio/commander)
1. [db-bootstrapper](https://github.com/astronomerio/db-bootstrapper)
1. [default-backend](https://github.com/astronomerio/default-backend)
1. [houston-api](https://github.com/astronomerio/houston-api)
1. [orbit-ui](https://github.com/astronomerio/orbit-ui)
1. [astronomer](https://github.com/astronomerio/astronomer) (second to last)
1. [helm.astronomer.io](https://github.com/astronomerio/helm.astronomer.io) (last)

## 2. Update `ARG VERSION` tag in each platform component Dockerfile

- https://github.com/astronomerio/astronomer/blob/master/docker/platform/commander/Dockerfile
- https://github.com/astronomerio/astronomer/blob/master/docker/platform/db-bootstrapper/Dockerfile
- https://github.com/astronomerio/astronomer/blob/master/docker/platform/default-backend/Dockerfile
- https://github.com/astronomerio/astronomer/blob/master/docker/platform/houston-api/Dockerfile
- https://github.com/astronomerio/astronomer/blob/master/docker/platform/orbit-ui/Dockerfile

Note: Keep [airflow](https://github.com/astronomerio/astronomer/blob/master/docker/platform/airflow/Dockerfile) pinned to the Airflow version string.

## 3. Create a GitHub Release for each platform component repo

- Tag version: `v0.3.0`
- Target: `v0.3-stable` (branch)
- Release title: `v0.3.0`

Creating a release will automatically create the `v0.3.0` tag as well.

\*Note: Wait to tag the `astronomer` and `helm.astronomer.io` repos until the last step of this guide.

## 4. Build and push the Docker images

1. Grab the latest code

	```shell
	cd astronomer
	git checkout master
	git pull
	```

1. Bump the platform version

	Adjust the version variables in the astronomer Makefile as needed:

	- `ASTRONOMER_MAJOR_VERSION`
	- `ASTRONOMER_MINOR_VERSION`
	- `ASTRONOMER_PATCH_VERSION`
	- `BUILD_NUMBER`

1. Build the Docker images

	```shell
	make build
	make push
	```

## 5. Bump `images.*.tag` values in `values.yaml` for each subchart

1. Grab the latest code

	```shell
	cd helm.astronomer.io
	git checkout master
	git pull
	```

1. Bump tags in subcharts:

	- https://github.com/astronomerio/helm.astronomer.io/blob/master/charts/airflow/values.yaml
	- https://github.com/astronomerio/helm.astronomer.io/blob/master/charts/astronomer/values.yaml
	- https://github.com/astronomerio/helm.astronomer.io/blob/master/charts/grafana/values.yaml
	- https://github.com/astronomerio/helm.astronomer.io/blob/master/charts/nginx/values.yaml
	- https://github.com/astronomerio/helm.astronomer.io/blob/master/charts/prometheus/values.yaml

TODO: do we need to change versions in [requirements.yaml](https://github.com/astronomerio/helm.astronomer.io/blob/master/requirements.yaml) too?

1. Bump the platform version

	Adjust the version variables in the helm.astronomer.io Makefile as needed:

	- `ASTRONOMER_MAJOR_VERSION`
	- `ASTRONOMER_MINOR_VERSION`
	- `ASTRONOMER_PATCH_VERSION`
	- `ASTRONOMER_RC_VERSION` (optional)

## 6. Build and publish the Helm charts

```shell
cd helm.astronomer.io
make build
make push
```

## 7. Create GitHub Releases for the platform itself

Create tags/releases for `astronomer` and `helm.astronomer.io`.

- Tag version: `v0.3.0`
- Target: `v0.3-stable` (branch)
- Release title: `v0.3.0`
