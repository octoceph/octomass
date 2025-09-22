"""
MQTT sensor ingestion — подпись на топики и вызов callback.

Этот модуль полезен для интеграции с IoT-датчиками в теплицах/агро.
"""
import paho.mqtt.client as mqtt
from loguru import logger
from typing import Callable, Any
import threading
import json

class MqttSensor:
    def __init__(self, broker_url: str, broker_port: int = 1883, client_id: str = "octocore-mqtt"):
        """Инициализация MQTT клиента. Не запускаем loop автоматически."""
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._callback: Callable[[str, dict], Any] = lambda t, p: None
        self._connected = False
        self.broker = broker_url
        self.port = broker_port

    def _on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT connected rc={}", rc)
        self._connected = True

    def _on_message(self, client, userdata, msg):
        payload = None
        try:
            payload = json.loads(msg.payload.decode())
        except Exception:
            payload = {"raw": msg.payload.decode(errors='ignore')}
        logger.debug("MQTT message on {}: {}", msg.topic, payload)
        self._callback(msg.topic, payload)

    def start(self, topics: list, callback: Callable[[str, dict], Any]):
        """Подписываемся на список топиков и запускаем loop в отдельном потоке."""
        self._callback = callback
        self.client.connect(self.broker, self.port)
        for t in topics:
            self.client.subscribe(t)
        thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        thread.start()
