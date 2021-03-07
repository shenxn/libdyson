# Changelog

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
