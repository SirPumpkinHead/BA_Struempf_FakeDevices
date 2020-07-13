import json
import signal
import time

import paho.mqtt.client as mqtt

MQTT_HOST: str = "mosquitto"
MQTT_PORT: int = 1883
API_KEY: str = "tOiOdxFTpZwezrrpCT"
VALVE_ID: str = "valve01"


def get_topic(device_id):
    return "/" + API_KEY + "/" + device_id + "/cmd"

    # The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    print("Subscribing to topic " + get_topic(VALVE_ID))
    client.subscribe(get_topic(VALVE_ID))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Payload " + str(msg.payload))

    command: dict = json.loads(msg.payload)

    if "open" in command:
        print("Opening fake valve")

    elif "close" in command:
        print("Closing fake valve")

    else:
        print("Unknown command")


class Program:
    _running = True
    _mqtt_client = None

    def __init__(self):
        print("Setting up mqtt client for " + MQTT_HOST + ":" + str(MQTT_PORT))
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = on_connect
        self._mqtt_client.on_message = on_message

    def run(self):
        print("Connecting to MQTT at " + MQTT_HOST + ":" + str(MQTT_PORT))
        self._mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

        while self._running:
            self._mqtt_client.loop()
            time.sleep(1)

        print("Disconnecting from MQTT")
        self._mqtt_client.disconnect()

    def stop(self):
        self._running = False

    def __del__(self):
        del self._mqtt_client


program = Program()


def sigterm_handler(_signo, _stack_frame):
    print("\nGot signal " + str(_signo))
    program.stop()


signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

program.run()

print("[end of program]")
