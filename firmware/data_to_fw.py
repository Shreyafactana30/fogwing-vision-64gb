""" * Copyright (C) 2023 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package."""

import os
import threading
import time, json, requests

from pub_data_api import APIPub
from pub_data_via_mqtt import MQTTClient
from cv_log import logger

class PayloadReader:
    """
    Class to read payloads from files and send them to the Fogwing API.
    """
    def __init__(self):
        """
        Constructor method to initialize the required paths for payloads.
        """
        # PROD Configuration
        self.BROKER = "iothub.fogwing.net"  # Replace with your MQTT broker
        self.PORT = 1883
        self.TOPIC = "fwent/edge/84c6cb9f4acd7862/inbound"
        self.CLIENT_ID = "1151-1787-2615-4032"
        self.USERNAME = "84c6cb9f4acd7862"  # Replace with your username if needed
        self.PASSWORD = "Qnlpmzmx8$"  # Replace with your password if needed

        # #Devin Configuration
        # self.BROKER = "iothub-demo.fogwing.net"  # Replace with your MQTT broker
        # self.PORT = 1883
        # self.TOPIC = "fwent/edge/3548e057b0f4885b/inbound"
        # self.CLIENT_ID = "3351-4894-2197-6708"
        # self.USERNAME = "3548e057b0f4885b"  # Replace with your username if needed
        # self.PASSWORD = "Aujmqlsv0*"  # Replace with your password if needed


        self.payload_path = os.path.expanduser('~/object_tracking/payloads/')
        self.order_status_payload_path = os.path.expanduser('~/object_tracking/order_status_payloads/')
        # self.api_pub = APIPub()
        self.mqtt_pub = MQTTClient(broker=self.BROKER, port=self.PORT, topic=self.TOPIC, client_id=self.CLIENT_ID, username=self.USERNAME,
                                 password=self.PASSWORD)

    # def _process_file(self, file_path):
    #     """
    #     Process a single file by reading its content and sending it to the Fogwing API.
    #     :param file_path: The path of the file to be processed
    #     :return: None
    #     """
    #     try:
    #         if os.path.getsize(file_path) == 0:
    #             logger.error(f"File {file_path} is empty. Removing.")
    #             os.remove(file_path)
    #             return
    #
    #         with open(file_path, 'r') as open_file:
    #             payload = open_file.read()
    #
    #         status_code = self.api_pub.sendtofwg(payload)
    #         if status_code == 201:
    #             os.remove(file_path)
    #         else:
    #             logger.error(f"Error sending data to Fogwing. Status code: {status_code}")
    #
    #     except Exception as ex:
    #         logger.error(f"Exception processing file {file_path}: {ex}")

     # Counters
        self.cloud_count = 0
        self.device_count = 0
        self.start_time = time.time()

    def _log_counts(self):
        print("started", print(f"intial Payloads sent - Cloud: {self.cloud_count}, Device API: {self.device_count}"))
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 60:  # Log every 60 seconds
            print(f"final Payloads sent - Cloud: {self.cloud_count}, Device API: {self.device_count}")
            logger.info(f"Payloads sent - Cloud: {self.cloud_count}, Device API: {self.device_count}")
            self.start_time = time.time()  # Reset timer


    def _process_file(self, file_path):
        """
        Process a single file by reading its content and sending it to the Fogwing API.
        :param file_path: The path of the file to be processed
        :return: None
        """
        try:
            if os.path.getsize(file_path) == 0:
                logger.error(f"File {file_path} is empty. Removing.")
                os.remove(file_path)
                return

            with open(file_path, 'r') as open_file:
                payload = open_file.read()

            try:
                self.mqtt_pub.connect()
                is_sent = self.mqtt_pub.publish(payload)
                time.sleep(3)
                if is_sent:
                    self.cloud_count += 1  # Increment cloud count
                    if "/home/factana/object_tracking/payloads" in file_path:
                        payload_dict = json.loads(payload)

                        sub_category_count = payload_dict.get('product')
                        sub_category_count["order_code"] = payload_dict.get('order_code')
                        sub_category_count["product_name"] = payload_dict.get('product_name')

                        resp=requests.put("http://127.0.0.1:7077/fwvision/qcinspection/update_qc_order", json=sub_category_count)
                        print(resp.status_code)
                        del sub_category_count["product_name"]
                        del sub_category_count["order_code"]

                        # Check the status code and increment the counter
                        if resp.status_code in {200, 201}:
                            self.device_count += 1

                        else:
                            logger.error(f"Error sending data to device. Status code: {resp.status_code}")

                        os.remove(file_path)
                    else:
                        print("elsee")
                        os.remove(file_path)
                else:
                    logger.error(f"Error sending data to Fogwing. Status code: {is_sent}")

                self._log_counts()  # Log counts periodically

            except KeyboardInterrupt:
                logger.error(f"Interrupted by user")
            except Exception as e:
                logger.error(f"Error : {e}")
            finally:
                self.mqtt_pub.disconnect()

        except Exception as ex:
            logger.error(f"Exception processing file {file_path}: {ex}")

    def _process_directory(self, directory_path):
        """
        Process all files in a directory and send their payloads to the Fogwing API.
        :param directory_path: The directory containing the payload files
        :return: None
        """
        try:
            lst_dir = sorted(os.listdir(directory_path))
            for file in lst_dir:
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    self._process_file(file_path)
        except Exception as ex:
            logger.error(f"Exception processing directory {directory_path}: {ex}")
            pass

    def payloads(self):
        """
        Continuously read payload files and send them to Fogwing API.
        :return: None
        """
        try:
            while True:
                self._process_directory(self.payload_path)
                time.sleep(0.3)
        except Exception as ex:
            logger.error(f"Exception in payload processing loop: {ex}")
            pass

    def order_status(self):
        """
        Continuously read order status payload files and send them to Fogwing API.
        :return: None
        """
        try:
            while True:
                self._process_directory(self.order_status_payload_path)
                time.sleep(0.3)
        except Exception as ex:
            logger.error(f"Exception in order status processing loop: {ex}")
            pass


if __name__ == '__main__':
    """
    Continuously read payload data and send them to Fogwing API.
    """
    payload_reader = PayloadReader()

    payloads_thread = threading.Thread(target=payload_reader.payloads)
    payloads_thread.start()

    payload_reader.order_status()
