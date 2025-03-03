"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from FWVisonKitAPI.CloudConnectionAPI.model import get_cloudconn_data_model, post_cloudconn_data_model


# This function will return the cloud conn data.
def get_cloudconn_data_control():
     return get_cloudconn_data_model()


# This function will add the cloud conn data in to table.
def post_cloudconn_data_control(conn_data):
     return post_cloudconn_data_model(conn_data)
