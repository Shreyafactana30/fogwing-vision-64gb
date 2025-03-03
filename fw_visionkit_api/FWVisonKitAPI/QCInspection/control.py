"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from FWVisonKitAPI.QCInspection.model import add_update_qcorder_m, get_category_type_m, get_quantity_count_m, \
                                             get_count_category_m


# this function will add and update the record
def add_update_qcorder_c(json_data):
    return add_update_qcorder_m(json_data)


# this function will return the good and rejected quantity based on order id and order type
def get_quantity_count_c(order_code, product_names):
    product_names = product_names.split(',')
    return get_quantity_count_m(order_code, product_names)


# this function will display the all product category type based on order id
def get_category_type_c(order_code):
    return get_category_type_m(order_code)


# This function will give good, rejection, total, and category_type count.
def get_count_category_c(order_code, product_names):
    product_names = product_names.split(',')
    return get_count_category_m(order_code, product_names)
