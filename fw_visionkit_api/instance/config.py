""" * Copyright (C) 2021 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package. """


from os.path import expanduser
import json


home = expanduser("~" + "/object_tracking/credentials/saahascv_cred.json")
with open(home, "r") as cred:
    fwvision_cred = json.load(cred)


SQLALCHEMY_DATABASE_URI = fwvision_cred.get("DB_URL")
IMAGE_PATH = fwvision_cred.get("IMAGE_PATH")
CREATE_ORDER_EVENT_CODE = fwvision_cred.get("CREATE_ORDER_EVENT_CODE")
UPDATE_ORDER_EVENT_CODE = fwvision_cred.get("UPDATE_ORDER_EVENT_CODE")
PATH_TO_WRITE_PAYLOAD = fwvision_cred.get("PATH_TO_WRITE_PAYLOAD")
WEIGHTS = fwvision_cred.get("WEIGHTS")
