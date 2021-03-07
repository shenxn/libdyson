"""Tests for Pure Cool."""

import pytest

from libdyson import DEVICE_TYPE_PURE_COOL
from libdyson.const import ENVIRONMENTAL_FAIL, ENVIRONMENTAL_INIT, ENVIRONMENTAL_OFF
from libdyson.dyson_pure_cool import DysonPureCool

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command

DEVICE_TYPE = DEVICE_TYPE_PURE_COOL

STATUS = {
    "mode-reason": "RAPP",
    "state-reason": "MODE",
    "dial": "OFF",
    "rssi": "-46",
    "channel": "1",
    "product-state": {
        "fpwr": "OFF",
        "fdir": "OFF",
        "auto": "OFF",
        "oscs": "OFF",
        "oson": "OIOF",
        "nmod": "OFF",
        "rhtm": "OFF",
        "fnst": "OFF",
        "ercd": "NONE",
        "wacd": "NONE",
        "nmdv": "0004",
        "fnsp": "AUTO",
        "bril": "0002",
        "corf": "ON",
        "cflr": "0100",
        "hflr": "0100",
        "sltm": "OFF",
        "osal": "0063",
        "osau": "0243",
        "ancp": "CUST",
    },
    "scheduler": {"srsc": "000000005b1792f0", "dstv": "0001", "tzid": "0001"},
}

ENVIRONMENTAL_DATA = {
    "data": {
        "tact": "OFF",
        "hact": "OFF",
        "pm25": "OFF",
        "pm10": "OFF",
        "va10": "INIT",
        "noxl": "FAIL",
        "p25r": "OFF",
        "p10r": "OFF",
        "sltm": "OFF",
    }
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Cool Link."""
    device = DysonPureCool(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Status
    assert device.is_on is False
    assert device.auto_mode is False
    assert device.oscillation is False
    assert device.oscillation_status is False
    assert device.oscillation_angle_low == 63
    assert device.oscillation_angle_high == 243
    assert device.front_airflow is False
    assert device.night_mode_speed == 4
    assert device.carbon_filter_life == 100
    assert device.hepa_filter_life == 100

    # Environmental
    assert device.particulate_matter_2_5 == ENVIRONMENTAL_OFF
    assert device.particulate_matter_10 == ENVIRONMENTAL_OFF
    assert device.volatile_organic_compounds == ENVIRONMENTAL_INIT
    assert device.nitrogen_dioxide == ENVIRONMENTAL_FAIL

    new_status = {
        "mode-reason": "LAPP",
        "state-reason": "MODE",
        "product-state": {
            "fpwr": ["OFF", "ON"],
            "fdir": ["OFF", "ON"],
            "auto": ["OFF", "ON"],
            "oscs": ["OFF", "ON"],
            "oson": ["OIOF", "OION"],
            "nmod": ["OFF", "ON"],
            "rhtm": ["OFF", "ON"],
            "fnst": ["OFF", "ON"],
            "ercd": ["NONE", "NONE"],
            "wacd": ["NONE", "NONE"],
            "nmdv": ["0004", "0010"],
            "fnsp": ["AUTO", "AUTO"],
            "bril": ["0002", "0002"],
            "corf": ["ON", "ON"],
            "cflr": ["0100", "INV"],
            "hflr": ["0100", "80"],
            "sltm": ["OFF", "OFF"],
            "osal": ["0063", "0030"],
            "osau": ["0243", "0200"],
            "ancp": ["CUST", "CUST"],
        },
        "scheduler": {"srsc": "000000005b1792f0", "dstv": "0001", "tzid": "0001"},
    }
    mqtt_client.state_change(new_status)
    assert device.is_on is True
    assert device.auto_mode is True
    assert device.oscillation is True
    assert device.oscillation_status is True
    assert device.oscillation_angle_low == 30
    assert device.oscillation_angle_high == 200
    assert device.front_airflow is True
    assert device.night_mode_speed == 10
    assert device.carbon_filter_life is None
    assert device.hepa_filter_life == 80

    mqtt_client._environmental_data = {
        "data": {
            "tact": "2977",
            "hact": "0058",
            "pm25": "0009",
            "pm10": "0005",
            "va10": "0004",
            "noxl": "0011",
            "p25r": "0010",
            "p10r": "0009",
            "sltm": "OFF",
        }
    }
    device.request_environmental_data()
    assert device.particulate_matter_2_5 == 9
    assert device.particulate_matter_10 == 5
    assert device.volatile_organic_compounds == 4
    assert device.nitrogen_dioxide == 11


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("turn_on", [], {"fpwr": "ON"}),
        ("turn_off", [], {"fpwr": "OFF"}),
        ("set_speed", [3], {"fpwr": "ON", "fnsp": "0003"}),
        ("enable_auto_mode", [], {"auto": "ON"}),
        ("disable_auto_mode", [], {"auto": "OFF"}),
        (
            "enable_oscillation",
            [],
            {
                "oson": "OION",
                "fpwr": "ON",
                "ancp": "CUST",
                "osal": "0063",
                "osau": "0243",
            },
        ),
        (
            "enable_oscillation",
            [15, 15],
            {
                "oson": "OION",
                "fpwr": "ON",
                "ancp": "CUST",
                "osal": "0015",
                "osau": "0015",
            },
        ),
        (
            "enable_oscillation",
            [15, 45],
            {
                "oson": "OION",
                "fpwr": "ON",
                "ancp": "CUST",
                "osal": "0015",
                "osau": "0045",
            },
        ),
        ("disable_oscillation", [], {"oson": "OIOF"}),
        ("enable_continuous_monitoring", [], {"fpwr": "OFF", "rhtm": "ON"}),
        ("disable_continuous_monitoring", [], {"fpwr": "OFF", "rhtm": "OFF"}),
        ("enable_front_airflow", [], {"fdir": "ON"}),
        ("disable_front_airflow", [], {"fdir": "OFF"}),
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
        DysonPureCool(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )


@pytest.mark.parametrize(
    "angle_low,angle_high",
    [
        (3, 300),
        (5, 400),
        (300, 5),
        (5, 34),
    ],
)
def test_oscillation_invalid_data(
    mqtt_client: MockedMQTT, angle_low: int, angle_high: int
):
    """Test commands with invalid data."""
    device = DysonPureCool(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)
    with pytest.raises(ValueError):
        device.enable_oscillation(angle_low, angle_high)
    assert len(mqtt_client.commands) == 0
