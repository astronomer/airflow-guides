from airflow.hooks.S3_hook import S3Hook
from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from snowflake_plugin.hooks.snowflake_hook import SnowflakeHook
from airflow.version import version as airflow_version
from airflow.exceptions import AirflowException


class S3ToSnowflakeOperator(BaseOperator):
    template_fields = ('s3_key',)

    base_copy = """
        COPY INTO {snowflake_destination}
        FROM s3://{s3_bucket}/{s3_key} CREDENTIALS=(AWS_KEY_ID='{aws_access_key_id}' AWS_SECRET_KEY='{aws_secret_access_key}')
        FILE_FORMAT=(TYPE='{file_format_name}', skip_header=1)
        FORCE=TRUE
    """

    def __init__(self,
                 s3_bucket,
                 s3_key,
                 database,
                 schema,
                 table,
                 file_format_name,
                 s3_conn_id,
                 snowflake_conn_id,
                 *args, **kwargs):

        super(S3ToSnowflakeOperator, self).__init__(*args, **kwargs)
        self.copy = self.base_copy
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.database = database
        self.schema = schema
        self.table = table
        self.file_format_name = file_format_name or 'JSON'
        self.s3_conn_id = s3_conn_id
        self.snowflake_conn_id = snowflake_conn_id

    def build_copy(self):
        s3_hook = S3Hook(self.s3_conn_id)
        if hasattr(s3_hook, 'get_credentials'):
            a_key, s_key = s3_hook.get_credentials()
        elif hasattr(s3_hook, '_get_credentials'):
            a_key, s_key, _, _ = s3_hook._get_credentials(region_name=None)
        else:
            raise AirflowException('{0} does not support airflow v{1}'.format(
                self.__class__.__name__, airflow_version))

        snowflake_destination = ''

        if self.database:
            snowflake_destination += '{}.'.format(self.database)

        if self.schema:
            snowflake_destination += '{}.'.format(self.schema)

        snowflake_destination += self.table

        fmt_str = {
            'snowflake_destination': snowflake_destination,
            's3_bucket': self.s3_bucket,
            's3_key': self.s3_key,
            'aws_access_key_id': a_key,
            'aws_secret_access_key': s_key,
            'file_format_name': self.file_format_name
        }

        return self.copy.format(**fmt_str)

    def execute(self, context):
        sf_hook = SnowflakeHook(
            snowflake_conn_id=self.snowflake_conn_id).get_conn()
        sql = self.build_copy()
        sf_hook.cursor().execute(sql)
