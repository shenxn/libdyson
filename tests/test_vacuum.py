"""Tests for Dyson vacuum base class."""
from unittest.mock import patch

import pytest

from libdyson import DEVICE_TYPE_360_EYE, CleaningType, Dyson360Eye, VacuumState

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT

STATUS = {
    "state": "INACTIVE_CHARGED",
    "fullCleanType": "",
    "cleanId": "",
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
    """Test properties of vaccums."""
    device = Dyson360Eye(SERIAL, CREDENTIAL)
    device.connect(HOST)

    assert device.state == VacuumState.INACTIVE_CHARGED
    assert device.cleaning_type is None
    assert device.cleaning_id is None
    assert device.position == (0, 0)
    assert device.is_charging is True
    assert device.battery_level == 100

    clean_id = "b599d00f-6f3b-401a-9c05-69877251e843"
    new_status = {
        "oldstate": "INACTIVE_CHARGED",
        "newstate": "FULL_CLEAN_RUNNING",
        "fullCleanType": "immediate",
        "cleanId": clean_id,
        "globalPosition": [],
        "batteryChargeLevel": 30,
    }
    mqtt_client.state_change(new_status)
    assert device.state == VacuumState.FULL_CLEAN_RUNNING
    assert device.cleaning_type == CleaningType.IMMEDIATE
    assert device.cleaning_id == clean_id
    assert device.position is None
    assert device.is_charging is False
    assert device.battery_level == 30
