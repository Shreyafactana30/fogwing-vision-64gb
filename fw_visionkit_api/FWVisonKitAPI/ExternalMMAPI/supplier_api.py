"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import requests, json
from FWVisonKitAPI.ExternalMMAPI import url


# This method will call the products api to fetch all data.
def get_supplier_data(fw_tenant_id):
    try:
        params = {'tenant_id': fw_tenant_id}
        get_suppliers_info = url["SUPPLIER"]["GET_AND_SYNC_SUPPLIERS"]
        resp = requests.get(url=get_suppliers_info, params=params)
        if resp.status_code == 200:
            return resp.json(), resp.status_code
        else:
            return resp.json(), resp.status_code
    except Exception as e:
        return {"Unsuccessful": "Server Is Not Responding"}, 500