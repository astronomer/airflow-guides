---
layout: page
title: Monitoring
permalink: /guides/monitoring/
hide: true
---

# Monitoring

<!-- markdownlint-disable MD036 -->
*Note: This feature will be available in the Astronomer EE 0.3 release (July
2018).*
<!-- markdownlint-enable MD036 -->

## Introduction

This document covers the current scope of monitoring features provided by Apache
Airflow and the Astronomer platform.

The monitoring system has three primary concerns:

1. metrics gathering
1. metrics storage
1. visualization

## Components

- StatsD
- StatsD Exporter
- Prometheus
- Grafana

## Getting Started

You might be wondering how monitoring compares in vanilla Airflow vs in the
Astronomer platform.

## Airflow

Airflow is instrumented with **StatsD**, which provides a stats aggregation
daemon.  StatsD is a [push-based monitoring framework][0].  While StatsD support
is built-in to Airflow, the details are not yet well documented.  Specifically,
most of the instrumentation in Airflow today is around the task scheduler.

The Airflow StatsD integration works by sending data to StatsD which is picked
up by the StatsD Exporter.  The **statsd** PyPI package provides the Python
client used in Airflow to gather metrics and push them to the exporter.

The **StatsD Exporter** (`statsd_exporter`) bridges the gap between StatsD and
Prometheus by translating StatsD metrics into Prometheus metrics via configured
mapping rules.

## Astronomer

Astronomer's monitoring picks up on the other side where Prometheus pulls the
data from the StatsD Exporter, which is then made available for visualization in
Grafana.

The **Astronomer Monitoring stack** provides Helm charts for Prometheus and
Grafana as well as custom dashboards for Airflow.  We provide Prometheus and
Grafana as top-level instances independent of Airflow deployments.

**Prometheus** provides a pull-based monitoring framework for apps, services,
hosts, etc.

**Grafana** provides support for dashboards and visualizations built on top of
Prometheus data.

## Customization

As a user, you have full access to Prometheus/Grafana and can customize it to
suit your needs.  You can, for example, create new dashboards, as well as add
new instrumentation metrics to Airflow itself.

## Known Bugs

Note: There is currently a known bug in Airflow where the number of DAGs
reported to Airflow by scheduler subprocesses can be inaccurate -
[AIRFLOW-774][1].

[0]: https://www.robustperception.io/which-kind-of-push-events-or-metrics/
[1]: https://issues.apache.org/jira/browse/AIRFLOW-774
