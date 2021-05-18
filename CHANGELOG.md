# Changelog

## 0.8.6

- Add new device type Pure Hot+Cool New (527E) (#9)

## 0.8.5

- Add new device type Pure Hot+Cool Link New (455A)
- Make it possible to parse WiFi SSID of 455A and 438E devices
- Support `ON/OFF` as `oson` value for Pure Cool devices

## 0.8.4

- Fix CN cert chain

## 0.8.3

- Fix socket leak
- Add new device type Pure Cool 2021 (438E)

## 0.8.2

- Turn off humidification auto mode when set target humidity
- Add `CUST` to `HumidifyOscillationMode`

## 0.8.1

- Fix reconnection
- Add `OFF` to `AirQualityTarget`

## 0.8.0

- Rename `humidity_target` to `target_humidity` (Breaking)
- Add support to 360 Heurist (Experimental)

## 0.7.3

- Rename `oscillation_angle` to `oscillation_mode` for Pure Humidity+Cool

## 0.7.2

- Rename `humidity_cool` to `humidify_cool` (Fix typo)
- Add full support to Pure Humidify+Cool device

## 0.7.1

- Improve `get_mqtt_info_from_wifi_info`

## 0.7.0

- Add function to retrieve MQTT username and password (local credential) from device WiFi SSID and password
- Skip Lightcycle lights when getting device info from the account so the function does not crash

## 0.6.2

- Report `is_on` based on `fpwr` (Pure Cool) and `fmod` (Pure Cool Link) instead of fan `fnst`
- Add a property `fan_state` (`fnst`) to fan devices

## 0.6.1

- Change typo (attr -> attrs) in the dependency list

## 0.6.0

- Add Hot+Cool devices into device type names
- Login using email OTP

## 0.5.2

- Callback on connect and disconnect
- Remove TM from device names

## 0.5.1

- Add dependencies to PyPI package

## 0.5.0

- Add support to Dyson Pure Hot+Cool
- Add support to Dyson Pure Hot+Cool Link

## 0.4.0

- Add support to Dyson Pure Cool
- Add device type names dictionary
- Add more states to VacuumState
- Code quality improvement

## 0.3.3

- Fix wheel building to include certificate

## 0.3.2

- Include Dyson cloud server certificate chain into PyPI package

## 0.3.1

- Add account region list

## 0.3.0

- Add support to login using phone number and OTP code for account in Mainland China.
- Fix account login problem.
- Code quality improvement.

## 0.2.0

- Replace `aiohttp` with `requests`. `asyncio` is removed.
- Add v2 devices list support to `DysonAccount`.
- Replace deprecated `pycryptodome` with `cryptography`.
- Add zeroconf based discovery.
- Code quality improvement.

## 0.1.0

This is the first version of this library. Only Dyson 360 Eye robot vacuums are currently supported.

- Dyson 360 Eye robot vacuum support added.
- Cloud account support added. 
- `get_devices.py` script to get serial numbers and credentials from cloud account.
