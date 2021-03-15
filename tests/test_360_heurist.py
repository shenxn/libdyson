"""Tests for Dyson 360 Heurist vacuum."""
from unittest.mock import patch

import pytest

from libdyson import (
    DEVICE_TYPE_360_HEURIST,
    CleaningMode,
    Dyson360Heurist,
    VacuumHeuristPowerMode,
)

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

STATUS = {
    "currentVacuumPowerMode": "1",
    "defaultVacuumPowerMode": "2",
    "currentCleaningMode": "zoneConfigured",
    "defaultCleaningMode": "global",
}


@pytest.fixture(autouse=True)
def mqtt_client() -> MockedMQTT:
    """Return mocked mqtt client."""
    mocked_mqtt = MockedMQTT(
        HOST,
        SERIAL,
        CREDENTIAL,
        f"{DEVICE_TYPE_360_HEURIST}/{SERIAL}/command",
        f"{DEVICE_TYPE_360_HEURIST}/{SERIAL}/status",
        STATUS,
    )
    with patch("libdyson.dyson_device.mqtt.Client", mocked_mqtt.refersh):
        yield mocked_mqtt


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of 360 Heurist."""
    device = Dyson360Heurist(SERIAL, CREDENTIAL)
    device.connect(HOST)
    assert device.current_power_mode == VacuumHeuristPowerMode.QUIET
    assert device.default_power_mode == VacuumHeuristPowerMode.HIGH
    assert device.current_cleaning_mode == CleaningMode.ZONE_CONFIGURED
    assert device.default_cleaning_mode == CleaningMode.GLOBAL
    assert device.is_bin_full is False

    new_status = {
        "currentVacuumPowerMode": "2",
        "defaultVacuumPowerMode": "3",
        "currentCleaningMode": "global",
        "defaultCleaningMode": "zoneConfigured",
        "faults": {
            "AIRWAYS": {"active": True, "description": "1.0.-1"},
        },
    }
    mqtt_client.state_change(new_status)
    assert device.current_power_mode == VacuumHeuristPowerMode.HIGH
    assert device.default_power_mode == VacuumHeuristPowerMode.MAX
    assert device.current_cleaning_mode == CleaningMode.GLOBAL
    assert device.default_cleaning_mode == CleaningMode.ZONE_CONFIGURED
    assert device.is_bin_full is True


@pytest.mark.parametrize(
    "command,command_args,msg,msg_data",
    [
        (
            "start_all_zones",
            [],
            "START",
            {"cleaningMode": "global", "fullCleanType": "immediate"},
        ),
        ("pause", [], "PAUSE", {}),
        ("resume", [], "RESUME", {}),
        ("abort", [], "ABORT", {}),
        (
            "set_default_power_mode",
            [VacuumHeuristPowerMode.QUIET],
            "STATE-SET",
            {"defaults": {"defaultVacuumPowerMode": "1"}},
        ),
        (
            "set_default_power_mode",
            [VacuumHeuristPowerMode.HIGH],
            "STATE-SET",
            {"defaults": {"defaultVacuumPowerMode": "2"}},
        ),
        (
            "set_default_power_mode",
            [VacuumHeuristPowerMode.MAX],
            "STATE-SET",
            {"defaults": {"defaultVacuumPowerMode": "3"}},
        ),
    ],
)
def test_command(
    mqtt_client: MockedMQTT, command: str, command_args: list, msg: str, msg_data: dict
):
    """Test commands of 360 Heurist."""
    device = Dyson360Heurist(SERIAL, CREDENTIAL)
    device.connect(HOST)

    func = getattr(device, command)
    func(*command_args)
    len(mqtt_client.commands) == 1
    payload = mqtt_client.commands[0]
    assert payload.pop("msg") == msg
    assert payload.pop("mode-reason") == "LAPP"
    payload.pop("time")
    assert payload == msg_data
