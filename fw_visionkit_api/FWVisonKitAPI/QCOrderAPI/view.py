"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import base64
import time

from flask import Blueprint
from flask import Response, request

from FWVisonKitAPI.HomeAPI.control import get_update_payload_c
from FWVisonKitAPI.QCOrderAPI.control import delete_order_c, get_qc_order_c, sync_qc_orders_c, add_qc_order_c, \
    get_open_orders_c, get_order_c, update_qc_order_c, previous_order_c
from instance.config import IMAGE_PATH

# Blueprint creation.
fwv_qcorder_bp = Blueprint("fwv_qcorder_bp", __name__, url_prefix='/fwvision/qcorder')


# This route will return all the quality control data
@fwv_qcorder_bp.route("/", methods=['GET'])
def get_qc_order_v():
    return get_qc_order_c()


# This route will sync the fault data from cloud.
@fwv_qcorder_bp.route("/", methods=['PUT'])
def sync_qc_orders_v():
    return sync_qc_orders_c()


# this route will add the qc order details
@fwv_qcorder_bp.route("/", methods=['POST'])
def add_qc_order_v():
    if request.method == 'POST':
        data = request.get_json()
        try:
            return add_qc_order_c(data)
        except Exception as e:
            return {"Unsuccessful": "Something went wrong"}, 500


# This route will return all the quality control data
@fwv_qcorder_bp.route("/open-order", methods=['GET'])
def get_open_orders_v():
    return get_open_orders_c()


# this function will return the image which is stored in device location
@fwv_qcorder_bp.route('/image_events', methods=['GET'])
def image_events():
    def generate_image_events():
        try:
            while True:
                odr_id_type  = get_update_payload_c()
                if odr_id_type.get("fwv_order_code"):
                    with open(IMAGE_PATH, 'rb') as image_file:
                        image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        if image_data:
                            yield f"id:1\ndata: {image_data}\nevent: online\n\n"
                        else:
                            yield "id:1\ndata: Image data not available\nevent: offline\n\n"
                    time.sleep(1)
                else:
                    yield "id:1\ndata: None\nevent: offline\n\n"
                time.sleep(1)
        except FileNotFoundError:
            yield "data: Image file not found\n\n"
        except Exception as e:
            yield f"data: Something went wrong - {str(e)}\n\n"
    return Response(generate_image_events(), content_type='text/event-stream')


# This route will return particular order details
@fwv_qcorder_bp.route("/get_order/<string:order_code>", methods=['GET'])
@fwv_qcorder_bp.route("/get_order/", methods=['GET'])
def get_order_v(order_code=None):
    return get_order_c(order_code)


# this route will delete the order from the order table
@fwv_qcorder_bp.route("/<string:order_code>", methods=['DELETE'])
def delete_order_v(order_code):
    return delete_order_c(order_code)


# this route will update the qc order details
@fwv_qcorder_bp.route("/update_order/<string:order_code>/<string:order_status>", methods=['PUT'])
def update_qc_order_v(order_code, order_status):
    if request.method == 'PUT':
        try:
            return update_qc_order_c(order_code, order_status)
        except Exception as e:
            return {"Unsuccessful": "Something went wrong"}, 500


# this route will give the privious order detail.
@fwv_qcorder_bp.route("/previous_order/<string:current_order_code>", methods=['GET'])
def previous_order(current_order_code):
    return previous_order_c(current_order_code)
