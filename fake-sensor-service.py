import json
import random
import signal
import sys
import time

import paho.mqtt.client as mqtt

MQTT_HOST: str = "mosquitto"
MQTT_PORT: int = 1883
API_KEY: str = "tOiOdxFTpZwezrrpCT"
SENSOR_READ_INTERVAL: float = 15

# checking for program arguments specifying sensor read interval
if len(sys.argv) > 1:
    try:
        SENSOR_READ_INTERVAL = int(sys.argv[1])
    except ValueError:
        SENSOR_READ_INTERVAL = float(sys.argv[1])


def get_topic(device_id):
    return "/" + API_KEY + "/" + device_id + "/attrs"


def publish_value(_mqtt_client, device_id, value: dict):
    print("Publishing value '" + str(json.dumps(value)) + "' for device " + device_id)
    _mqtt_client.publish(get_topic(device_id), json.dumps(value))


def get_text_from_sensor_value(value):
    if value == 1:
        return "not_sufficient"
    else:
        return "sufficient"


class Program:
    _running = True
    _mqtt_client = None

    def __init__(self):
        self._mqtt_client = mqtt.Client()

    def run(self):
        print("Running...")
        while True:
            print("Connecting to MQTT at " + MQTT_HOST + ":" + str(MQTT_PORT))
            self._mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

            print("Activating fake sensors")
            time.sleep(1)

            value = random.randint(0, 1)
            publish_value(self._mqtt_client, "soil-moisture01", {"s": get_text_from_sensor_value(value)})

            time.sleep(0.5)

            value = random.randint(0, 1)
            publish_value(self._mqtt_client, "soil-moisture02", {"s": get_text_from_sensor_value(value)})

            time.sleep(0.5)

            print("Deactivating fake sensors")

            print("Disconnecting from MQTT")
            self._mqtt_client.disconnect()

            seconds_asleep = 0
            while seconds_asleep < SENSOR_READ_INTERVAL * 60:
                seconds_asleep += 1
                time.sleep(1)
                if not self._running:
                    print("Sleep interrupted")
                    return

    def stop(self):
        self._running = False


# main
program = Program()


def sigterm_handler(_signo, _stack_frame):
    print("\nGot signal " + str(_signo))
    program.stop()


print("Registering signal handler")
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

print("Reading sensor values every " + str(SENSOR_READ_INTERVAL) + " minutes")

program.run()

del program

print("[end of program]")
