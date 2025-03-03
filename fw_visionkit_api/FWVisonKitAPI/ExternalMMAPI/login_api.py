"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import requests, json
from FWHMIKitAPI.ExternalMMAPI import url


def post_login(access_code):
    try:
        post_data = url["LOGIN_API"]["POST_LOGIN_API"].format(access_code)
        resp = requests.get(url=post_data)
        if resp.status_code == 200:
            return resp.json(), resp.status_code
        else:
            return resp.json(), resp.status_code
    except Exception:
        return {"Unsuccessful": "Server Is Not Responding"}, 500
