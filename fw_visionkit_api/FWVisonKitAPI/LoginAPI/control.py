"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""
    

# This function will aunthenticate user from vision cloud database.
from FWVisonKitAPI.QCOrderAPI.model import update_payload_order_m


def post_login_control(login_data):
    access_code = login_data.get("access_code")
    if access_code == "12345":
        update_payload_order_m()
        default_info = {"first_name": "Default", "last_name": "User"}
        return default_info
    else:
        return {"Unsuccessful": "Invalid access code"}, 401
