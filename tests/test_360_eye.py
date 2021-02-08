"""Tests for Dyson 360 Eye vacuum."""
from unittest.mock import patch

import pytest

from libdyson import DEVICE_TYPE_360_EYE
from libdyson.dyson_360_eye import Dyson360Eye, Dyson360EyePowerMode, Dyson360EyeState

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

STATUS = {
    "state": "INACTIVE_CHARGED",
    "fullCleanType": "",
    "cleanId": "",
    "currentVacuumPowerMode": "fullPower",
    "defaultVacuumPowerMode": "fullPower",
    "globalPosition": [0, 0],
    "batteryChargeLevel": 100,
}


@pytest.fixture(autouse=True)
def mqtt_client() -> MockedMQTT:
    """Return mocked mqtt client."""
    mocked_mqtt = MockedMQTT(
        HOST,
        SERIAL,
        CREDENTIAL,
        f"{DEVICE_TYPE_360_EYE}/{SERIAL}/command",
        f"{DEVICE_TYPE_360_EYE}/{SERIAL}/status",
        STATUS,
    )
    with patch("libdyson.dyson_device.mqtt.Client", mocked_mqtt.refersh):
        yield mocked_mqtt


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of 360 Eye."""
    device = Dyson360Eye(SERIAL, CREDENTIAL)

    # Make sure no errors without connection
    assert device.state is None
    assert device.full_clean_type is None
    assert device.clean_id is None
    assert device.power_mode is None
    assert device.position is None
    assert device.is_charging is None
    assert device.battery_level is None

    device.connect(HOST)

    assert device.state == Dyson360EyeState.INACTIVE_CHARGED
    assert device.full_clean_type == ""
    assert device.clean_id == ""
    assert device.power_mode == Dyson360EyePowerMode.MAX
    assert device.position == (0, 0)
    assert device.is_charging is True
    assert device.battery_level == 100

    clean_id = "b599d00f-6f3b-401a-9c05-69877251e843"
    new_status = {
        "oldstate": "INACTIVE_CHARGED",
        "newstate": "FULL_CLEAN_RUNNING",
        "fullCleanType": "immediate",
        "cleanId": clean_id,
        "currentVacuumPowerMode": "halfPower",
        "defaultVacuumPowerMode": "halfPower",
        "globalPosition": [-3, 50],
        "batteryChargeLevel": 30,
    }
    mqtt_client.state_change(new_status)
    assert device.state == Dyson360EyeState.FULL_CLEAN_RUNNING
    assert device.full_clean_type == "immediate"
    assert device.clean_id == clean_id
    assert device.power_mode == Dyson360EyePowerMode.QUIET
    assert device.position == (-3, 50)
    assert device.is_charging is False
    assert device.battery_level == 30


@pytest.mark.parametrize(
    "command,command_args,msg,msg_data",
    [
        ("start", [], "START", {"fullCleanType": "immediate"}),
        ("pause", [], "PAUSE", {}),
        ("resume", [], "RESUME", {}),
        ("abort", [], "ABORT", {}),
        (
            "set_power_mode",
            [Dyson360EyePowerMode.MAX],
            "STATE-SET",
            {"data": {"defaultVacuumPowerMode": "fullPower"}},
        ),
        (
            "set_power_mode",
            [Dyson360EyePowerMode.QUIET],
            "STATE-SET",
            {"data": {"defaultVacuumPowerMode": "halfPower"}},
        ),
    ],
)
def test_command(
    mqtt_client: MockedMQTT, command: str, command_args: list, msg: str, msg_data: dict
):
    """Test commands of 360 Eye."""
    device = Dyson360Eye(SERIAL, CREDENTIAL)
    device.connect(HOST)

    func = getattr(device, command)
    func(*command_args)
    len(mqtt_client.commands) == 1
    payload = mqtt_client.commands[0]
    assert payload.pop("msg") == msg
    payload.pop("time")
    assert payload == msg_data
