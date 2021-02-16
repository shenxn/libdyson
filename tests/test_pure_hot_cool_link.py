"""Tests for Dyson Pure Hot+Cool Link device."""

import pytest

from libdyson import DEVICE_TYPE_PURE_HOT_COOL_LINK, DysonPureHotCoolLink

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_fan_device import assert_command
from .test_pure_cool_link import ENVIRONMENTAL_DATA  # noqa: F401

DEVICE_TYPE = DEVICE_TYPE_PURE_HOT_COOL_LINK

STATUS = {"product-state": {"ffoc": "ON"}}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Hot+Cool Link."""
    device = DysonPureHotCoolLink(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Status
    assert device.focus_mode is True

    new_status = {"product-state": {"ffoc": ["ON", "OFF"]}}
    mqtt_client.state_change(new_status)
    assert device.focus_mode is False


@pytest.mark.parametrize(
    "command,command_args,msg_data",
    [
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
