---
title: Astronomer Operators
sidebar: platform_sidebar
---

For a complete list of Airflow Hooks, Operators, and Utilities maintained by Astronomer, check out our [Airflow Plugins](https://github.com/airflow-plugins?utf8=%E2%9C%93&q=&type=&language=) organization on Github.

## MongoDB to S3

~~~ python
import json
from bson import json_util

from airflow.models import BaseOperator
from airflow.hooks.S3_hook import S3Hook
from ..hooks.MongoHook import MongoHook


class MongoToS3BaseOperator(BaseOperator):
    """
    Mongo -> S3
	A more specific baseOperator meant to move data from mongo via pymongo to s3 via boto
	things to note
		.execute() is written to depend on .transform()
		.transform() is meant to be extended by child classes to perform transformations unique
		    to those operators needs
    """

    template_fields = ['s3_key', 'mongo_query']

    def __init__(self,
                 mongo_conn_id,
                 s3_conn_id,
                 mongo_collection,
                 mongo_database,
                 mongo_query,
                 s3_bucket,
                 s3_key,
                 *args, **kwargs):
        super(MongoToS3BaseOperator, self).__init__(*args, **kwargs)
        # Conn Ids
        self.mongo_conn_id = mongo_conn_id
        self.s3_conn_id = s3_conn_id
        # Mongo Query Settings
        self.mongo_db = mongo_database
        self.mongo_collection = mongo_collection
        # Grab query and determine if we need to run an aggregate pipeline
        self.mongo_query = mongo_query
        self.is_pipeline = True if isinstance(self.mongo_query, list) else False

        # S3 Settings
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key

        # KWARGS
        self.replace = kwargs.pop('replace', False)

    def execute(self, context):
        """
        Executed by task_instance at runtime
        """
        mongo_conn = MongoHook(self.mongo_conn_id).get_conn()
        s3_conn = S3Hook(self.s3_conn_id)

        # Grab collection and execute query according to whether or not it is a pipeline
        collection = mongo_conn.get_database(self.mongo_db).get_collection(self.mongo_collection)
        results = collection.aggregate(self.mongo_query) if self.is_pipeline else collection.find(self.mongo_query)

        # Performs transform then stringifies the docs results into json format
        docs_str = self._stringify(self.transform(results))

        #if len(docs_str) > 0:
        s3_conn.load_string(docs_str, self.s3_key, bucket_name=self.s3_bucket, replace=self.replace)

        return {'rendered_templates': {'mongo_query': self.mongo_query, 's3_key': self.s3_key}}

    def _stringify(self, iter, joinable='\n'):
        """
        Takes an interable (pymongo Cursor or Array) containing dictionaries and
        returns a stringified version using python join
        """
        return joinable.join([json.dumps(doc, default=json_util.default) for doc in iter])

    def transform(self, docs):
        """
        Processes pyMongo cursor and returns single array with each element being
                a JSON serializable dictionary
        MongoToS3BaseOperator.transform() assumes no processing is needed
        ie. docs is a pyMongo cursor of documents and cursor just needs to be
            converted into an array.
        """
        return [doc for doc in docs]
~~~

_[Source](https://github.com/astronomerio/example-pipelines/blob/master/plugins/MongoToRedshiftPlugin/operators/MongoToS3Operator.py)_

## Salesforce to S3

~~~ python
from airflow.contrib.hooks.salesforce_hook import SalesforceHook
from airflow.hooks.S3_hook import S3Hook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging
from tempfile import NamedTemporaryFile


class SalesforceToS3Operator(BaseOperator):
    """
    Make a query against Salesforce and write the resulting data to s3.
    NOTE: The basis of this operator comes from a Salesforce operator written
    by Giovanni Briggs -- It can be found here:
    https://github.com/Jalepeno112/airflow-salesforce
    """
    template_fields = ("query", )

    @apply_defaults
    def __init__(
        self,
        sf_conn_id,
        obj,
        output,
        s3_conn_id,
        s3_bucket,
        fields=None,
        fmt="csv",
        query=None,
        relationship_object=None,
        record_time_added=False,
        coerce_to_timestamp=False,
        *args,
        **kwargs
    ):
        """
        Initialize the operator
        :param conn_id:             name of the Airflow connection that has
                                    your Salesforce username, password and
                                    security_token
        :param obj:                 name of the Salesforce object we are
                                    fetching data from
        :param output:              name of the file where the results
                                    should be saved
        :param fields:              *(optional)* list of fields that you want
                                    to get from the object.
                                    If *None*, then this will get all fields
                                    for the object
        :param fmt:                 *(optional)* format that the output of the
                                    data should be in.
                                    *Default: CSV*
        :param query:               *(optional)* A specific query to run for
                                    the given object.  This will override
                                    default query creation.
                                    *Default: None*
        :param relationship_object: *(optional)* Some queries require
                                    relationship objects to work, and
                                    these are not the same names as
                                    the SF object.  Specify that
                                    relationship object here.
                                    *Default: None*
        :param record_time_added:   *(optional)* True if you want to add a
                                    Unix timestamp field to the resulting data
                                    that marks when the data was
                                    fetched from Salesforce.
                                    *Default: False*.
        :param coerce_to_timestamp: *(optional)* True if you want to convert
                                    all fields with dates and datetimes
                                    into Unix timestamp (UTC).
                                    *Default: False*.
        """

        super(SalesforceToS3Operator, self).__init__(*args, **kwargs)

        self.sf_conn_id = sf_conn_id
        self.output = output
        self.s3_conn_id = s3_conn_id
        self.s3_bucket = s3_bucket
        self.object = obj
        self.fields = fields
        self.fmt = fmt.lower()
        self.query = query
        self.relationship_object = relationship_object
        self.record_time_added = record_time_added
        self.coerce_to_timestamp = coerce_to_timestamp

    def special_query(self, query, sf_hook, relationship_object=None):
        if not query:
            raise ValueError("Query is None.  Cannot query nothing")

        sf_hook.sign_in()

        results = sf_hook.make_query(query)
        if relationship_object:
            records = []
            for r in results['records']:
                if r.get(relationship_object, None):
                    records.extend(r[relationship_object]['records'])
            results['records'] = records

        return results

    def execute(self, context):
        """
        Execute the operator.
        This will get all the data for a particular Salesforce model
        and write it to a file.
        """
        logging.info("Prepping to gather data from Salesforce")

        # open a name temporary file to
        # store output file until S3 upload
        with NamedTemporaryFile("w") as tmp:

            # load the SalesforceHook
            # this is what has all the logic for
            # connecting and getting data from Salesforce
            hook = SalesforceHook(
                conn_id=self.sf_conn_id,
                output=tmp.name
            )

            # attempt to login to Salesforce
            # if this process fails, it will raise an error and die right here
            # we could wrap it
            hook.sign_in()

            # get object from Salesforce
            # if fields were not defined,
            # then we assume that the user wants to get all of them
            if not self.fields:
                self.fields = hook.get_available_fields(self.object)

            logging.info(
                "Making request for"
                "{0} fields from {1}".format(len(self.fields), self.object)
            )

            if self.query:
                query = self.special_query(
                    self.query,
                    hook,
                    relationship_object=self.relationship_object
                )
            else:
                query = hook.get_object_from_salesforce(self.object,
                                                        self.fields)

            # output the records from the query to a file
            # the list of records is stored under the "records" key
            logging.info("Writing query results to: {0}".format(tmp.name))
            hook.write_object_to_file(
                query['records'],
                filename=tmp.name,
                fmt=self.fmt,
                coerce_to_timestamp=self.coerce_to_timestamp,
                record_time_added=self.record_time_added
            )

            # flush the temp file
            # upload temp file to S3
            tmp.flush()
            dest_s3 = S3Hook(s3_conn_id=self.s3_conn_id)
            dest_s3.load_file(
                filename=tmp.name,
                key=self.output,
                bucket_name=self.s3_bucket,
                replace=True
            )
            dest_s3.connection.close()
            tmp.close()
        logging.info("Query finished!")
~~~

_[Source](https://github.com/astronomerio/example-pipelines/tree/master/plugins/SalesforceToS3Plugin)_

