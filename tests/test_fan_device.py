"""Tests for DysonFanDevice."""

import json
from unittest.mock import MagicMock

import pytest

from libdyson.const import (
    DEVICE_TYPE_PURE_COOL_LINK_DESK,
    ENVIRONMENTAL_OFF,
    MessageType,
)
from libdyson.dyson_device import DysonFanDevice
from libdyson.exceptions import DysonConnectTimeout, DysonNotConnected

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

DEVICE_TYPE = DEVICE_TYPE_PURE_COOL_LINK_DESK

STATUS = {
    "mode-reason": "RAPP",
    "state-reason": "MODE",
    "dial": "OFF",
    "rssi": "-29",
    "product-state": {
        "fnst": "OFF",
        "fnsp": "0001",
        "rhtm": "OFF",
        "ercd": "NONE",
        "nmod": "OFF",
        "wacd": "NONE",
    },
    "scheduler": {"srsc": "8773", "dstv": "0000", "tzid": "0001"},
}

ENVIRONMENTAL_DATA = {
    "data": {
        "tact": "OFF",
        "hact": "OFF",
        "sltm": "OFF",
    }
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of fan device."""
    device = DysonFanDevice(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Status
    assert device.device_type == DEVICE_TYPE
    assert device.fan_state is False
    assert device.speed == 1
    assert device.night_mode is False
    assert device.continuous_monitoring is False
    assert device.error_code == "NONE"
    assert device.warning_code == "NONE"

    # Environmental
    assert device.humidity == ENVIRONMENTAL_OFF
    assert device.temperature == ENVIRONMENTAL_OFF
    assert device.sleep_timer == ENVIRONMENTAL_OFF

    error_code = "0X03"  # Just mock data
    warning_code = "0X01"  # Just mock data
    new_status = {
        "mode-reason": "LAPP",
        "state-reason": "MODE",
        "product-state": {
            "fnst": ["OFF", "FAN"],
            "fnsp": ["0001", "AUTO"],
            "rhtm": ["OFF", "ON"],
            "ercd": ["NONE", error_code],
            "nmod": ["OFF", "ON"],
            "wacd": ["NONE", warning_code],
        },
        "scheduler": {"srsc": "8773", "dstv": "0000", "tzid": "0001"},
    }
    mqtt_client.state_change(new_status)
    assert device.fan_state is True
    assert device.speed is None
    assert device.night_mode is True
    assert device.continuous_monitoring is True
    assert device.error_code == error_code
    assert device.warning_code == warning_code

    mqtt_client._environmental_data = {
        "data": {
            "tact": "2903",
            "hact": "0030",
            "sltm": "0003",
        }
    }
    device.request_environmental_data()
    assert device.humidity == 30
    assert device.temperature == 290.3
    assert device.sleep_timer == 3


def assert_command(
    device: DysonFanDevice,
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of fan device."""
    device.connect(HOST)
    func = getattr(device, command)
    func(*command_args)
    assert len(mqtt_client.commands) == 1
    payload = mqtt_client.commands[0]
    assert payload["msg"] == "STATE-SET"
    assert payload["data"] == msg_data


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("enable_night_mode", [], {"nmod": "ON"}),
        ("disable_night_mode", [], {"nmod": "OFF"}),
        ("set_sleep_timer", [15], {"sltm": "0015"}),
        ("disable_sleep_timer", [], {"sltm": "OFF"}),
        ("reset_filter", [], {"rstf": "RSTF"}),
    ],
)
def test_command(
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of fan device."""
    assert_command(
        DysonFanDevice(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )


@pytest.mark.parametrize(
    "command,command_args",
    [
        ("set_speed", [0]),
        ("set_speed", [11]),
        ("set_sleep_timer", [0]),
        ("set_sleep_timer", [600]),
    ],
)
def test_command_invalid_data(
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
):
    """Test commands with invalid data."""
    device = DysonFanDevice(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)
    func = getattr(device, command)
    with pytest.raises(ValueError):
        func(*command_args)
    assert len(mqtt_client.commands) == 0


def test_not_connected(mqtt_client: MockedMQTT):
    """Test making operations without connection."""
    device = DysonFanDevice(SERIAL, CREDENTIAL, DEVICE_TYPE)
    with pytest.raises(DysonNotConnected):
        device.enable_night_mode()
    with pytest.raises(DysonNotConnected):
        device.request_environmental_data()


def test_connect_environmental_timeout(mqtt_client: MockedMQTT):
    """Test environmental data timed out during connection."""
    original_publish = mqtt_client.publish

    def _publish(topic: str, payload: str) -> None:
        if (
            json.loads(payload)["msg"]
            == "REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA"
        ):
            return  # Do not publish environmental data request
        original_publish(topic, payload)

    mqtt_client.publish = _publish

    device = DysonFanDevice(SERIAL, CREDENTIAL, DEVICE_TYPE)
    with pytest.raises(DysonConnectTimeout):
        device.connect(HOST)
    assert device._status_data_available.is_set()
    assert device.is_connected is False
    assert mqtt_client.connected is False
    assert mqtt_client.loop_started is False


def test_environmental_callback(mqtt_client: MockedMQTT):
    """Test callback on environmental data."""
    device = DysonFanDevice(SERIAL, CREDENTIAL, DEVICE_TYPE)
    callback = MagicMock()
    device.add_message_listener(callback)
    device.connect(HOST)
    callback.assert_called_with(MessageType.ENVIRONMENTAL)
    callback.reset_mock()

    device.request_environmental_data()
    callback.assert_called_once_with(MessageType.ENVIRONMENTAL)
    callback.reset_mock()
