
def max(column, table,schema=None,snowflake_conn_id='snowflake_default', default=None):
    """
    Gets the max value for a column.
    :param table: The hive table you are interested in, database and schema are infered from connection unless specified in dot notation
    :type table: string
    :param snowflake_conn_id: The snowflake connection you are interested in.
    :type snowflake_conn_id: string
    :param column: the column to get the max value from.
    :type field: string or list
    >>> max('created_at','accounts')
    '2015-01-01'
    >>> max(['created_at','updated_at'],'accounts')
    '2015-01-01'
    """
    from plugins.snowflake_plugin.hooks.snowflake_hook import SnowflakeHook
    hook = SnowflakeHook(snowflake_conn_id).get_conn()
    cs = hook.cursor()
    cs.execute("USE WAREHOUSE {0}".format(hook.warehouse))
    cs.execute("USE DATABASE {0}".format(hook.database))
    if schema:
        cs.execute("USE SCHEMA {0}".format(schema))
    cs.execute("USE ROLE {0}".format(hook.role))
    columns = column if isinstance(column, list) else [colum]
    columns = list(map(lambda c: "MAX({0})".format(c),columns))
    query ="SELECT GREATEST({0}) FROM {1}".format(','.join(columns),table)
    row = cs.execute(query).fetchone()
    if row is None or row[0] is None:
        return default
    else:
        return row[0]
