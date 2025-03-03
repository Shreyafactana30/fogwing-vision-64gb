"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from FWVisonKitAPI.ProductAPI.model import get_product_name_m, get_products_m, sync_products_m


# This function will return the list of products.
def get_products_c():
     return get_products_m()


# This function will fetch the products from the cloud.
def sync_products_c():
     return sync_products_m()


# this function will return the all distinct product name
def get_product_name_c():
     return get_product_name_m()