"""Tests for Dyson Pure Cool Link fan."""

import pytest

from libdyson import DEVICE_TYPE_PURE_COOL_LINK_DESK
from libdyson.const import ENVIRONMENTAL_INIT, AirQualityTarget
from libdyson.dyson_pure_cool_link import DysonPureCoolLink

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command

DEVICE_TYPE = DEVICE_TYPE_PURE_COOL_LINK_DESK

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


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Cool Link."""
    device = DysonPureCoolLink(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Status
    assert device.is_on is False
    assert device.auto_mode is False
    assert device.oscillation is False
    assert device.air_quality_target == AirQualityTarget.DEFAULT
    assert device.filter_life == 1500

    # Environmental
    assert device.particulates == 3
    assert device.volatile_organic_compounds == 4

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
            "ercd": ["NONE", "NONE"],
            "nmod": ["OFF", "ON"],
            "wacd": ["NONE", "NONE"],
        },
        "scheduler": {"srsc": "8773", "dstv": "0000", "tzid": "0001"},
    }
    mqtt_client.state_change(new_status)
    assert device.is_on is True
    assert device.auto_mode is True
    assert device.oscillation is True
    assert device.air_quality_target == AirQualityTarget.VERY_SENSITIVE
    assert device.filter_life == 1450

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
    assert device.particulates == 5
    assert device.volatile_organic_compounds == ENVIRONMENTAL_INIT


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("turn_on", [], {"fmod": "FAN"}),
        ("turn_off", [], {"fmod": "OFF"}),
        ("set_speed", [3], {"fmod": "FAN", "fnsp": "0003"}),
        ("enable_auto_mode", [], {"fmod": "AUTO"}),
        ("disable_auto_mode", [], {"fmod": "FAN"}),
        ("enable_oscillation", [], {"oson": "ON"}),
        ("disable_oscillation", [], {"oson": "OFF"}),
        ("enable_continuous_monitoring", [], {"fmod": "OFF", "rhtm": "ON"}),
        ("disable_continuous_monitoring", [], {"fmod": "OFF", "rhtm": "OFF"}),
        ("set_air_quality_target", [AirQualityTarget.SENSITIVE], {"qtar": "0003"}),
    ],
)
def test_command(
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of Pure Cool Link."""
    assert_command(
        DysonPureCoolLink(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )
