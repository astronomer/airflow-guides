---
title: "Best Practices Calling AWS Lambda from Airflow"
description: "A few tips, guidelines, and best practices for calling Lambda from Airflow"
date: 2018-08-27T00:00:00.000Z
slug: "lambda-cloud"
heroImagePath: null
tags: ["Best Practices", "Integrations"]
---

You might be wanting to trigger an [AWS Lambda](https://goo.gl/zYGM7L) function directly via Airflow. Here are some tidbits of knowledge accumulated at Astronomer that might help you perform that function successfully.

## AWS Lambda Basics

At a high-level, AWS Lambda lets you run code without provisioning or managing servers. You can use AWS Lambda to execute code in response to triggers such as a change in data or a particular user action.

It can be directly triggered by a variety of services, and can be orchestrated into workflows. Naturally, the latter can effectively be done via Apache Airflow.

In general, we'd recommend using a serverless framework such as [Zappa](https://www.zappa.io/) or [Serverless](https://serverless.com/), as there is a surprising amount of boilerplate involved in writing, deploying, updating, and maintaining both serverless functions and an API Gateway.

## Lambda & Airflow

To call an AWS Lambda function in Airflow, you have a few options.

### 1. Invoke Call in Boto3

The simplest way to call the AWS Lambda function in Airflow is to [invoke](https://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.invoke) it in [Boto3](https://aws.amazon.com/sdk-for-python/) as a [PythonOperator](https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator).

The [AwsLambdaHook](https://registry.astronomer.io/providers/amazon/modules/awslambdahook) itself uses the [AwsBaseHook](https://registry.astronomer.io/providers/amazon/modules/awsbasehook), which is a wrapper around the boto3 library (the standard way to interact with AWS via Python). If you add the AWS connections correctly, you can use the hook in one of your self-written operators to trigger a particular Lambda function. 

### 2. Use the SimpleHttpOperator

Another option would be to use the [SimpleHttpOperator](https://registry.astronomer.io/providers/http/modules/simplehttpoperator) in Airflow to hit the Lambda function, much like a REST API.

### 3. Trigger Lambda via an AWS API Gateway

You could also trigger Lambda functions via an [AWS API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/getting-started-with-lambda-integration.html).

In this case, you'd use the `SimpleHttpOperator` as a starting point, but would also have to handle HTTP Authorization.

## Use Cases

In the past, we've seen folks running Lambda in parallel for a token refresh.

Usually, this looks like an ELT structure with GA/Pardot/HubSpot/Marketo to serve a Lambda token and refresh it as soon as it expires.

## Caveats

There are a few caveats to invoking Lambda:

- Execution time is limited (5 min max IIRC)
- It's relatively difficult to debug
- Light security concerns

## Alternatives

If AWS Lambda doesn't fit your needs, you can likely run what you need using the following:

-  [Selenium](https://seleniumhq.github.io/selenium/docs/api/py/)
- Headless Chrome with [pyppeteer](https://github.com/miyakogi/pyppeteer) - (example [here](https://duo.com/decipher/driving-headless-chrome-with-python))

- [Zeit Now](https://zeit.co/blog/serverless-docker) Serverless
Docker Beta - (example [here](https://github.com/zeit/now-examples/tree/master/python-flask>))
