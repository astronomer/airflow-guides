from airflow.plugins_manager import AirflowPlugin
from plugins.google_analytics_plugin.hooks.google_analytics_hook import GoogleAnalyticsHook
from plugins.google_analytics_plugin.operators.google_analytics_reporting_to_cloud_storage_operator import GoogleAnalyticsReportingToCloudStorageOperator


class GoogleAnalyticsPlugin(AirflowPlugin):
    name = "google_analytics_plugin"
    hooks = [GoogleAnalyticsHook]
    operators = [GoogleAnalyticsReportingToCloudStorageOperator]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
