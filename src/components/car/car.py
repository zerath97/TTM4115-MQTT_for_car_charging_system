from stmpy import Machine, Driver

import paho.mqtt.client as mqtt
import stmpy
import json
import logging

# Configure the MQTT settings 
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

# Server settings
CAR_TOPIC = "ttm4115/g11/cars"
CHARGER_TOPIC = "ttm4115/g11/chargers"

logger = logging.getLogger("car_logger")

class BatteryLogic:
    def __init__(self, car_id, component):
        self.car_id = car_id
        self.percentage = 10 # Assuming the battery is at 10 percent
        self.charger_id = None
        self.component: BatteryComponent = component
        self.mqtt_client = self.component.mqtt_client

        # Transitions
        transitions = [
            {"source": "initial", "target": "idle"},
            {"source": "idle", "target": "charging", "trigger": "start_charging", "effect": "on_charging"},
            {"source": "charging", "target": "charging", "trigger": "update_timer", "effect": "on_charging_update"},
            {"source": "charging", "target": "idle", "trigger": "finish_charging", "effect": "on_finish_charging"}
        ]

        # States
        states = [
            {"name": "charging", "entry": "start_timer('update_timer', 500)"}
        ]

        # State machine
        self.stm = stmpy.Machine(
            name=car_id, 
            transitions=transitions, 
            states=states,
            obj=self
        )


    def init_stm(self):
        logger.info("Car state machine initialized")


    def on_charging(self):
        logger.debug("Car moved from state idle -> charging. Charging has started.")


    def on_charging_update(self):
        if self.percentage < 99: # prevent going over 100% because its not possible
            self.percentage += 2
        logger.info(f"Charging percentage updated to {self.percentage}.")

        # Send battery percentage to charger
        topic = f"{CHARGER_TOPIC}/{self.charger_id}"
        payload = {"command": "battery_update", "percentage": self.percentage}
        payload = json.dumps(payload)
        self.mqtt_client.publish(topic, payload)
        logger.debug(f"Sent battery update to topic '{topic}' with payload {payload}")


    def on_finish_charging(self):
        logger.debug(f"Car moved from state charging -> idle. Charging has finished with battery_percentage={self.percentage}%")


class BatteryComponent:
    def __init__(self, car_id):
        # mqtt definitions
        self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(f"{CAR_TOPIC}/{car_id}")
        self.mqtt_client.loop_start()

        # stm definitions
        self.battery = BatteryLogic(car_id, self)

        # driver
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self.stm_driver.add_machine(self.battery.stm)

        # other variables
        self.charger_id = None


    def on_message(self, client, userdata, msg):
        logger.debug(f"MQTT Client recieved a message in topic '{msg.topic}': {msg.payload}")
        msg = json.loads(msg.payload)  # now a dict

        command = msg.get("command")

        if command == "start_charging":
            charger_id = msg.get("charger_id")
            self.battery.charger_id = charger_id
            self.battery.stm.send("start_charging")
            
        elif command == "stop_charging":
            self.battery.stm.send("finish_charging")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.debug(f"Client connected to broker {MQTT_BROKER}:{MQTT_PORT}.")
        else:
            logger.debug(f"Broker {MQTT_BROKER}:{MQTT_PORT} refused connection")
