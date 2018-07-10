---
title: "Airflow vs. AWS Glue"
description: "How Airflow differs from Amazon's data pipeline orchestration tool, AWS Glue."
date: 2018-05-21T00:00:00.000Z
slug: "airflow-vs-aws-glue"
heroImagePath: null
tags: ["AWS-Glue", "Competition"]
---

You may have come across AWS Glue mentioned as a code-based, server-less ETL alternative to traditional drag-and-drop platforms. While this is all true (and Glue has a number of very exciting advancements over traditional tooling), there is still a very large distinction that should be made when comparing it to Apache Airflow.

##Platform

###Airflow
Airflow is an open-sourced project that (with a few executor options) can be run anywhere in the cloud (e.g. AWS, GCP, Azure, etc). With [Astronomer Enterprise](http://enterprise.astronomer.io/), you can run Airflow on Kubernetes either on-premise or in any cloud.

###AWS Glue
Glue is an AWS product and cannot be implemented on-premise or in any other cloud environment.

##Purpose

###Airflow
Airflow is designed to be an incredibly flexible task scheduler; there really are no limits of how it can be used. Often, it is used to perform ETL jobs (see the ETL section of [Example Airflow Dags](https://github.com/airflow-plugins/Example-Airflow-DAGs), but it can easily be used to [train ML models](https://wecode.wepay.com/posts/training-machine-learning-models-with-airflow-and-bigquery), [check the state of different systems and send notifications via email/slack](https://www.astronomer.io/blog/automating-salesforce-reports-in-slack-with-airflow-3/), and [power features within an app using various APIs](https://robinhood.engineering/why-robinhood-uses-airflow-aed13a9a90c8?gi=e3d130abaf1a).

###Glue
Glue is designed to make the processing of your data as easy as possible ONCE it is the AWS ecosystem. According to AWS Glue documentation:

"AWS Glue natively supports data stored in Amazon Aurora, Amazon RDS for MySQL, Amazon RDS for Oracle, Amazon RDS for PostgreSQL, Amazon RDS for SQL Server, Amazon Redshift, and Amazon S3, as well as MySQL, Oracle, Microsoft SQL Server, and PostgreSQL databases in your Virtual Private Cloud (Amazon VPC) running on Amazon EC2.

AWS Glue provides out-of-the-box integration with Amazon Athena, Amazon EMR, Amazon Redshift Spectrum, and any Apache Hive Metastore-compatible application."

Because of this, it can be advantageous to still use Airflow handle the data pipeline for all things OUTSIDE of AWS (e.g. pulling in records from an API and storing in s3) as this will be not be a capability of AWS Glue itself.

##Underlying Framework

###Airflow
Airflow is an independent framework that executes native Python code without any other dependencies. This can then be extended to use other services, such as [Apache Spark](https://github.com/apache/incubator-airflow/blob/master/airflow/contrib/operators/spark_submit_operator.py), using the library of officially supported and community contributed operators.

###Glue
Glue uses Apache Spark as the foundation for it's ETL logic. There are some notable differences, however, that differentiate it from traditional Spark. The biggest of these differences include the use of a "dynamic frame" vs. the "data frame" (in Spark) that adds a number of additional Glue methods including [ResolveChoice()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-ResolveChoice.html), [ApplyMapping()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-ApplyMapping.html), and [Relationalize()](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-Relationalize.html).

##Execution

###Airflow
Airflow can be executed in a number of fashions; the most common of which is the [CeleryExecutor](https://github.com/apache/incubator-airflow/blob/master/airflow/executors/celery_executor.py). Other [executors](https://github.com/apache/incubator-airflow/tree/master/airflow/executors) are currently available and compatibility with other platforms can be written to extend the framework (such as the [Mesos](https://github.com/apache/incubator-airflow/blob/master/airflow/contrib/executors/mesos_executor.py) or [Kubernetes](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=71013666) Executors).

Airflow on Astronomer (Enterprise) runs on a private Kubernetes cluster and includes resource management tooling and analytics including Prometheus, [Grafana](https://grafana.com/), and [StatsD](https://github.com/etsy/statsd).

###Glue
AWS Glue is notably "server-less", meaning that it requires no specific resources to manage.

##Pricing

###Airflow
While it can be pretty difficult to get up and running alone, Airflow is an open-source project that's completely free to use. If you think you could use some help managing infrastructure or getting Airflow training, check out our [products](https://astronomer.io) and shoot us an email at humans@astronomer.io if you'd like to chat.


###Glue
Pricing on Glue is determined using the derived measure of "Data Processing Units." More information can be found on their [Pricing Page](https://aws.amazon.com/glue/pricing/).