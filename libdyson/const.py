"""Constants for Dyson Python library."""
from enum import Enum, auto

DEVICE_TYPE_360_EYE = "N223"
DEVICE_TYPE_PURE_COOL_LINK_TOWER = "475"
DEVICE_TYPE_PURE_COOL_LINK_DESK = "469"

ENVIRONMENTAL_OFF = -1
ENVIRONMENTAL_INIT = -2


class MessageType(Enum):
    """Update message type."""

    STATE = auto()
    ENVIRONMENTAL = auto()


class AirQualityTarget(Enum):
    """Air Quality Target."""

    GOOD = "0004"
    SENSITIVE = "0003"
    DEFAULT = "0002"
    VERY_SENSITIVE = "0001"
