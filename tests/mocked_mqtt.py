"""Mocked paho-mqtt client."""

import json

import paho.mqtt.client as mqtt


def get_mocked_mqtt(
    host: str,
    username: str,
    password: str,
    command_topic: str,
    status_topic: str,
    status: dict,
):
    """Return mocked mqtt client."""

    class _MockedMQTT:

        instance = None

        def __init__(self, protocol: str) -> None:
            self._protocol = protocol
            self._username = None
            self._password = None
            self._host = None

            self.on_connect = None
            self.on_disconnect = None
            self.on_message = None

            self._subscribed = False
            self.commands = []
            _MockedMQTT.instance = self

        def username_pw_set(self, username: str, password: str) -> None:
            self._username = username
            self._password = password

        def connect_async(self, host: str) -> None:
            self._host = host

        def disconnect(self) -> None:
            self.on_disconnect(self, None, 0)

        def loop_start(self) -> None:
            if self._host != host:
                return
            if self._username == username and self._password == password:
                self.on_connect(self, None, None, 0)
            else:
                self.on_connect(self, None, None, 4)
                self.on_disconnect(self, None, 5)

        def loop_stop(self) -> None:
            pass

        def subscribe(self, topic: str) -> None:
            assert topic == status_topic
            self._subscribed = True

        def publish(self, topic: str, payload: str) -> None:
            assert topic == command_topic
            assert self._subscribed
            payload = json.loads(payload)
            message_type = payload["msg"]
            if message_type == "REQUEST-CURRENT-STATE":
                data = {"msg": "CURRENT-STATE"}
                data.update(status)
            else:
                self.commands.append(payload)
                return

            message = mqtt.MQTTMessage(topic=status_topic.encode("utf-8"))
            message.payload = json.dumps(data).encode("utf-8")
            self.on_message(self, None, message)

        def state_change(self, new_status) -> None:
            data = {"msg": "STATE-CHANGE"}
            data.update(new_status)
            message = mqtt.MQTTMessage(topic=status_topic.encode("utf-8"))
            message.payload = json.dumps(data).encode("utf-8")
            self.on_message(self, None, message)

    return _MockedMQTT
