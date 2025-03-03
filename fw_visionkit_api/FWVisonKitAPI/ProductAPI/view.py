"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import request
from flask import Blueprint
from FWVisonKitAPI.ProductAPI.control import get_product_name_c, get_products_c, sync_products_c


# Blueprint creation.
fwv_product_bp = Blueprint("fwv_product_bp", __name__, url_prefix='/fwvision/product')


# This route will return all the fault data
@fwv_product_bp.route("/", methods=['GET'])
def get_products_v():
     return get_products_c()


# This route will sync the fault data from cloud.
@fwv_product_bp.route("/", methods=['PUT'])
def sync_products_v():
     return sync_products_c()


# This route will return all distict product name
@fwv_product_bp.route("/product", methods=['GET'])
def get_product_name_v():
     return get_product_name_c()