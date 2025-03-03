""" * Copyright (C) 2023 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import socket
import Jetson.GPIO as GPIO
from time import sleep
from os.path import expanduser
import json
import time


class LED:
    """
    Class to control LED actions
    """
    def __init__(self):
        """
        Initializing GPIOs and path to read credentials
        """
        self.ONLINE_LED = 20
        self.POWER_LED = 7
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ONLINE_LED, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.POWER_LED, GPIO.OUT, initial=GPIO.HIGH)

        self.cred_path = expanduser('~/object_tracking/credentials/saahascv_cred.json')
        with open(self.cred_path, "r") as open_file:
            self.cred = json.loads(open_file.read()).get('MQTT_CRED')

    def internet_status(self):
        """
        :return: True if internet is available else False
        """
        host = self.cred.get("SERVER_HOST")
        port = self.cred.get("PORT")
        try:
            socket.create_connection((host, port), timeout=1)
            return True
        except (socket.timeout, socket.error, Exception):
            return False

    def online_led(self):
        """
        This function is to blink LED if internet is available
        :return: None
        """
        try:
            if self.internet_status():
                GPIO.output(self.ONLINE_LED, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(self.ONLINE_LED, GPIO.LOW)
                time.sleep(1)
            else:
                GPIO.output(self.ONLINE_LED, GPIO.LOW)
                time.sleep(1)
        except Exception:
            pass


if __name__ == '__main__':
    status = LED()
    while True:
        status.online_led()
