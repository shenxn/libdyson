"""Utility functions for Dyson Python library."""

import base64
import hashlib
import time


def mqtt_time():
    """Return current time string for mqtt messages."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get_mqtt_password_from_wifi_password(wifi_password: str) -> str:
    """Calculate MQTT password from WiFi password."""
    hash_ = hashlib.sha512()
    hash_.update(wifi_password.encode("utf-8"))
    password_hash = base64.b64encode(hash_.digest()).decode("utf-8")
    return password_hash
