"""Dyson device."""
from abc import abstractmethod
from enum import Enum
from typing import Any, List, Optional
import json
from libdyson.exceptions import DysonConnectTimeout, DysonNotConnected
import logging
import threading
import time
import paho.mqtt.client as mqtt

_LOGGER = logging.getLogger(__name__)


class DysonDevice():
    """Base class for dyson devices."""

    def __init__(self, serial: str, credentials: str):
        self._serial = serial
        self._credentials = credentials
        self._mqtt_client = None
        self._connected = threading.Event()
        self._disconnected = threading.Event()
        self._state_data_available = threading.Event()
        self._callbacks = []

    @property
    @abstractmethod
    def _device_type(self) -> str:
        """Device type."""

    @property
    def _status_topic(self) -> str:
        """MQTT status topic."""
        return f"{self._device_type}/{self._serial}/status"

    @property
    def _command_topic(self) -> str:
        """MQTT command topic."""
        return f"{self._device_type}/{self._serial}/command"

    @property
    @abstractmethod
    def _state_types(self) -> List[str]:
        """MQTT message types that represents a state message."""

    def connect(self, host: str) -> None:
        self._disconnected.clear()
        self._mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
        self._mqtt_client.username_pw_set(self._serial, self._credentials)
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_message = self._on_message
        self._mqtt_client.connect_async(host)
        self._mqtt_client.loop_start()
        if self._connected.wait(timeout=10):
            _LOGGER.info("Connected to device %s", self._serial)
            self.request_current_state()

            # Wait for first data
            if self._state_data_available.wait(timeout=10):
                return

        self._mqtt_client.loop_stop()
        raise DysonConnectTimeout

    def disconnect(self) -> None:
        self._connected.clear()
        self._mqtt_client.disconnect()
        if not self._disconnected.wait(timeout=10):
            _LOGGER.warning("Disconnect timed out")
        self._mqtt_client.loop_stop()

    def register_callback(self, callback) -> None:
        self._callbacks.append(callback)

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags, rc):
        # TODO: error handling
        client.subscribe(self._status_topic)
        _LOGGER.info(f"Connected with result code {str(rc)}")
        self._connected.set()

    def _on_disconnect(self, client, userdata, rc):
        _LOGGER.info(f"Disconnected with result code {str(rc)}")
        self._disconnected.set()

    def _on_message(self, client, userdata: Any, msg: mqtt.MQTTMessage):
        print(f"{msg.topic} {str(msg.payload)}")
        _LOGGER.debug(f"{msg.topic} {str(msg.payload)}")
        payload = json.loads(msg.payload.decode("utf-8"))
        if payload["msg"] in ["CURRENT-STATE", "STATE-CHANGE"]:
            self._update_state(payload)
            if not self._state_data_available.is_set():
                self._state_data_available.set()
            for callback in self._callbacks:
                callback()

    @abstractmethod
    def _update_state(self, data: dict) -> None:
        """Update the device state."""

    def _set_enum_attr(self, value: str, attr: str, enum: Enum) -> None:
        """Helper function to update state based on enum."""
        try:
            setattr(self, f"_{attr}", enum(value))
        except ValueError:
            _LOGGER.error("Unknown %s value %s", attr, value)

    def _send_command(self, command: str, data: Optional[dict]=None):
        if not self._connected.is_set():
            raise DysonNotConnected
        if data is None:
            data = {}
        payload = {
            "msg": command,
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        payload.update(data)
        self._mqtt_client.publish(self._command_topic, json.dumps(payload))

    def request_current_state(self):
        """Request new state message."""
        if not self._connected.is_set():
            raise DysonNotConnected
        payload = {
            "msg": "REQUEST-CURRENT-STATE",
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self._mqtt_client.publish(self._command_topic, json.dumps(payload))
