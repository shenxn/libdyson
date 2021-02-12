# Changelog

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
