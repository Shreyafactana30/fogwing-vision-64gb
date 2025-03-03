"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import request
from flask import Blueprint
from FWVisonKitAPI.CloudConnectionAPI.control import get_cloudconn_data_control, post_cloudconn_data_control

# Blueprint creation.
fwvision_cloudconn_bp = Blueprint("fwvision_cloudconn_bp", __name__, url_prefix='/fwvision/cloudconn')


# This route will return cloud conn data.
@fwvision_cloudconn_bp.route("/", methods=['GET'])
def get_cloudconn_data():
     return get_cloudconn_data_control()


# This route will add the cloud conn data into database.
@fwvision_cloudconn_bp.route("/", methods=['POST'])
def post_cloudconn_data():
     if request.method == "POST":
          conn_data = request.get_json()
          if conn_data:
               return post_cloudconn_data_control(conn_data)
          else:
               return dict(Unsuccessful="Unprocessable Entity"), 422
