""" * Copyright (C) 2023 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import time
import json
from datetime import datetime
from os.path import expanduser

import requests
import cv2
from cv_log import logger

image_path = expanduser('~/object_tracking/images/')
config_path = expanduser('~/object_tracking/credentials/saahascv_cred.json')
with open(config_path, "r") as config_file:
    camer_config = json.load(config_file)
CAPTURING_INTERVAL = camer_config.get('IMAGE_CAPTURING_INTERVAL')
TCP_STREAM = camer_config.get('TCP_STREAM')
PAYLOAD_DATA_URL = camer_config.get('PAYLOAD_DATA_URL')

def utcnow():
    """
    Returns the current UTC time as a string in epoch format.
    :return: Current UTC time in epoch format as a string.
    :rtype: str
    """
    try:
        local_time = datetime.now()
        epoch_time_utc = local_time.timestamp()
        return str(epoch_time_utc).replace(".", "").ljust(16, '0')
    except Exception as ex:
        logger.error(f"Error getting UTC time: {ex}")
        return None


def get_order_info():
    """
    Fetches the order code and product name from the API.
    :return: A formatted string with order code and product name, or False on failure.
    :rtype: str or bool
    """
    try:
        response = requests.get(PAYLOAD_DATA_URL)
        if response.status_code == 200:
            order_code = response.json().get("fwv_order_code")
            product_name = response.json().get("product_name")
            if order_code and product_name:
                return f"{order_code}_{product_name}"
            else:
                logger.error("Order info is incomplete.")
                return False
        else:
            logger.error(f"Failed to fetch order info. Status code: {response.status_code}")
            return False
    except Exception as ex:
        logger.error(f"Error getting order info: {ex}")
        return False


def capture_image():
    """
    Captures images from the camera and saves them with order info and timestamp as the filename.
    :return: None
    """

    Cam_driver = "/dev/video0"
    video_capture = cv2.VideoCapture(Cam_driver, cv2.CAP_V4L2)
    if not video_capture.isOpened():
        logger.error("Failed to open camera.")
        return

    last_capture_time = 0
    order_data = get_order_info()

    if not order_data:
        logger.error("Order data missing, cannot capture image.")
        return

    try:
        while True:
            current_time = time.time()
            ret_val, frame = video_capture.read()
            if not ret_val:
                logger.error("Failed to capture frame from the camera.")
                break

            if current_time - last_capture_time >= CAPTURING_INTERVAL:
                timestamp = utcnow()
                if timestamp:
                    image_filename = f"{image_path}img_{order_data}_{timestamp}.png"
                    print(image_path)
                    print(image_filename)
                    cv2.imwrite(image_filename, frame)
                    last_capture_time = current_time
                else:
                    logger.error("Error generating timestamp for the image.")
    except Exception as ex:
        logger.error(f"Exception during image capture: {ex}")
        pass
    finally:
        video_capture.release()


if __name__ == "__main__":
    try:
        capture_image()
    except Exception as ex:
        logger.error(f"Exception in main: {ex}")
        pass
