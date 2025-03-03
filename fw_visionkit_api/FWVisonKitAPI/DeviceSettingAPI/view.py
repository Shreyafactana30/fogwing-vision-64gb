"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import request, Response, stream_with_context
from flask import Blueprint
from FWVisonKitAPI.DeviceSettingAPI.control import get_ssids_control, post_wifi_conn_control, \
  start_camera_control, stop_camera_control, check_image_count_control


# Blueprint creation.
fwvison_deviceset_bp = Blueprint("fwvision_devicesetting", __name__, url_prefix='/fwvision/config')


# This route will return list of networks available.
@fwvison_deviceset_bp.route("/ssids", methods=['GET'])
def get_ssids():
     return get_ssids_control()


# This route will connect to a Wi-Fi network.
@fwvison_deviceset_bp.route("/wifi-conn", methods=['POST'])
def post_wifi_conn_data():
     if request.method == "POST":
          wifi_conn_data = request.get_json()
          if wifi_conn_data:
               return post_wifi_conn_control(wifi_conn_data)
          else:
               return dict(Unsuccessful="Unprocessable Entity"), 422


# This route will start capturing images
@fwvison_deviceset_bp.route("/start-capture", methods=['GET'])
def start_camera():
     return start_camera_control()


# This method will stop capturing images
@fwvison_deviceset_bp.route("/stop-capture", methods=['GET'])
def stop_camera():
     return stop_camera_control()


# This method will check no. of images in images directory.
@fwvison_deviceset_bp.route("/check-images-count")
def vehiclend_listen():
    return Response(stream_with_context(check_image_count_control()), mimetype="text/event-stream")