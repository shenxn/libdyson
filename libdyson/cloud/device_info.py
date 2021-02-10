"""Dyson device info."""

from .utils import decrypt_password


class DysonDeviceInfo:
    """Dyson device info."""

    def __init__(self, raw):
        """Create device info from raw data."""
        if "Active" in raw:
            self.active = raw["Active"]
        else:
            self.active = None
        self.serial = raw["Serial"]
        self.name = raw["Name"]
        self.version = raw["Version"]
        self.credential = decrypt_password(raw["LocalCredentials"])
        self.auto_update = raw["AutoUpdate"]
        self.new_version_available = raw["NewVersionAvailable"]
        self.product_type = raw["ProductType"]
