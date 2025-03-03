"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import request
from flask import Blueprint
from FWVisonKitAPI.LoginAPI.control import post_login_control


# Blueprint creation.
fwvision_usermgmt_bp = Blueprint("fwvision_usermgmt", __name__, url_prefix='/fwvision/user')


# This route will aunthenticate user from MM cloud database.
@fwvision_usermgmt_bp.route("/login", methods=['POST'])
def login():
     if request.method == "POST":
          login_data = request.get_json()
          if login_data:
               return post_login_control(login_data)
          else:
               return dict(Unsuccessful="Unprocessable Entity"), 422
