"""Calculate device credential using WiFi information."""

from libdyson import DEVICE_TYPE_NAMES, get_mqtt_info_from_wifi_info

print(
    "Note that you need to input your Dyson device WiFi information on the sticker"
    "on user's manual and device body. Do not put your home WiFi information."
)

wifi_ssid = input("Device WiFi SSID: ")
wifi_password = input("Device WiFi password: ")

serial, credential, model = get_mqtt_info_from_wifi_info(wifi_ssid, wifi_password)
print()
print("Serial:", serial)
print("Credential:", credential)
print("Model:", model)
print("Device Type:", DEVICE_TYPE_NAMES[model])
