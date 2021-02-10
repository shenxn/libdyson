"""Tests for Dyson Pure Cool Link fan."""
import json
from unittest.mock import MagicMock, patch

import pytest

from libdyson import DEVICE_TYPE_PURE_COOL_LINK_DESK, DEVICE_TYPE_PURE_COOL_LINK_TOWER
from libdyson.const import (
    ENVIRONMENTAL_INIT,
    ENVIRONMENTAL_OFF,
    AirQualityTarget,
    FanMode,
    FanSpeed,
    MessageType,
)
from libdyson.dyson_pure_cool_link import DysonPureCoolLink
from libdyson.exceptions import DysonConnectTimeout, DysonNotConnected

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

STATUS = {
    "mode-reason": "RAPP",
    "state-reason": "MODE",
    "dial": "OFF",
    "rssi": "-29",
    "product-state": {
        "fmod": "OFF",
        "fnst": "OFF",
        "fnsp": "0001",
        "qtar": "0002",
        "oson": "OFF",
        "rhtm": "OFF",
        "filf": "1500",
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
        "pact": "0003",
        "vact": "0004",
        "sltm": "OFF",
    }
}


@pytest.fixture(
    params=[DEVICE_TYPE_PURE_COOL_LINK_DESK, DEVICE_TYPE_PURE_COOL_LINK_TOWER]
)
def device_type(request) -> str:
    """Return device type."""
    return request.param


@pytest.fixture(autouse=True)
def mqtt_client(device_type) -> MockedMQTT:
    """Return mocked mqtt client."""
    mocked_mqtt = MockedMQTT(
        HOST,
        SERIAL,
        CREDENTIAL,
        f"{device_type}/{SERIAL}/command",
        f"{device_type}/{SERIAL}/status/current",
        STATUS,
        ENVIRONMENTAL_DATA,
    )
    with patch("libdyson.dyson_device.mqtt.Client", mocked_mqtt.refersh), patch(
        "libdyson.dyson_device.TIMEOUT", 0
    ), patch("libdyson.dyson_pure_cool_link.TIMEOUT", 0):
        yield mocked_mqtt


def test_properties(device_type: str, mqtt_client: MockedMQTT):
    """Test properties of Pure Cool Link."""
    device = DysonPureCoolLink(SERIAL, CREDENTIAL, device_type)
    device.connect(HOST)

    # Status
    assert device.device_type == device_type
    assert device.fan_mode == FanMode.OFF
    assert device.is_on is False
    assert device.speed == FanSpeed.SPEED_1
    assert device.auto_mode is False
    assert device.oscillation is False
    assert device.night_mode is False
    assert device.continuous_monitoring is False
    assert device.air_quality_target == AirQualityTarget.DEFAULT
    assert device.filter_life == 1500
    assert device.error_code == "NONE"
    assert device.warning_code == "NONE"

    # Environmental
    assert device.humidity == ENVIRONMENTAL_OFF
    assert device.temperature == ENVIRONMENTAL_OFF
    assert device.particulars == 3
    assert device.volatile_organic_compounds == 4
    assert device.sleep_timer == ENVIRONMENTAL_OFF

    error_code = "0X03"  # Just mock data
    warning_code = "0X01"  # Just mock data
    new_status = {
        "mode-reason": "LAPP",
        "state-reason": "MODE",
        "product-state": {
            "fmod": ["OFF", "AUTO"],
            "fnst": ["OFF", "FAN"],
            "fnsp": ["0001", "AUTO"],
            "qtar": ["0002", "0001"],
            "oson": ["OFF", "ON"],
            "rhtm": ["OFF", "ON"],
            "filf": ["1500", "1450"],
            "ercd": ["NONE", error_code],
            "nmod": ["OFF", "ON"],
            "wacd": ["NONE", warning_code],
        },
        "scheduler": {"srsc": "8773", "dstv": "0000", "tzid": "0001"},
    }
    mqtt_client.state_change(new_status)
    assert device.fan_mode == FanMode.AUTO
    assert device.is_on is True
    assert device.speed == FanSpeed.SPEED_AUTO
    assert device.auto_mode is True
    assert device.oscillation is True
    assert device.night_mode is True
    assert device.continuous_monitoring is True
    assert device.air_quality_target == AirQualityTarget.BETTER
    assert device.filter_life == 1450
    assert device.error_code == error_code
    assert device.warning_code == warning_code

    mqtt_client._environmental_data = {
        "data": {
            "tact": "2903",
            "hact": "0030",
            "pact": "0005",
            "vact": "INIT",
            "sltm": "0003",
        }
    }
    device.request_environmental_data()
    assert device.humidity == 30
    assert device.temperature == 290.3
    assert device.particulars == 5
    assert device.volatile_organic_compounds == ENVIRONMENTAL_INIT
    assert device.sleep_timer == 3


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("turn_on", [], {"fmod": "FAN"}),
        ("turn_off", [], {"fmod": "OFF"}),
        ("set_speed", [FanSpeed.SPEED_3], {"fmod": "FAN", "fnsp": "0003"}),
        ("set_speed", [FanSpeed.SPEED_AUTO], {"fmod": "AUTO"}),
        ("set_auto_mode", [True], {"fmod": "AUTO"}),
        ("set_auto_mode", [False], {"fmod": "FAN"}),
        ("set_oscillation", [True], {"oson": "ON"}),
        ("set_oscillation", [False], {"oson": "OFF"}),
        ("set_night_mode", [True], {"nmod": "ON"}),
        ("set_night_mode", [False], {"nmod": "OFF"}),
        ("set_continuous_monitoring", [True], {"fmod": "OFF", "rhtm": "ON"}),
        ("set_continuous_monitoring", [False], {"fmod": "OFF", "rhtm": "OFF"}),
        ("set_air_quality_target", [AirQualityTarget.HIGH], {"qtar": "0003"}),
        ("set_sleep_timer", [15], {"sltm": "0015"}),
        ("disable_sleep_timer", [], {"sltm": "OFF"}),
        ("reset_filter", [], {"rstf": "RSTF"}),
    ],
)
def test_command(
    device_type: str,
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of Pure Cool Link."""
    device = DysonPureCoolLink(SERIAL, CREDENTIAL, device_type)
    device.connect(HOST)
    func = getattr(device, command)
    func(*command_args)
    assert len(mqtt_client.commands) == 1
    payload = mqtt_client.commands[0]
    assert payload["msg"] == "STATE-SET"
    assert payload["data"] == msg_data


def test_invalid_sleep_timer(device_type: str, mqtt_client: MockedMQTT):
    """Test set sleep timer with invalid value."""
    device = DysonPureCoolLink(SERIAL, CREDENTIAL, device_type)
    device.connect(HOST)
    with pytest.raises(ValueError):
        device.set_sleep_timer(0)
    with pytest.raises(ValueError):
        device.set_sleep_timer(600)
    assert len(mqtt_client.commands) == 0


def test_not_connected(device_type: str):
    """Test making operations without connection."""
    device = DysonPureCoolLink(SERIAL, CREDENTIAL, device_type)
    with pytest.raises(DysonNotConnected):
        device.turn_on()
    with pytest.raises(DysonNotConnected):
        device.request_environmental_data()


def test_connect_environmental_timeout(device_type: str, mqtt_client: MockedMQTT):
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

    device = DysonPureCoolLink(SERIAL, CREDENTIAL, device_type)
    with pytest.raises(DysonConnectTimeout):
        device.connect(HOST)
    assert device._status_data_available.is_set()
    assert device.is_connected is False
    assert mqtt_client.connected is False
    assert mqtt_client.loop_started is False


def test_environmental_callback(device_type: str):
    """Test callback on environmental data."""
    device = DysonPureCoolLink(SERIAL, CREDENTIAL, device_type)
    callback = MagicMock()
    device.add_message_listener(callback)
    device.connect(HOST)
    callback.assert_called_with(MessageType.ENVIRONMENTAL)
    callback.reset_mock()

    device.request_environmental_data()
    callback.assert_called_once_with(MessageType.ENVIRONMENTAL)
    callback.reset_mock()
