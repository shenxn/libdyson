"""Tests for Dyson Pure Humidity+Cool device."""

import pytest

from libdyson import (
    DEVICE_TYPE_PURE_HUMIDIFY_COOL,
    DysonPureHumidifyCool,
    HumidifyOscillationMode,
    WaterHardness,
)

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command
from .test_pure_cool_link import ENVIRONMENTAL_DATA  # noqa: F401

DEVICE_TYPE = DEVICE_TYPE_PURE_HUMIDIFY_COOL

STATUS = {
    "product-state": {
        "oson": "ON",
        "ancp": "BRZE",
        "hume": "HUMD",
        "haut": "ON",
        "humt": "0050",
        "rect": "0080",
        "wath": "2025",
        "cltr": "1853",
        "cdrr": "0060",
    }
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Hot+Cool Link."""
    device = DysonPureHumidifyCool(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    assert device.oscillation is True
    assert device.oscillation_mode == HumidifyOscillationMode.BREEZE
    assert device.humidification is True
    assert device.humidification_auto_mode is True
    assert device.target_humidity == 50
    assert device.auto_target_humidity == 80
    assert device.water_hardness == WaterHardness.SOFT
    assert device.time_until_next_clean == 1853
    assert device.clean_time_remaining == 60

    new_status = {
        "product-state": {
            "oson": ["ON", "OFF"],
            "ancp": ["BRZE", "0045"],
            "hume": ["HUMD", "OFF"],
            "haut": ["ON", "OFF"],
            "humt": ["0050", "0030"],
            "rect": ["0080", "0050"],
            "wath": ["2025", "0675"],
            "cltr": ["1853", "1800"],
            "cdrr": ["0060", "0050"],
        }
    }
    mqtt_client.state_change(new_status)
    assert device.oscillation is False
    assert device.oscillation_mode == HumidifyOscillationMode.DEGREE_45
    assert device.humidification is False
    assert device.humidification_auto_mode is False
    assert device.target_humidity == 30
    assert device.auto_target_humidity == 50
    assert device.water_hardness == WaterHardness.HARD
    assert device.time_until_next_clean == 1800
    assert device.clean_time_remaining == 50


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("enable_oscillation", [], {"oson": "ON", "fpwr": "ON", "ancp": "BRZE"}),
        (
            "enable_oscillation",
            [HumidifyOscillationMode.DEGREE_45],
            {"oson": "ON", "fpwr": "ON", "ancp": "0045"},
        ),
        (
            "enable_oscillation",
            [HumidifyOscillationMode.DEGREE_90],
            {"oson": "ON", "fpwr": "ON", "ancp": "0090"},
        ),
        (
            "enable_oscillation",
            [HumidifyOscillationMode.BREEZE],
            {"oson": "ON", "fpwr": "ON", "ancp": "BRZE"},
        ),
        ("disable_oscillation", [], {"oson": "OFF"}),
        ("enable_humidification", [], {"hume": "HUMD"}),
        ("disable_humidification", [], {"hume": "OFF"}),
        ("enable_humidification_auto_mode", [], {"haut": "ON"}),
        ("disable_humidification_auto_mode", [], {"haut": "OFF"}),
        ("set_target_humidity", [50], {"humt": "0050", "haut": "OFF"}),
        ("set_water_hardness", [WaterHardness.SOFT], {"wath": "2025"}),
        ("set_water_hardness", [WaterHardness.MEDIUM], {"wath": "1350"}),
        ("set_water_hardness", [WaterHardness.HARD], {"wath": "0675"}),
    ],
)
def test_command(
    mqtt_client: MockedMQTT,
    command: str,
    command_args: list,
    msg_data: dict,
):
    """Test commands of Pure Hot+Cool Link."""
    assert_command(
        DysonPureHumidifyCool(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )
