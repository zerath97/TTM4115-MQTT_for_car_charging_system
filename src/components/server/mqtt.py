import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
CHARGER_TOPIC = "ttm4115/g11/chargers"

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, msg):
        return # Server does not subscribe to any topics

    
    def send_start_charging_to_charger(self, charger_id: int, car_id: str, battery_target: int, max_charging_time: int):
        payload = {
            "command": "start_charging",
            "car_id": car_id,
            "battery_target": battery_target,
            "max_charging_time": max_charging_time,
        }
        payload = json.dumps(payload)

        self.client.publish(f"{CHARGER_TOPIC}/{charger_id}", payload)


    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()
    

    def stop(self):
        self.client.disconnect()

    
        