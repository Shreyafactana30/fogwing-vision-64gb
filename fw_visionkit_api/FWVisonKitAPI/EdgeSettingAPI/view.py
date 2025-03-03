"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import request
from flask import Blueprint
from FWVisonKitAPI.EdgeSettingAPI.control import get_edgeset_data_control, get_shifts_c, post_edgeset_data_control


# Blueprint creation.
fwvison_edgeset_bp = Blueprint("fwvision_edgesetting", __name__, url_prefix='/fwvision/edge')


# This route will return vision setup screen data.
@fwvison_edgeset_bp.route("/", methods=['GET'])
def get_edgeset_data():
     return get_edgeset_data_control()


# This route will add the vision setup screen data into database.
@fwvison_edgeset_bp.route("/", methods=['POST'])
def post_edgeset_data():
     if request.method == "POST":
          try:
               hmisetup_data = request.get_json()
               if hmisetup_data:
                    return post_edgeset_data_control(hmisetup_data)
               else:
                    return dict(Unsuccessful="Unprocessable Entity"), 422
          except Exception as e:
               return {"Unsuccessful": "Something went wrong"}, 500
               
               
# this route will return the shifts name and timing
@fwvison_edgeset_bp.route("/get_shifts") 
def get_shifts_v():
     return get_shifts_c()