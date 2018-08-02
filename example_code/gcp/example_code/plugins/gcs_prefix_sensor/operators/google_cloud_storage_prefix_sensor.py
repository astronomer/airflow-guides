from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults


class GoogleCloudStoragePrefixSensor(BaseSensorOperator):
    """
    Checks for the existence of a files at prefix in Google Cloud Storage bucket.
    Create a new GoogleCloudStorageObjectSensor.
        :param bucket: The Google cloud storage bucket where the object is.
        :type bucket: string
        :param prefix: The name of the prefix to check in the Google cloud
            storage bucket.
        :type prefix: string
        :param google_cloud_storage_conn_id: The connection ID to use when
            connecting to Google cloud storage.
        :type google_cloud_storage_conn_id: string
        :param delegate_to: The account to impersonate, if any.
            For this to work, the service account making the request must have
            domain-wide delegation enabled.
        :type delegate_to: string
    """
    template_fields = ('bucket', 'prefix')
    ui_color = '#f0eee4'

    @apply_defaults
    def __init__(self,
                 bucket,
                 prefix,
                 google_cloud_conn_id='google_cloud_default',
                 delegate_to=None,
                 *args, **kwargs):
        super(GoogleCloudStoragePrefixSensor, self).__init__(*args, **kwargs)
        self.bucket = bucket
        self.prefix = prefix
        self.google_cloud_conn_id = google_cloud_conn_id
        self.delegate_to = delegate_to

    def poke(self, context):
        self.log.info('Sensor checks existence of objects: %s, %s',
                      self.bucket, self.prefix)
        hook = GoogleCloudStorageHook(
            google_cloud_storage_conn_id=self.google_cloud_conn_id,
            delegate_to=self.delegate_to)
        return bool(hook.list(self.bucket, prefix=self.prefix))
