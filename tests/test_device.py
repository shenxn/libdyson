"""Test DysonDevice functionalities."""
from unittest.mock import MagicMock, patch

import pytest

from libdyson.const import MessageType
from libdyson.dyson_device import DysonDevice
from libdyson.exceptions import (
    DysonConnectionRefused,
    DysonConnectTimeout,
    DysonInvalidCredential,
    DysonNotConnected,
)

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

DEVICE_TYPE = "device_type"

STATUS = {
    "key1": "V1",
    "key2": "V2",
}


class _TestDevice(DysonDevice):
    def __init__(self, serial: str, credential: str):
        """Initialize the device."""
        super().__init__(serial, credential)

    @property
    def device_type(self) -> str:
        return DEVICE_TYPE

    @property
    def _status_topic(self) -> str:
        return f"{DEVICE_TYPE}/{self._serial}/status"

    def _update_status(self, payload: dict) -> None:
        payload.pop("msg")
        payload.pop("time")
        self._status = payload


@pytest.fixture(autouse=True)
def mqtt_client() -> MockedMQTT:
    """Return mocked mqtt client."""
    mocked_mqtt = MockedMQTT(
        HOST,
        SERIAL,
        CREDENTIAL,
        f"{DEVICE_TYPE}/{SERIAL}/command",
        f"{DEVICE_TYPE}/{SERIAL}/status",
        STATUS,
    )
    with patch("libdyson.dyson_device.mqtt.Client", mocked_mqtt.refersh), patch(
        "libdyson.dyson_device.TIMEOUT", 0
    ):
        yield mocked_mqtt


def test_properties():
    """Test device properties."""
    device = _TestDevice(SERIAL, CREDENTIAL)
    assert device.serial == SERIAL
    assert device.is_connected is False
    assert device.device_type == DEVICE_TYPE


def test_connect(mqtt_client: MockedMQTT):
    """Test successful connection."""
    device = _TestDevice(SERIAL, CREDENTIAL)
    device.connect(HOST)
    assert device.is_connected is True
    assert mqtt_client.connected is True
    assert mqtt_client.loop_started is True


def test_invalid_credential(mqtt_client: MockedMQTT):
    """Test invalid credential."""
    device = _TestDevice(SERIAL, "invalid")
    with pytest.raises(DysonInvalidCredential):
        device.connect(HOST)
    assert device.is_connected is False
    assert mqtt_client.loop_started is False


def test_connect_timeout(mqtt_client: MockedMQTT):
    """Test connection timed out."""
    device = _TestDevice(SERIAL, CREDENTIAL)
    with pytest.raises(DysonConnectTimeout):
        device.connect("192.168.1.5")
    assert device.is_connected is False
    assert mqtt_client.loop_started is False


def test_connect_status_timeout(mqtt_client: MockedMQTT):
    """Test first data timed out."""

    def _publish(topic: str, payload: str) -> None:
        pass  # Do nothing in publish so CURRENT-STATUS never sent

    mqtt_client.publish = _publish
    device = _TestDevice(SERIAL, CREDENTIAL)
    with pytest.raises(DysonConnectTimeout):
        device.connect(HOST)
    assert device.is_connected is False
    assert mqtt_client.connected is False
    assert mqtt_client.loop_started is False


def test_connection_refused(mqtt_client: MockedMQTT):
    """Test connection refused."""

    def _connect_async(host: str) -> None:
        mqtt_client.on_connect(mqtt_client, None, None, 2)
        mqtt_client.on_disconnect(mqtt_client, None, 3)

    mqtt_client.connect_async = _connect_async
    device = _TestDevice(SERIAL, CREDENTIAL)
    with pytest.raises(DysonConnectionRefused):
        device.connect(HOST)
    assert device.is_connected is False
    assert mqtt_client.connected is False
    assert mqtt_client.loop_started is False


def test_disconnect(mqtt_client: MockedMQTT):
    """Test successful disconnect."""
    device = _TestDevice(SERIAL, CREDENTIAL)
    device.connect(HOST)
    device.disconnect()
    assert device.is_connected is False
    assert mqtt_client.connected is False
    assert mqtt_client.loop_started is False


def test_disconnect_timeout(mqtt_client: MockedMQTT):
    """Test disconnection timed out."""

    def _disconnect():
        pass  # Do nothing so on_disconnect never called

    mqtt_client.disconnect = _disconnect
    device = _TestDevice(SERIAL, CREDENTIAL)
    device.connect(HOST)
    device.disconnect()
    assert device.is_connected is False
    assert mqtt_client.loop_started is False


def test_not_connected():
    """Test send commands without connection."""
    device = _TestDevice(SERIAL, CREDENTIAL)
    with pytest.raises(DysonNotConnected):
        device.request_current_status()
    assert device._status is None
    with pytest.raises(DysonNotConnected):
        device._send_command("COMMAND")


def test_status_update(mqtt_client: MockedMQTT):
    """Test status update."""
    device = _TestDevice(SERIAL, CREDENTIAL)
    callback = MagicMock()
    device.add_message_listener(callback)
    device.connect(HOST)

    # Data updated
    assert device._status == STATUS
    callback.assert_called_once_with(MessageType.STATE)
    callback.reset_mock()

    new_status = {
        "key1": "V2",
        "key2": "V1",
    }
    mqtt_client.state_change(new_status)
    assert device._status == new_status
    callback.assert_called_once_with(MessageType.STATE)
    callback.reset_mock()

    # Remove callback
    device.remove_message_listener(callback)
    mqtt_client.state_change(new_status)
    callback.assert_not_called()
