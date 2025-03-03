"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from FWVisonKitAPI.SupplierAPI.model import get_suppliers_m, sync_suppliers_m


# This function will return the list of suppliers.
def get_suppliers_c():
    return get_suppliers_m()


# This function will fetch the products from the cloud.
def sync_suppliers_c():
    return sync_suppliers_m()
