"""Dyson test configuration."""

from unittest.mock import patch

import pytest

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT


@pytest.fixture()
def mqtt_client(request: pytest.FixtureRequest) -> MockedMQTT:
    """Return mocked mqtt client."""
    device_type = request.module.DEVICE_TYPE
    status = request.module.STATUS
    environmental_data = request.module.ENVIRONMENTAL_DATA
    mocked_mqtt = MockedMQTT(
        HOST,
        SERIAL,
        CREDENTIAL,
        f"{device_type}/{SERIAL}/command",
        f"{device_type}/{SERIAL}/status/current",
        status,
        environmental_data,
    )
    with patch("libdyson.dyson_device.mqtt.Client", mocked_mqtt.refersh), patch(
        "libdyson.dyson_device.TIMEOUT", 0
    ):
        yield mocked_mqtt
