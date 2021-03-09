"""Calculate device credential using WiFi information."""

from libdyson import get_mqtt_password_from_wifi_password

wifi_password = input("WiFi password: ")

mqtt_password = get_mqtt_password_from_wifi_password(wifi_password)
print("MQTT password: ", mqtt_password)
