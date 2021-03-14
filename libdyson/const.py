"""Constants for Dyson Python library."""
from enum import Enum, auto

DEVICE_TYPE_360_EYE = "N223"
DEVICE_TYPE_PURE_COOL_LINK = "475"
DEVICE_TYPE_PURE_COOL_LINK_DESK = "469"
DEVICE_TYPE_PURE_COOL = "438"
DEVICE_TYPE_PURE_COOL_DESK = "520"
DEVICE_TYPE_PURE_HUMIDIFY_COOL = "358"
DEVICE_TYPE_PURE_HOT_COOL_LINK = "455"
DEVICE_TYPE_PURE_HOT_COOL = "527"

DEVICE_TYPE_NAMES = {
    DEVICE_TYPE_360_EYE: "360 Eye robot vacuum",
    DEVICE_TYPE_PURE_COOL: "Pure Cool",
    DEVICE_TYPE_PURE_COOL_DESK: "Pure Cool Desk",
    DEVICE_TYPE_PURE_COOL_LINK: "Pure Cool Link",
    DEVICE_TYPE_PURE_COOL_LINK_DESK: "Pure Cool Link Desk",
    DEVICE_TYPE_PURE_HOT_COOL: "Pure Hot+Cool",
    DEVICE_TYPE_PURE_HOT_COOL_LINK: "Pure Hot+Cool Link",
    DEVICE_TYPE_PURE_HUMIDIFY_COOL: "Pure Humidify+Cool",
}

ENVIRONMENTAL_OFF = -1
ENVIRONMENTAL_INIT = -2
ENVIRONMENTAL_FAIL = -3


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


class HumidifyOscillationMode(Enum):
    """Pure Humidify+Cool oscillation mode."""

    DEGREE_45 = "0045"
    DEGREE_90 = "0090"
    BREEZE = "BRZE"


class WaterHardness(Enum):
    """Water Hardness."""

    SOFT = "Soft"
    MEDIUM = "Medium"
    HARD = "Hard"
