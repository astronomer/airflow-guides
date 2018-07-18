---
layout: page
title: Amazon Web Services Guide
permalink: /guides/aws/
hide: true
---

# Install Astronomer EE on Amazon EKS

For information about getting started with EKS, see the [AWS Getting Started Guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html).

## In this guide we'll cover:

- [Setting up the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/installing.html) (optional)
- [Setting up Kubectl](/guides/kubectl/)
- [Setting up Heptio Authenticator](https://github.com/heptio/authenticator)
- [Setting up Helm and Tiller](/guides/helm/)
- A DNS service. In this guide we use [Route53](https://aws.amazon.com/route53/).
- IAM user creation. It is required that you create your Kubernetes cluster with an elevated IAM user, creating the cluster with root will prevent you from authenticating to your cluster via the CLI.

## Getting started

Make sure you have correctly installed the following tools, and can run a test command for each:

- Helm: `helm version`
  - Output: `Client: &version.Version{SemVer:"v2.9.1", GitCommit:"20adb27c7c5868466912eebdf6664e7390ebe710", GitTreeState:"clean"}`

- AWS CLI: `aws -version`
  - Output: `Client: &version.Version{SemVer:"v2.9.1", GitCommit:"20adb27c7c5868466912eebdf6664e7390ebe710", GitTreeState:"clean"}`

- Kubectl: `kubectl version`
  - Output: `Client Version: version.Info{Major:"1", Minor:"10", GitVersion:"v1.10.3", GitCommit:"2bba0127d85d5a46ab4b778548be28623b32d0b0", GitTreeState:"clean", BuildDate:"2018-05-21T09:17:39Z"`

- Heptio: `heptio-authenticator-aws help`
  - Output: `A tool to authenticate to Kubernetes using AWS IAM credentials...`

- An AWS VPC. You can setup a custom VPC, or use the provided AWS template to get started. See the VPC setup guide in the [EKS Getting Started Docs](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html)

## Create IAM Role

- Admin policy or EKS specific policy + passRole and assumeRole. Make sure to pass the ARM role when creating the cluster, and not the ARN user. Do not uncomment the -r and ARN line from the kube config file (This is optional in the AWS docs but caused authentication issues during our setup process, TRY TO FIND THAT POST ABOUT THE ISSUE SOMEONE ELSE WAS HAVING)
- Following the [AWS Getting Started with Amazon EKS guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html), create your IAM role using the available `EKS Service`.
- You will also need to add the `passRole` and `assumeRole` permissions to this IAM role through a custom policy assigned to your role:

    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": "*"
            }
        ]
    }
    ```

In this example we've assigned these actions to all resources, you may decide to assign these permisions to only the EKS resource, that it fine.

## AWS CLI

If you decided to install the AWS CLI, now is a good time to define your IAM access keys [following this example](https://aws.amazon.com/blogs/security/how-to-use-a-single-iam-user-to-easily-access-all-your-accounts-by-using-the-aws-cli/).

In short, set your default profile configuration details using these commands:

```
aws configure set profile.example.aws_access_key_id <YOUR_AWS_ACCESS_KEY>
aws configure set profile.example.aws_secret_access_key <YOUR_AWS_SECRET_KEY>
aws configure set profile.example.region <YOUR AWS REGION>
```

## Deploy your cluster

With your CLIs setup and your IAM configured you're ready to deploy your EKS cluster.

Deploying a new cluster is easily done through the AWS CLI, or through the console UI.

```
Note: If deploying your cluster through the UI, make sure to do so as the IAM user created above, this will require console access be granted to the IAM user. Creating the cluster through the root login will prohibit you from authenticating against the cluster via the cli in later steps.
```

In terminal run this command to provision a new cluster:

```
aws eks create-cluster --name devel --role-arn arn:aws:iam::111122223333:role/eks-service-role-AWSServiceRoleForAmazonEKS-EXAMPLEBKZRQR --resources-vpc-config subnetIds=subnet-a9189fe2,subnet-50432629,securityGroupIds=sg-f5c54184
```

- Replace `devel` with the name you want to give your new cluster.
- Replace `arn:aws:iam::111122223333:role/eks-service-role-AWSServiceRoleForAmazonEKS-EXAMPLEBKZRQR` with the `Role ARN` identifier under your IAM role summary.
- Replace the `subnetIds` with the subnets created when setting up your VPC. To look these up again you can navigate to the [CloudFormation Serivce](https://console.aws.amazon.com/cloudformation/) select the box next to your VPC stack name and click the `Outputs` tab in the lower half of the screen.
- Replace the `securityGroupIds` with your VPC secuirityGroups value in the outputs tab.

After running this command you may allow up to 10 minutes for the cluster to be fully provisioned.

You can check the status of your cluster by running:

```
aws eks describe-cluster --name <CLUSTER NAME> --query cluster.status
```

Once your cluster is `ACTIVE` you can retrieve the necessary details to configure kubectl to communicate with your cluster using Heptio for authentication.

You will need the cluster endpoint, and certificateAuthority. These can both be access via the UI as well, by navigating to the EKS service and selecting your cluster.

Retrieve your cluster endpoint:

```
aws eks describe-cluster --name <CLUSTER NAME>  --query cluster.endpoint
```

Retrieve your cluster certificate:

```
aws eks describe-cluster --name devel  --query cluster.certificateAuthority.data
```

```
Note: The endpoint and certificate will be returned in double quotations, these are not required when adding them to your kubectl config file.
```

## Configure Kubectl

If this is your first time using Kubectl you will need to create a new config file. If you have an existing kubectl file you can follow the [Kubernetes Guide](https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/) to modify your config file to work with multiple clusters.

To create your own kubectl config file, see the AWS steps [here](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html).

```
Note: It is optional to uncomment the "-r" and "<role-arn>" values when setting up the kubectl config file. During our testing this caused an authentication issue and was better left commented out.
```

With your kubectl config setup and your `KUBECONFIG` path updated, you can query your cluster with:

```
kubectl get svc
```

Your output should look similar to this:

```
NAME             TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
svc/kubernetes   ClusterIP   10.100.0.1   <none>        443/TCP   1m
```

If you receive an authentication error or a message that the cluster does not contain a resource type svc, you may need to double check the Role ARN you're using. Ensure that the cluster was setup using the correct IAM role, that this role has the proper policies assigned and that it is properly configured in your kubectl config file.

## Setup worker nodes

Not that your cluster is provisioned and you've authenticated through the CLI, it's time to create your worker pool. It may be possible to create the worker nodes through the cli similar to the cluster creation, however we will be creating these workers through the console UI.

As with the VPC, Amazon provides a YAML template to quickly create your worker node stack. Set up your worker nodes following the [EKS Worker Nodes](https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html) guide.

Now that your worker nodes are setup and you've configured the `aws-auth-cm.yaml` you can check the status of your nodes using:

```
kubectl get nodes --watch
```

Once your nodes are in the `READY` status you can move on to creating your Tiller user.

## Helm & Tiller

Create the tiller service account and [Install Tiller with Helm](/guides/helm/)

## Deploy Helm charts

Helm and Tiller configured, you can begin deploying your PostgreSQL and Redis databases and the Astronomer EE Helm chart.

We provide example Helm charts for the PostgreSQL and Redis databases [here](/guides/helm/).

## Configure your DNS

If using an existing domain, you can configure the Route53 DNS to route your Astronomer instance requests to the appropriate resources following the [AWS Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/MigratingDNS.html).

<!-- TODO

- Creating SSH key pair
- Automatic kubectl config additions
- Create  VPC template YAML
- Create node stack template YAML

-->
