"""Tests for Dyson Pure Hot+Cool Link device."""

import pytest

from libdyson import DEVICE_TYPE_PURE_HOT_COOL_LINK, DysonPureHotCoolLink

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command
from .test_pure_cool_link import ENVIRONMENTAL_DATA  # noqa: F401

DEVICE_TYPE = DEVICE_TYPE_PURE_HOT_COOL_LINK

STATUS = {
    "mode-reason": "RAPP",
    "state-reason": "MODE",
    "dial": "OFF",
    "rssi": "-29",
    "product-state": {
        "tilt": "OK",
        "ffoc": "ON",
        "hmax": "2805",
        "hmod": "HEAT",
        "hsta": "HEAT",
    },
    "scheduler": {"srsc": "8773", "dstv": "0000", "tzid": "0001"},
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Hot+Cool Link."""
    device = DysonPureHotCoolLink(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Status
    assert device.tilt is False
    assert device.focus_mode is True
    assert device.heat_target == 280.5
    assert device.heat_mode_is_on is True
    assert device.heat_status_is_on is True

    new_status = {
        "mode-reason": "LAPP",
        "state-reason": "MODE",
        "product-state": {
            "tilt": ["OK", "TILT"],
            "ffoc": ["ON", "OFF"],
            "hmax": ["2805", "2755"],
            "hmod": ["HEAT", "OFF"],
            "hsta": ["HEAT", "OFF"],
        },
        "scheduler": {"srsc": "8773", "dstv": "0000", "tzid": "0001"},
    }
    mqtt_client.state_change(new_status)
    assert device.tilt is True
    assert device.focus_mode is False
    assert device.heat_target == 275.5
    assert device.heat_mode_is_on is False
    assert device.heat_status_is_on is False


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
        ("set_heat_target", [279.5], {"hmod": "HEAT", "hmax": "2795"}),
        ("enable_heat_mode", [], {"hmod": "HEAT"}),
        ("disable_heat_mode", [], {"hmod": "OFF"}),
        ("enable_focus_mode", [], {"ffoc": "ON"}),
        ("disable_focus_mode", [], {"ffoc": "OFF"}),
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
        DysonPureHotCoolLink(SERIAL, CREDENTIAL, DEVICE_TYPE),
        mqtt_client,
        command,
        command_args,
        msg_data,
    )


@pytest.mark.parametrize("heat_target", [273, 310.5])
def test_set_heat_target_invalid_value(mqtt_client: MockedMQTT, heat_target: float):
    """Test set heat target with invalid value."""
    device = DysonPureHotCoolLink(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)
    with pytest.raises(ValueError):
        device.set_heat_target(heat_target)
    assert len(mqtt_client.commands) == 0
