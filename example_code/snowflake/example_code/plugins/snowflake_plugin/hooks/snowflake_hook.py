from airflow.hooks.base_hook import BaseHook
import snowflake.connector


class SnowflakeHook(BaseHook):
    def __init__(self, snowflake_conn_id='snowflake_default'):
        self.snowflake_conn_id = snowflake_conn_id
        self.snowflake_conn = self.get_connection(snowflake_conn_id)
        self.user = self.snowflake_conn.login
        self.password = self.snowflake_conn.password
        if self.snowflake_conn.extra:
            self.extra_params = self.snowflake_conn.extra_dejson
            self.account = self.extra_params.get('account', None)
            self.region = self.extra_params.get('region', None)
            self.database = self.extra_params.get('database', None)
            self.role = self.extra_params.get('role', None)
            self.schema = self.extra_params.get('schema', None)
            self.warehouse = self.extra_params.get('warehouse', None)

    def get_conn(self):
        return snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            region=self.region,
            database=self.database,
            role=self.role,
            schema=self.schema,
            warehouse=self.warehouse
        )
