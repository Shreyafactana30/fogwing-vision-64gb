"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

import time
from datetime import datetime, timedelta
from firmware.system_config import SYSConf


# This method will return list of networks available.
def get_ssids_control():
    wifi_list = SYSConf()
    ssids = wifi_list.scan_wifi_nw()
    try:
        if ssids:
            return dict(ssids=ssids), 200
        else:
            return dict(Unsuccessful="No networks available"), 404
    except Exception:
        return dict(Unsuccessful="Something went wrong"), 500

# This method will connect to a Wi-Fi network
def post_wifi_conn_control(wifi_data):
    wifi_conn = SYSConf()
    try:
        if len(wifi_data.get("password")) < 8:
            return dict(Unsuccessful="Password should be between 8 and 63 characters"), 400
        wifi_cred = wifi_conn.wifi_config(wifi_data.get("ssid"), wifi_data.get("password"))
        if wifi_cred:
            return dict(Successful= f"Connected to {wifi_data.get('ssid')}"), 200
        else:
            return dict(Unsuccessful="Failed to connect"), 404
    except Exception:
        return dict(Unsuccessful="Something went wrong"), 500


# This method will start capturing images
def start_camera_control():
    cam_start = SYSConf()
    try:
        cam_start.start_capture()
        return dict(Successful= "Scanning started"), 200
    except Exception:
        return dict(Unsuccessful="Something went wrong"), 500


# This method will stop capturing images
def stop_camera_control():
    cam_stop = SYSConf()
    try:
        cam_stop.stop_capture()
        return dict(Successful= "Scanning stopped"), 200
    except Exception:
        return dict(Unsuccessful="Something went wrong"), 500

# This method will check if images are remaining to be processed.
def check_image_count_control():
    check_image_count = SYSConf()
    while True:
        image_count = check_image_count.no_of_images()
        yield f"id: 1\ndata: {image_count}\nevent: online\n\n"
        time.sleep(5)
