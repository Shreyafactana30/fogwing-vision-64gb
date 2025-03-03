""" * Copyright (C) 2023 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import logging
import argparse


logging.disable(logging.WARNING)
parser = argparse.ArgumentParser()
parser.add_argument("--loglevel", type=str, required=False, default="DEBUG", help="set loglevel")
parser.add_argument("--console", type=str, required=False, default=True, help="Display message on console")
args = parser.parse_args()
level_type = args.loglevel
console = args.console

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(filename)s %(levelname)s: %(message)s')
try:
    if level_type.lower() == "info":
        logger.setLevel(logging.INFO)
    elif level_type.lower() == "debug":
        logger.setLevel(logging.DEBUG)
    elif level_type.lower() == "error":
        logger.setLevel(logging.ERROR)
    elif level_type.lower() == "warning":
        logger.setLevel(logging.WARNING)
except Exception:
    pass

file_handler = logging.FileHandler("/home/factana/object_tracking/firmware/cv_kit.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
