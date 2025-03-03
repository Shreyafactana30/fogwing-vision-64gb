"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import requests, json
from FWHMIKitAPI.ExternalMMAPI import url


# This method will call the downReasons api to fetch all data.
def get_Down_data(access_code):
    try:
        get_faults_info = url["DOWNREASON"]["GET_AND_SYNC_DOWNREASON"].format(access_code)
        resp = requests.get(url=get_faults_info)
        if resp.status_code == 200:
            return resp.json(), resp.status_code
        else:
            return resp.json(), resp.status_code
    except Exception:
        return {"Unsuccessful": "Server Is Not Responding"}, 500
