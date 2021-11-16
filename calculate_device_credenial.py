"""Calculate device credential using WiFi information."""

from libdyson import DEVICE_TYPE_NAMES, get_mqtt_info_from_wifi_info
from libdyson.exceptions import DysonFailedToParseWifiInfo

print(
    "Note that you need to input your Dyson device WiFi information on the sticker"
    "on user's manual and device body. Do not put your home WiFi information."
)

wifi_ssid = input("Device WiFi SSID: ")
wifi_password = input("Device WiFi password: ")

try:
    serial, credential, device_type = get_mqtt_info_from_wifi_info(
        wifi_ssid, wifi_password
    )
except DysonFailedToParseWifiInfo:
    print(
        "Failed to parse SSID. Please report this to https://github.com/shenxn/libdyson/issues/new"
    )
print()
print("Serial:", serial)
print("Credential:", credential)
print("Device Type:", device_type)
print("Device Type Name:", DEVICE_TYPE_NAMES[device_type])
