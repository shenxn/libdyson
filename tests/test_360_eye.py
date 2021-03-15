"""Tests for Dyson 360 Eye vacuum."""
from unittest.mock import patch

import pytest

from libdyson import DEVICE_TYPE_360_EYE, Dyson360Eye, VacuumEyePowerMode

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

STATUS = {
    "currentVacuumPowerMode": "fullPower",
    "defaultVacuumPowerMode": "fullPower",
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
    device.connect(HOST)
    assert device.power_mode == VacuumEyePowerMode.MAX

    new_status = {
        "currentVacuumPowerMode": "halfPower",
        "defaultVacuumPowerMode": "halfPower",
    }
    mqtt_client.state_change(new_status)
    assert device.power_mode == VacuumEyePowerMode.QUIET


@pytest.mark.parametrize(
    "command,command_args,msg,msg_data",
    [
        ("start", [], "START", {"fullCleanType": "immediate"}),
        ("pause", [], "PAUSE", {}),
        ("resume", [], "RESUME", {}),
        ("abort", [], "ABORT", {}),
        (
            "set_power_mode",
            [VacuumEyePowerMode.MAX],
            "STATE-SET",
            {"data": {"defaultVacuumPowerMode": "fullPower"}},
        ),
        (
            "set_power_mode",
            [VacuumEyePowerMode.QUIET],
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
