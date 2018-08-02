from plugins.gcs_prefix_sensor.operators.google_cloud_storage_prefix_sensor import GoogleCloudStoragePrefixSensor

from plugins.gcs_prefix_sensor.hooks.bigquery_hook import BigQueryHook
from airflow.plugins_manager import AirflowPlugin


class GoogleCloudStoragePrefixSensor(AirflowPlugin):
    name = "google_cloud_storage_prefix_sensor"
    hooks = [BigQueryHook]
    operators = [GoogleCloudStoragePrefixSensor]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
