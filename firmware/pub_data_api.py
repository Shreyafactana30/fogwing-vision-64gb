""" * Copyright (C) 2023 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import json
import os
import requests

from cv_log import logger


class APIPub:
    """
    This class is used to send payload data to a Fogwing API.
    """

    def __init__(self):
        """
        Initializes the class instance by setting class-level attributes:
        - cred_path: absolute path to the credentials file
        - api_url: API URL to post payload using API Key
        - account_id: Fogwing account ID
        - api_key: API key for the Fogwing API
        - edge_eui: Edge EUI for the device connected to the Fogwing API
        """
        _cred_path = os.path.expanduser('~' + '/object_tracking/credentials/saahascv_cred.json')
        with open(_cred_path, "r") as open_file:
            _cred = json.loads(open_file.read())
        _api_cred = _cred.get('API_CRED')
        self.api_url = _api_cred.get("HOST")
        cloud_conn = requests.get(_cred.get('CLOUD_CONN_URL')).json()
        edge_data = requests.get(_cred.get('EDGE_SETTING_URL')).json()
        self.api_key = cloud_conn.get("cloud_conn")[0].get("fwv_fogwing_apikey")
        self.account_id = edge_data.get("edgesetup")[0].get("fw_tenant_id")
        self.edge_eui = edge_data.get("edgesetup")[0].get("fwv_dev_eui")

    def sendtofwg(self, payload):
        """
        Sends payload data to Fogwing API.
        :param payload: Payload data to be sent to Fogwing.
        :return: HTTP status code of the API response.
        :rtype: int
        """
        try:
            header = {"accountID": str(self.account_id), "apiKey": self.api_key, "edgeEUI": self.edge_eui}
            payload_resp = requests.post(self.api_url, data=payload, headers=header, timeout=10)
            return payload_resp.status_code
        except Exception as ex:
            logger.error(ex)
            pass
