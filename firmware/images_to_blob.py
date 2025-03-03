""" * Copyright (C) 2024 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import os
import json
import time
import requests
from azure.storage.blob import BlobServiceClient

from cv_log import logger


class BlobUploader:
    """
    A class responsible for handling Azure Blob Storage uploads.
    """
    def __init__(self):
        self.image_dir = os.path.expanduser('~/object_tracking/predicted_images/')
        _config_path = os.path.expanduser('~/object_tracking/credentials/saahascv_cred.json')

        with open(_config_path, "r") as config_file:
            _config = json.load(config_file)
        blob_config = _config.get("BLOB_STORAGE_CONFIG")
        _connect_str = blob_config.get("BLOB_STORAGE_CONNECTION_STRING")
        self.container_name = blob_config.get("CONTAINER_NAME")
        self.blob_service_client = BlobServiceClient.from_connection_string(_connect_str)

        response = requests.get(_config.get("EDGE_DATA_URL"))
        response.raise_for_status()
        edge_data = response.json()
        self.tenant_id = edge_data["edgesetup"][0]["fw_tenant_id"]
        self.asset_code = edge_data["edgesetup"][0]["fwv_asset_code"]

    def upload_image(self):
        """
        This method scans the specified directory and upload images to Azure Blob Storage.
        :return: None
        """
        try:
            for filename in sorted(os.listdir(self.image_dir)):
                image_path = os.path.join(self.image_dir, filename)
                if os.path.isfile(image_path):
                    blob_client = self.blob_service_client.get_blob_client(
                        container=self.container_name, blob=f"vision/{self.tenant_id}/{self.asset_code}/{filename}")

                    with open(image_path, "rb") as image_file:
                        blob_client.upload_blob(image_file, content_type='image/png', overwrite=True)
                    properties = blob_client.get_blob_properties()
                    if properties.size == os.path.getsize(image_path):
                        os.remove(image_path)
                    else:
                        logger.error(f"Upload verification failed for {filename}")
        except Exception as ex:
            logger.error(f"Error uploading {filename}: {ex}")
            pass


if __name__ == '__main__':
     uploader = BlobUploader()
     while True:
       try:
          uploader.upload_image()
          time.sleep(0.5)
       except Exception as ex:
          logger.log(f"Fatal error:{ex}")
          continue
