"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from datetime import datetime, timedelta
from FWVisonKitAPI.EdgeSettingAPI.model import FWVEdgeSetup

payload_data = {
                "fwv_order_code": None,
                "fwv_order_id": None,
                "product_name": None,
                "fwv_order_status": None
                }


# this function will update the orde payload
def update_payload_c(data):
    if data:
        payload_data.update(data)
        return dict(Successful="Successfully Updated The Data."), 200
    else:
        return dict(Unuccessful="Bad request"), 400


# This method will genrate the JSON file.
def get_update_payload_c():
    """
    This function removes None value(source or destination) from the payload and creates
    JSON file that contains payload and shift data.
    """
    try:
        return payload_data
    except Exception:
        return dict(Unsuccessful="Something Went Wrong")
