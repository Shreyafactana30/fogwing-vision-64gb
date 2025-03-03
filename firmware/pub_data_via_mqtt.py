import paho.mqtt.client as mqtt
import json
import time


class MQTTClient:
    def __init__(self, broker, port, topic, client_id, username=None, password=None, qos=1, keepalive=60):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.keepalive = keepalive
        self.client_id = client_id
        self.qos = qos
        self.username = username
        self.password = password
        self.client = mqtt.Client(client_id=self.client_id)

        # Set credentials if provided
        if username and password:
            self.client.username_pw_set(username, password)

        # Attach callback functions
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected from MQTT Broker with return code {rc}")

    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()  # Start a separate thread to handle communication

    def disconnect(self):
        self.client.loop_stop()  # Stop the loop thread
        self.client.disconnect()

    def publish(self, payload):
        try:
            result = self.client.publish(self.topic, payload, qos=self.qos)
            status = result[0]
            print(result, status)
            if status == mqtt.MQTT_ERR_SUCCESS:
                print(f"Message sent to topic {self.topic}")
                return 1
            else:
                print(f"Failed to send message to topic {self.topic}")
                return 0
        except Exception as e:
            print(f"Error while publishing: {e}")
            return 0


# if __name__ == "__main__":
#     # Configuration
#     BROKER = "iothub-demo.fogwing.net"  # Replace with your MQTT broker
#     PORT = 1883
#     TOPIC = "fwent/edge/09f7c73d0ef755ac/inbound"
#     CLIENT_ID = "3351-3522-2019-6892"
#     USERNAME = "09f7c73d0ef755ac"  # Replace with your username if needed
#     PASSWORD = "Qsclqjdr9@"  # Replace with your password if needed
#
#     mqtt_client = MQTTClient(broker=BROKER, port=PORT, topic=TOPIC, client_id=CLIENT_ID, username=USERNAME,
#                              password=PASSWORD)
#
#     try:
#         mqtt_client.connect()
#         mqtt_client.publish(payload)
#         time.sleep(1)  # Delay between messages
#
#     except KeyboardInterrupt:
#         print("Interrupted by user")
#
#     finally:
#         mqtt_client.disconnect()
