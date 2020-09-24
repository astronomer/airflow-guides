---
title: "Airflow vs. AWS Glue"
description: "How Airflow differs from Amazon's data pipeline orchestration tool, AWS Glue."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-aws-glue"
heroImagePath: null
tags: []
---

>This guide was last updated September 2020

You may have come across [AWS Glue](https://aws.amazon.com/glue/) mentioned as a code-based, serverless ETL alternative to traditional drag-and-drop platforms. While Glue has some exciting advancements over traditional tooling, it is a very different tool than [Apache Airflow](https://airflow.apache.org/). Here we will outline the differences between the tools in several different factors

## Platform

### Airflow

Airflow is an open-source project (with a few [executor options](https://www.astronomer.io/guides/airflow-executors-explained/)) that can be run anywhere in the cloud (e.g. AWS, GCP, Azure, etc)

### AWS Glue

AWS Glue is a fully managed ETL service designed to be compatible with other AWS services, and cannot be implemented on-premise or in any other cloud environment .

## Purpose

### Airflow

Airflow is designed to be a flexible workflow orchestrator; there really are no limits to how it can be used. Often, it is used to perform ETL jobs, but it can easily be used to [train ML models](https://blog.twitter.com/engineering/en_us/topics/insights/2018/ml-workflows.html), [check the state of different systems and send notifications via email/slack](https://www.astronomer.io/blog/automating-salesforce-reports-in-slack-with-airflow-3/), and [power features within an app using various APIs](https://robinhood.engineering/why-robinhood-uses-airflow-aed13a9a90c8?gi=e3d130abaf1a).

### Glue

Glue is designed to make the processing of your data as easy as possible once it is in the AWS ecosystem. According to AWS Glue documentation:

“AWS Glue natively supports data stored in Amazon Aurora, Amazon RDS for MySQL, Amazon RDS for Oracle, Amazon RDS for PostgreSQL, Amazon RDS for SQL Server, Amazon Redshift, DynamoDB and Amazon S3, as well as MySQL, Oracle, Microsoft SQL Server, and PostgreSQL databases in your Virtual Private Cloud (Amazon VPC) running on Amazon EC2. AWS Glue also supports data streams from Amazon MSK, Amazon Kinesis Data Streams, and Apache Kafka.”

Because of this, it can be advantageous to still use Airflow to handle the data pipeline for all things OUTSIDE of AWS (e.g. pulling in records from an API and storing in s3) as this is not be a capability of AWS Glue.

## Underlying Framework

### Airflow

Airflow is an independent framework that executes native Python code without any other dependencies. This can then be extended to use other services, such as [Apache Spark](https://github.com/apache/incubator-airflow/blob/master/airflow/contrib/operators/spark_submit_operator.py), using the library of officially supported and community contributed operators. Flexible interaction with third-party APIs, databases, infrastructure layers, and data systems (including AWS) is made possible through these operators.  

### Glue

Glue uses Apache Spark as the foundation for it's ETL logic. There are some notable differences, however, that differentiate it from traditional Spark. The biggest of these differences include the use of a "dynamic frame" vs. the "data frame" (in Spark) that adds a number of additional Glue methods including [ResolveChoice()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-ResolveChoice.html), [ApplyMapping()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-ApplyMapping.html), and [Relationalize()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-Relationalize.html). Glue ETL scripts can be written in either PySpark or Scala.

## Execution

### Airflow

Airflow can use a number of different [executors](https://github.com/apache/incubator-airflow/tree/master/airflow/executors) to run tasks. These executors allow Airflow to use resources flexibly in response to the needs of your workflow. This extends Airflow’s framework to be used for many different use cases, including serverless task execution via the [Kubernetes Executor](https://airflow.apache.org/docs/stable/executor/kubernetes.html).

### Glue

AWS Glue is notably serverless, meaning that it requires no specific resources to manage.

Glue uses [crawlers](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html) to crawl through your AWS data stores(S3, DynamoDB, etc…) and populate the AWS Glue Data Catalog by looking for a particular data schema. ETL jobs are run from this Data Catalog and Glue uses this catalog as a data source for jobs. For the crawlers to work correctly the data may need to be in a specific format. Airflow could be used to organize your data to be efficiently crawled by Glue.

## Pricing

### Airflow

 Airflow is an open-source project that's completely free to use if you’d like to spin it up and maintain the deployment. If you would like some help managing infrastructure,  efficiently scaling Airflow, or getting Airflow training, [send us a note](https://astronomer.io/contact) and we’d be happy to give you a tour of our product features.

### Glue

Pricing on Glue is determined using the derived measure of "Data Processing Units." More information can be found on their [Pricing Page](https://aws.amazon.com/glue/pricing/).

## Conclusion

AWS Glue is designed specifically to run ETL processes within the AWS ecosystem. Airflow is an open-source workflow orchestrator and scheduler that is designed to be flexible and work with any data platform, API, or data store. Those running ETL processes in AWS may still need Airflow to organize data for Glue to process or manage data processes outside of AWS. 