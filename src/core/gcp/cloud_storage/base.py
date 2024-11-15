import base64
import json
import logging
import tempfile
from typing import Any

from google.cloud import storage
from google.oauth2 import service_account

from src.settings.base import settings

logger = logging.getLogger(__name__)


class GCPCloudStorage:
    def __init__(self):
        string_credentials = settings.GCP_CREDENTIALS_BASE64.replace('"', "")
        logger.info(f"GCP Credentials: {string_credentials}")
        gcp_json_credentials_dict = json.loads(
            base64.b64decode(string_credentials).decode("utf-8")
        )
        credentials = service_account.Credentials.from_service_account_info(
            gcp_json_credentials_dict
        )
        logger.info(f"GCP Project ID: {settings.GCP_PROJECT_ID}")
        self.client = storage.Client(
            project=settings.GCP_PROJECT_ID, credentials=credentials
        )
        logger.info("Conexión a Google Cloud Storage exitosa")

    def upload_file(
        self,
        bucket_name: str,
        destination_path: str,
        file: Any = None,
        file_path: str = None,
    ):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_path)
        content_type = (
            "video/mp4"
            if destination_path.endswith(".mp4")
            else "application/octet-stream"
        )
        blob.content_type = content_type
        if file:
            blob.upload_from_file(file)
        elif file_path:
            blob.upload_from_filename(file_path)
        else:
            raise ValueError("Debe proporcionar un archivo o una ruta de archivo")
        return blob.public_url

    def download_file(self, bucket_name: str, source_path: str):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(source_path)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_file.close()
        blob.download_to_filename(temp_file.name)
        return temp_file.name

    def download_file_as_bytes(self, bucket_name: str, source_path: str):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(source_path)
        return blob.download_as_bytes()

    def list_files(self, bucket_name: str):
        bucket = self.client.bucket(bucket_name)
        return [blob.name for blob in bucket.list_blobs()]

    def get_public_url(self, bucket_name: str, file_path: str):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        return blob.generate_signed_url(expiration=3600)
