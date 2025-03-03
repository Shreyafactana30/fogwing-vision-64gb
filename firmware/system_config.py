""" * Copyright (C) 2023 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import os
import time
import subprocess
import Jetson.GPIO as GPIO


class SYSConf:
    """
    Class to control system realted functions via APIs
    """
    def __init__(self):
          """
          Initializing GPIOs and path to read credentials
          """
          self.image_directory = os.path.expanduser("~/object_tracking/images/")
          self.GREEN_LED = 13
          self.RED_LED = 11
          GPIO.setwarnings(False)
          GPIO.setmode(GPIO.BCM)
          GPIO.setup(self.GREEN_LED, GPIO.OUT, initial=GPIO.LOW)
          GPIO.setup(self.RED_LED, GPIO.OUT, initial=GPIO.LOW)

    @staticmethod
    def scan_wifi_nw():
        """
        This function is to scan Wi-Fi networks available
        :return: List of the Wi-Fi networks avilable
        """
        try:
            ssid = ""
            cmd_output = subprocess.check_output("sudo nmcli -f SSID dev wifi list --rescan yes | grep -v 'SSID'", shell=True)
            cmd_res = cmd_output.decode("utf-8")
            time.sleep(0.5)
            ssid_list = cmd_res.strip().split('\n')
            return [ssid.strip() for ssid in ssid_list]
        except Exception:
            pass

    @staticmethod
    def wifi_config(ssid, pwd):
        """
        This function writes the SSID and password of the Wi-Fi network
        :param ssid: SSID of Wi-Fi
        :param pwd: Password of Wi-Fi
        :return: True if Wi-Fi is connected else false
        """
        try:
            response = subprocess.check_output(f"sudo nmcli device wifi connect {ssid} password {pwd}", shell=True)
            wifi_res = response.decode("utf-8")
            if "successfully" in wifi_res:
                return True
            else:
                return False
        except Exception:
            pass


    def start_capture(self):
        """
        This instructs to start capturing images
        :return: None
        """
        try:
            subprocess.run("sudo systemctl start capture_img.service", shell=True)
            GPIO.output(self.GREEN_LED, GPIO.HIGH)
            GPIO.output(self.RED_LED, GPIO.LOW)
        except Exception:
            pass


    def stop_capture(self):
        """
        This instructs to stop capturing images
        :return: None
        """
        try:
            subprocess.run("sudo systemctl stop capture_img.service", shell=True)
            GPIO.output(self.GREEN_LED, GPIO.LOW)
            GPIO.output(self.RED_LED, GPIO.LOW)
        except Exception:
            pass

    def no_of_images(self):
        """
        This function checks if images are present
        in the directory
        :return: True is images are present, false otherwise
        :rtype: Bool
        """
        try:
            images_count = subprocess.check_output(f"ls {self.image_directory} | wc -l", shell=True)
            return int(images_count)
        except Exception:
            return None
