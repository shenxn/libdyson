"""Mocked paho-mqtt client."""

import json
from typing import Optional

import paho.mqtt.client as mqtt

from libdyson.utils import mqtt_time


class MockedMQTT:
    """Mocked paho-mqtt client."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        command_topic: str,
        status_topic: str,
        status: dict,
        environmental_data: Optional[dict] = None,
    ) -> None:
        """Initialize the client with expected values."""
        self._expected_host = host
        self._expected_username = username
        self._expected_password = password
        self._command_topic = command_topic
        self._status_topic = status_topic
        self._status = status
        self._environmental_data = environmental_data

    def refersh(self, protocol: str):
        """Refresh client state."""
        self._protocol = protocol
        self._username = None
        self._password = None

        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None

        self._subscribed = False
        self.connected = False
        self.commands = []
        self.loop_started = False

        return self

    def username_pw_set(self, username: str, password: str) -> None:
        """Set username and password."""
        self._username = username
        self._password = password

    def connect_async(self, host: str) -> None:
        """Connect to the server asynchronously."""
        if host != self._expected_host:
            return
        if (
            self._username == self._expected_username
            and self._password == self._expected_password
        ):
            self.connected = True
            self.on_connect(self, None, None, 0)
        else:
            self.on_connect(self, None, None, 4)
            self.on_disconnect(self, None, 5)

    def disconnect(self) -> None:
        """Disconnect from the server."""
        self.connected = False
        self.on_disconnect(self, None, 0)

    def loop_start(self) -> None:
        """Start loop."""
        self.loop_started = True

    def loop_stop(self) -> None:
        """Stop loop."""
        self.loop_started = False

    def subscribe(self, topic: str) -> None:
        """Subscribe to a topic."""
        assert topic == self._status_topic
        self._subscribed = True

    def publish(self, topic: str, payload: str, qos: int = 0) -> None:
        """Publish to a topic."""
        assert topic == self._command_topic
        assert self._subscribed
        payload = json.loads(payload)
        message_type = payload["msg"]
        if message_type == "REQUEST-CURRENT-STATE":
            data = {"msg": "CURRENT-STATE"}
            data.update(self._status)
        elif message_type == "REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA":
            data = {"msg": "ENVIRONMENTAL-CURRENT-SENSOR-DATA"}
            data.update(self._environmental_data)
        else:
            self.commands.append(payload)
            return

        message = mqtt.MQTTMessage(topic=self._status_topic.encode("utf-8"))
        data["time"] = mqtt_time()
        message.payload = json.dumps(data).encode("utf-8")
        self.on_message(self, None, message)

    def state_change(self, new_status) -> None:
        """Trigger a state change."""
        data = {
            "msg": "STATE-CHANGE",
            "time": mqtt_time(),
        }
        data.update(new_status)
        message = mqtt.MQTTMessage(topic=self._status_topic.encode("utf-8"))
        message.payload = json.dumps(data).encode("utf-8")
        self.on_message(self, None, message)
