from airflow.hooks.S3_hook import S3Hook
from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from snowflake_plugin.hooks.snowflake_hook import SnowflakeHook
import io
from jinja2 import Template

class SnowflakeOperator(BaseOperator):

    template_fields = ('query',)

    def __init__(self,
                 query,
                 snowflake_conn_id='snowflake_default',
                 role=None,
                 database=None,
                 *args, **kwargs):

        super(SnowflakeOperator, self).__init__(*args, **kwargs)
        self.snowflake_conn_id = snowflake_conn_id
        self.query = query
        self.role = role
        self.database = database

    def execute(self, context):
        hook = SnowflakeHook(snowflake_conn_id=self.snowflake_conn_id).get_conn()
        cs = hook.cursor()
        cs.execute("USE WAREHOUSE {0}".format(hook.warehouse))
        cs.execute("USE DATABASE {0}".format(self.database or hook.database))
        cs.execute("USE ROLE {0}".format(self.role or hook.role))
        if self.query is not None:
            if isinstance(self.query, list):
                query_sequence = self.query
            else:
                query_sequence = [self.query]

            for query in query_sequence:
                cs.execute(query)
