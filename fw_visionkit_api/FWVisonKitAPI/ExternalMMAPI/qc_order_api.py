"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import requests, json
from FWVisonKitAPI.ExternalMMAPI import url

# This method will call the quality control order api to fetch all data.
def get_qc_order_data(tenant_id, edge_eui):
    try:
        get_qc_order_info = url["QCORDER"]["GET_AND_SYNC_QCORDERS"]
        params = {'edge_eui': edge_eui, 'tenant_id': tenant_id}
        resp = requests.get(url=get_qc_order_info, params=params)
        if resp.status_code == 200:
            return resp.json(), resp.status_code
        else:
            return resp.json(), resp.status_code
    except Exception as e:
        return {"Unsuccessful": "Server Is Not Responding"}, 500


# this function will call the post method of order from web application
def post_order_data(data):
    try:
        post_ord_url = url["QCORDER"]["POST_QCORDERS"]
        resp = requests.post(url=post_ord_url, json=data)
        if resp.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return {"Unsuccessful": "Server Is Not Responding"}, 500


# this function will call the vision order update api
def update_order_data(order_id, data):
    try:
        update_order_url = url["QCORDER"]["UPDATE_QCORDER"].format(order_id)
        resp = requests.put(update_order_url, json=data)
        if resp.status_code == 200:
            True
        else:
            return False
    except Exception as e:
        return {"Unsuccessful": "Server Is Not Responding"}, 500


# This method will call the faults api to fetch all data.
def get_shifts_data(tenant_id, edge_eui):
    try:
        shifts_url = url["SHIFTS"]["GET_SHIFTS_TIMING"]
        params = {'tenant_id': tenant_id, "edge_eui": edge_eui}
        resp = requests.get(url=shifts_url, params=params)
        return resp.json(), resp.status_code
    except Exception as e:
        return {"Unsuccessful": "Something went wrong"}, 500
