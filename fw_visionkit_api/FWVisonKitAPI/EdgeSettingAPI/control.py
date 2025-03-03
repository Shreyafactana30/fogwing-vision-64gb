"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from FWVisonKitAPI.EdgeSettingAPI.model import get_edgeset_data_model, get_shifts_m, post_edgeset_data_model


# This function will return the vision edge screen data.
def get_edgeset_data_control():
     return get_edgeset_data_model()


# This function will add the vision edge screen data in to table.
def post_edgeset_data_control(himisetup_data):
    return post_edgeset_data_model(himisetup_data)


# this function will call the eternal api and return the updated shifts data
def get_shifts_c():
     return get_shifts_m()