"""Tests for Pure Cool Formaldehyde"""

import pytest

from libdyson.const import (
    DEVICE_TYPE_PURE_COOL_FORMALDEHYDE,
    ENVIRONMENTAL_FAIL,
    ENVIRONMENTAL_INIT,
    ENVIRONMENTAL_OFF,
)
from libdyson.dyson_pure_cool import DysonPureCoolFormaldehyde

from . import CREDENTIAL, HOST, SERIAL
from .mocked_mqtt import MockedMQTT
from .test_pure_cool import STATUS as TEST_PURE_COOL_STATUS

DEVICE_TYPE = DEVICE_TYPE_PURE_COOL_FORMALDEHYDE

STATUS = TEST_PURE_COOL_STATUS
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
        "hcho": "OFF",
        "hchr": "OFF",
    }
}


def test_properties(mqtt_client: MockedMQTT):
    """Test properties of Pure Cool Link Formaldehyde."""
    device = DysonPureCoolFormaldehyde(SERIAL, CREDENTIAL, DEVICE_TYPE)
    device.connect(HOST)

    # Environmental
    assert device.particulate_matter_2_5 == ENVIRONMENTAL_OFF
    assert device.particulate_matter_10 == ENVIRONMENTAL_OFF
    assert device.volatile_organic_compounds == ENVIRONMENTAL_INIT
    assert device.nitrogen_dioxide == ENVIRONMENTAL_FAIL
    assert device.formaldehyde == ENVIRONMENTAL_OFF

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
            "hcho": "0001",
            "hchr": "0002",
        }
    }
    device.request_environmental_data()
    assert device.particulate_matter_2_5 == 9
    assert device.particulate_matter_10 == 5
    assert device.volatile_organic_compounds == 4
    assert device.nitrogen_dioxide == 11
    assert device.formaldehyde == 1
