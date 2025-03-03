"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


import os, requests, json


# Initializing urls path.
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, '../../instance/urls.json')
with open(file_path, 'r') as urls:
    url = json.load(urls)
