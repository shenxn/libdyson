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


class FanMode(Enum):
    """Fan mode."""

    OFF = "OFF"
    FAN = "FAN"
    AUTO = "AUTO"


class FanSpeed(Enum):
    """Fan Speed."""

    SPEED_1 = "0001"
    SPEED_2 = "0002"
    SPEED_3 = "0003"
    SPEED_4 = "0004"
    SPEED_5 = "0005"
    SPEED_6 = "0006"
    SPEED_7 = "0007"
    SPEED_8 = "0008"
    SPEED_9 = "0009"
    SPEED_10 = "0010"
    SPEED_AUTO = "AUTO"


class AirQualityTarget(Enum):
    """Air Quality Target."""

    NORMAL = "0004"
    HIGH = "0003"
    DEFAULT = "0002"
    BETTER = "0001"
