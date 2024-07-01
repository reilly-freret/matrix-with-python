import paho.mqtt
from apps.App import App
import paho.mqtt.client as paho
from paho import mqtt
from PIL import Image
from utils.logging import get_logger
logger = get_logger(__name__)


class MessageApp(App):

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
        client.subscribe("testTopic")

    def on_message(self, client, userdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        self.message = msg.payload.decode("utf-8")

    def __init__(self, image_setter, data_refresh_rate=10, render_refresh_rate=1) -> None:
        super().__init__(image_setter, data_refresh_rate, render_refresh_rate)
        self.message = "none received"
        self.mqttc = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.mqttc.on_connect = lambda client, userdata, flags, reason_code, properties: self.on_connect(client, userdata, flags, reason_code, properties)
        self.mqttc.on_message = lambda client, userdata, msg: self.on_message(client, userdata, msg)
        self.mqttc.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        self.mqttc.username_pw_set("rf_test", "Test1234")
        self.mqttc.connect("d7ad67d5cbb14999894675743d50e0e6.s1.eu.hivemq.cloud", 8883, 60)
        self.mqttc.loop_start()

    def __data_update__(self):
        pass

    def __render_update__(self):
        canvas = Image.new("RGB", (64, 32), (0, 0, 0))
        self.__draw_text__(canvas, (0, 0), self.message)
        self.__image_setter__(canvas)

    def stop(self):
        super().stop()
        self.mqttc.loop_stop()
