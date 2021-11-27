"""Tests for utils."""

from libdyson.const import DEVICE_TYPE_360_EYE
from libdyson.utils import get_mqtt_info_from_wifi_info


def test_get_mqtt_info_from_wifi_info():
    """Test the function to get mqtt info from wifi info."""
    assert get_mqtt_info_from_wifi_info("JH1-US-GDA0001A", "z2jks80tmz") == (
        "JH1-US-GDA0001A",
        "wcosm2mJlB57tHnsxp3i8CiSz8H13J4i4p6Jw2SjdW3c+u+AZtG3PNmZ/ldaFS+Auubl5QRC/z3Lk4D3j+DQNw==",
        DEVICE_TYPE_360_EYE,
    )
    assert get_mqtt_info_from_wifi_info("360EYE-JH1-US-GDA0001A", "z2jks80tmz") == (
        "JH1-US-GDA0001A",
        "wcosm2mJlB57tHnsxp3i8CiSz8H13J4i4p6Jw2SjdW3c+u+AZtG3PNmZ/ldaFS+Auubl5QRC/z3Lk4D3j+DQNw==",
        DEVICE_TYPE_360_EYE,
    )
    assert get_mqtt_info_from_wifi_info("DYSON-NN3-EU-HWL4729E-475", "hjkj3gjask") == (
        "NN3-EU-HWL4729E",
        "Tp+0uDTy8scsa/PnYOeBVljZJiqzIZG+A0zOe4fiRJWXVKNOI4mpnFX7gDeEl5MEO10KFDbvVn4/4hiE2vpwiw==",
        "475",
    )
    assert get_mqtt_info_from_wifi_info("DYSON-SZ1-AU-MMZ2666D-455A", "sgrjjnsk01") == (
        "SZ1-AU-MMZ2666D",
        "sJKBwMhAGU9nAfdiHh4cXXCAm2E+YYPXGU6xp1NFcxX86f7NcRzs75QwCreZKt1SF1dQ9JoCrgj1bSsduaDcZA==",
        "455",
    )
