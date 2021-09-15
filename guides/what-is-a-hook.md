---
title: "Hooks 101"
description: "An introduction to Hooks in Apache Airflow."
date: 2018-05-21T00:00:00.000Z
slug: "what-is-a-hook"
heroImagePath: "https://assets.astronomer.io/website/img/guides/IntroToDAG_preview.png"
tags: ["Hooks", "Operators", "Tasks", "Basics"]
---

## Hooks

Operators are the main building blocks of Airflow, but operators rely heavily upon Hooks to interact with all of their source and destination systems.

Hooks are used as a way to abstract the methods you would use against a source system, but often contain limited logic for how that system is interacted with. Hooks should always be used to connect with any external system.

The [S3Hook](https://registry.astronomer.io/providers/amazon/modules/s3hook) below just shows how a hook can import a standard library (in this case, boto3) and expose some of the most common methods.

The full code for the hook is [here](https://github.com/apache/airflow/blob/main/airflow/providers/amazon/aws/hooks/s3.py)

> To browse and search all of the available Hooks in Airflow, visit the [Astronomer Registry](https://registry.astronomer.io/modules?types=hooks), the discovery and distribution hub for Apache Airflow integrations created to aggregate and curate the best bits of the ecosystem.

```python
class S3Hook(AwsHook):
    """
    Interact with AWS S3, using the boto3 library.
    """

    def get_conn(self):
        return self.get_client_type('s3')

    @staticmethod
    def parse_s3_url(s3url):        
            return bucket_name, key

    def check_for_bucket(self, bucket_name):        
            return False

    def get_bucket(self, bucket_name):        
        return s3.Bucket(bucket_name)

    def create_bucket(self, bucket_name, region_name=None):
        return None

    def check_for_prefix(self, bucket_name, prefix, delimiter):        
        return False if plist is None else prefix in plist

    def list_prefixes(self, bucket_name, prefix='', delimiter='', page_size=None, max_items=None):        
            return prefixes

    def list_keys(self, bucket_name, prefix='', delimiter='', page_size=None, max_items=None):
            return keys

    def check_for_key(self, key, bucket_name=None):
        return obj

    def read_key(self, key, bucket_name=None):
        return obj.get()['Body'].read().decode('utf-8')

    def select_key(self, key, bucket_name=None,
                   expression='SELECT * FROM S3Object',
                   expression_type='SQL',
                   input_serialization=None,
                   output_serialization=None):
        return ''.join(event['Records']['Payload'].decode('utf-8')
                       for event in response['Payload']
                       if 'Records' in event)

    def load_file(self, filename, key, bucket_name=None, replace=False, encrypt=False):
        return None

    def load_string(self, string_data, key, bucket_name=None, replace=False, encrypt=False,
                    encoding='utf-8'):
        return None

    def load_bytes(self, bytes_data, key, bucket_name=None, replace=False, encrypt=False):
      return None

    def load_file_obj(self, file_obj, key, bucket_name=None, replace=False, encrypt=False):
      return None

    def copy_object(self, source_bucket_key, dest_bucket_key, source_bucket_name=None, dest_bucket_name=None, source_version_id=None):
        return response

    def delete_objects(self, bucket, keys):
        return response
```

 This Hook inherits from the [AwsBaseHook](https://registry.astronomer.io/providers/amazon/modules/awsbasehook) which inherits from the [BaseHook](https://registry.astronomer.io/providers/apache-airflow/modules/basehook). All Hooks inherit from the `BaseHook` which contains the logic for how hooks interact with `Airflow Connections`. `Connections`  are Airflow's built in credential-store for your source/destination systems. Hooks are designed to handle these in a clean, reusable way. Tasks that use a hook will have an input parameter for the `conn_id` of the connection you wish to use.

 **Hooks provide an interface in which to interact with an external system, but do not contain the logic for how that system is interacted with.** (in this example, boto3 holds the logic on how to interact with S3)

### These are the hooks that come with airflow

- `https://github.com/apache/airflow/tree/master/airflow/hooks`
- `https://github.com/apache/airflow/tree/master/airflow/contrib/hooks`

Of course, you can write hooks to interact with any system you want!
