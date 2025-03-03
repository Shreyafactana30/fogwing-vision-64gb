"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import request
from flask import Blueprint
from FWVisonKitAPI.SupplierAPI.control import get_suppliers_c, sync_suppliers_c


# Blueprint creation.
fwv_supplier_bp = Blueprint("fwv_supplier_bp", __name__, url_prefix='/fwvision/supplier')


# This route will return list of suppliers
@fwv_supplier_bp.route("/", methods=['GET'])
def get_suppliers():
    return get_suppliers_c()


# This route will sync the fault data from cloud.
@fwv_supplier_bp.route("/", methods=['PUT'])
def sync_suppliers_v():
    return sync_suppliers_c()
