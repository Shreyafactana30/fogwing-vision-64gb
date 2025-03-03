"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import time
import json
from flask import request, Response, stream_with_context
from flask import Blueprint
from FWVisonKitAPI.HomeAPI.control import get_update_payload_c, update_payload_c
# from firmware.system_config import WiFiSettings


# Blueprint creation.
fwv_home_bp = Blueprint("fwv_home_bp", __name__, url_prefix='/fwvision/home')


# This route will update the in memory payload data.
@fwv_home_bp.route("/update_payload", methods=['PUT'])
def update_payload_v():
    """
    In the Payload either source or destination will be present both cannot
    exist at same time. 
    """
    if request.method == "PUT":
        try:
            data = request.get_json()
            if data:
                return update_payload_c(data)
        except Exception as e:
            return dict(Unsuccessful="Something Went Wrong"), 500


# This route will store payload data in JSON file.
@fwv_home_bp.route("/get_payload_data")
def get_update_payload_v():
    return get_update_payload_c()

