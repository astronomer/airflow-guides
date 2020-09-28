---
title: "Airflow vs. AWS Glue"
description: "How Airflow differs from Amazon's data pipeline orchestration tool, AWS Glue."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-aws-glue"
heroImagePath: null
tags: []
---

>This guide was last updated September 2020

For those whose tooling lives in the Amazon ecosystem, [AWS Glue](https://aws.amazon.com/glue/) is commonly presented and used as a code-based, serverless ETL alternative to traditional drag-and-drop platforms.

Given that Glue has some exciting advancements over traditional tooling, it's commonly pitted against [Apache Airflow](https://airflow.apache.org/) for those looking for a code-based ETL tool with more extensibility. With that said, there are key differences between the two that are worth outlining for anyone evaluating them both. We'll walk you through those differences below.

## Platform

### Airflow

Airflow is an open-source workflow orchestration tool that's entirely cloud-agnostic and offers three distinct execution methods ([Executors](https://www.astronomer.io/guides/airflow-executors-explained/)), each designed for a particular use case.

Airflow can serve as a standard ETL tool but can be stretched well beyond that to accommodate much more complex workflows and dependencies. Given its large community and the vast array of supported use cases, there are dozens of pre-built templates for tools across cloud providers (AWS, GCP, Azure, etc.).

### AWS Glue

AWS Glue is a fully managed ETL service designed to be compatible with other AWS services, and cannot be implemented on-premise or in any other cloud environment.

AWS customers can use Glue to prepare and load their data for analytics. You can use your AWS console to point Glue to your data stored on AWS. Glue will catalog the data and make it available for ETL jobs.  If you have a lot of data stored in AWS, Glue could be a good option for ETL.

## Purpose

### Airflow

Airflow is designed to be a flexible workflow orchestrator with no limits to how it can be used. While ETL is its most common use case, Airflow is also widely used to [train ML models](https://blog.twitter.com/engineering/en_us/topics/insights/2018/ml-workflows.html), [check the state of different systems and send notifications via email/slack](https://www.astronomer.io/blog/automating-salesforce-reports-in-slack-with-airflow-3/), and [power features within an app using various APIs](https://robinhood.engineering/why-robinhood-uses-airflow-aed13a9a90c8?gi=e3d130abaf1a).

### Glue

Glue is designed to make the processing of your data as easy as possible once it is in the AWS ecosystem. According to AWS Glue documentation:

“AWS Glue natively supports data stored in Amazon Aurora, Amazon RDS for MySQL, Amazon RDS for Oracle, Amazon RDS for PostgreSQL, Amazon RDS for SQL Server, Amazon Redshift, DynamoDB and Amazon S3, as well as MySQL, Oracle, Microsoft SQL Server, and PostgreSQL databases in your Virtual Private Cloud (Amazon VPC) running on Amazon EC2. AWS Glue also supports data streams from Amazon MSK, Amazon Kinesis Data Streams, and Apache Kafka.”

Precisely because of Glue's dependency on the AWS ecosystem, dozens of users choose to leverage both by using Airflow to handle data pipelines that interact with data outside of AWS (e.g. pulling records from an API and storing it in S3), as AWS Glue isn't able to handle those jobs.

## Underlying Framework

### Airflow

Airflow is an independent framework that executes native Python code without any other dependencies. This can then be extended to use other services, such as [Apache Spark](https://github.com/apache/incubator-airflow/blob/master/airflow/contrib/operators/spark_submit_operator.py), using the library of officially supported and community contributed operators. Flexible interaction with third-party APIs, databases, infrastructure layers, and data systems (including AWS) is made possible through these operators.  

### Glue

Glue uses Apache Spark as the foundation for its ETL logic. There are some notable differences, however, that differentiate it from vanilla Spark. The biggest of these differences include the use of a "dynamic frame" vs. the "data frame" in Spark that adds a number of additional Glue methods including [ResolveChoice()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-ResolveChoice.html), [ApplyMapping()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-ApplyMapping.html), and [Relationalize()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-Relationalize.html). By contract, Glue ETL scripts can be written in either PySpark or Scala.

## Execution

### Airflow



One of Airflow's biggest strengths is its built-in choice between three [executors](https://github.com/apache/incubator-airflow/tree/master/airflow/executors), each built to execute tasks for a distinct use case. These executors allow Airflow to consume resources in a way that's optimized to the needs of your workflows and extends its framework to support serverless task execution via the [Kubernetes Executor](https://airflow.apache.org/docs/stable/executor/kubernetes.html), for example.

### Glue

AWS Glue is notably serverless by default and does not require the user to decide how to allocate resources at any given time.

Glue uses [crawlers](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html) to crawl through your AWS data stores(S3, DynamoDB, etc…) and populate the AWS Glue Data Catalog by looking for a particular data schema. ETL jobs are run from this Data Catalog and Glue uses this catalog as a data source for jobs. For the crawlers to work correctly, data often needs to be in a particular format. Given that limitation, it's common to leverage Apache Airflow to organize or transform data as needed so Glue can efficiently crawl it.

## Pricing

### Airflow

Airflow's status as a widely used open-source project makes it free to use as long as you're willing to manage your Airflow Deployment's resources. If you'd like help managing infrastructure at scale or are interested in Airflow training, [send us a note](https://astronomer.io/contact), and we'd be happy to give you a tour of our product features.

Airflow is an open-source project that's completely free to use if you’d like to spin it up and maintain the deployment. If you would like some help managing infrastructure,  efficiently scaling Airflow, or getting Airflow training, [send us a note](https://astronomer.io/contact) and we’d be happy to give you a tour of our product features.

### Glue

Pricing on Glue is determined using the derived measure of "Data Processing Units." More information can be found on their [Pricing Page](https://aws.amazon.com/glue/pricing/).

## Conclusion

AWS Glue is designed specifically to run ETL processes within the AWS ecosystem. Airflow is an open-source workflow orchestrator and scheduler that is designed to be flexible and work with any data platform, API, or data store. Those running ETL processes in AWS may still need Airflow to organize data for Glue to process or manage data processes outside of AWS. 