"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import time

from flask import Blueprint
from flask import Response, request, stream_with_context

from FWVisonKitAPI.QCInspection.control import add_update_qcorder_c, get_category_type_c, get_quantity_count_c, \
                                               get_count_category_c

# Blueprint creation.
fwv_qcinspection_bp = Blueprint("fwv_qcinspection_bp", __name__, url_prefix='/fwvision/qcinspection')


# this route will add the data and if data is there on particular order id then it will update the data
@fwv_qcinspection_bp.route('/update_qc_order', methods = ['PUT'])
def add_update_qcorder_v():
    if request.method == 'PUT':
        json_data = request.get_json()
        try:
            return add_update_qcorder_c(json_data)
        except Exception as e:
            return {"Unsuccessful": "Something went wrong"}, 500


# this route will return the goods and rejection counts
@fwv_qcinspection_bp.route('/<string:order_code>/<string:product_names>', methods=['GET'])
def get_quantity_count_v(order_code, product_names):
    def sse_product():
        while True:
            data = get_quantity_count_c(order_code, product_names)
            yield f"id: 1\ndata: {data[0]}\nevent: online\n\n"
            time.sleep(1)
    return Response(stream_with_context(sse_product()), mimetype="text/event-stream")


# this route will display the all product category type based on order id
@fwv_qcinspection_bp.route('/category_type/<string:order_code>', methods=['GET'])
def get_category_type_v(order_code):
    def sse_category_type():
        while True:
            data = get_category_type_c(order_code)
            yield f"id: 1\ndata: {data[0]}\nevent: online\n\n"
            time.sleep(1)
    return Response(stream_with_context(sse_category_type()), mimetype="text/event-stream")


# this route will display all product category type, good, rejection, and total count based on order id
@fwv_qcinspection_bp.route('/count_category/<string:order_code>/<string:product_names>', methods=['GET'])
def get_count_category(order_code, product_names):
    def sse_count_category_type():
        while True:
            data = get_count_category_c(order_code, product_names)
            yield f"id: 1\ndata: {data[0]}\nevent: online\n\n"
            time.sleep(1)
    return Response(stream_with_context(sse_count_category_type()), mimetype="text/event-stream")
