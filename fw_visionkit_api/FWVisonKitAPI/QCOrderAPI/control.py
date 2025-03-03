"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

import random
import string
from datetime import datetime

from FWVisonKitAPI import app
from FWVisonKitAPI.QCOrderAPI.model import delete_order_m, get_qc_order_m, sync_qc_orders_m, add_qc_order_m, \
    get_open_orders_m, get_order_m, update_qc_order_m, previous_order_m


# this function will generate the random 6-digit code
def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code


# This function will return the list of qc order.
def get_qc_order_c():
    return get_qc_order_m()


# This function will fetch the QC order from the cloud.
def sync_qc_orders_c():
    return sync_qc_orders_m()


# this function will add the order quantity in order table
def add_qc_order_c(data):
    try:
        if data['fwv_order_status'] not in ('Open', 'In Progress', 'Stopped', 'Completed'):
            return {'unsuccessful': 'Invalid Order Status'}, 400

        data['fwv_order_code'] = generate_code()
#        data['fwv_order_date'] = datetime.now()
        return add_qc_order_m(data)
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500


# this function will return the all order which are in open status
def get_open_orders_c():
    return get_open_orders_m()


# this function will return the particular order details
def get_order_c(order_code):
    return get_order_m(order_code)


# this function will delete the order from the order table
def delete_order_c(order_code):
    return delete_order_m(order_code)


# this function will update the record of qc order
def update_qc_order_c(order_code, order_status):
    return update_qc_order_m(order_code, order_status)


# this route will give the privious order detail.
def previous_order_c(current_order_code):
    return previous_order_m(current_order_code)
