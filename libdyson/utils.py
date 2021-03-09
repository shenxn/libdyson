"""Utility functions for Dyson Python library."""

import base64
import hashlib
import re
import time
from typing import Tuple

from .const import DEVICE_TYPE_360_EYE


def mqtt_time():
    """Return current time string for mqtt messages."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get_mqtt_password_from_wifi_password(wifi_password: str) -> str:
    """Calculate MQTT password from WiFi password."""
    hash_ = hashlib.sha512()
    hash_.update(wifi_password.encode("utf-8"))
    password_hash = base64.b64encode(hash_.digest()).decode("utf-8")
    return password_hash


def get_mqtt_info_from_wifi_info(
    wifi_ssid: str, wifi_password: str
) -> Tuple[str, str, str]:
    """Get MQTT information from WiFi information."""
    result = re.match(r"^[0-9A-Z]{3}-[A-Z]{2}-[0-9A-Z]{8}$", wifi_ssid)
    if result is not None:
        serial = wifi_ssid
        model = DEVICE_TYPE_360_EYE
    else:
        result = re.match(
            r"^DYSON-([0-9A-Z]{3}-[A-Z]{2}-[0-9A-Z]{8})-([0-9]{3})$", wifi_ssid
        )
        if result is not None:
            serial = result.group(1)
            model = result.group(2)
        else:
            print(
                "Failed to parse SSID. Please report this to https://github.com/shenxn/libdyson/issues/new"
            )

    password = get_mqtt_password_from_wifi_password(wifi_password)
    return serial, password, model
