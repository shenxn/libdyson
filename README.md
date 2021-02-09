# Dyson Python Library

[![codecov](https://codecov.io/gh/shenxn/libdyson/branch/main/graph/badge.svg?token=v2OypI2WaI)](https://codecov.io/gh/shenxn/libdyson)

This library is still under development.

This library is a refactor of [libpurecool](https://github.com/etheralm/libpurecool). There is going to be some major changes:

- Initializing local connections no longer requires cloud login. Users can use the MQTT credentials directly.

- The interface of the library will be improved so that the same operation of different types of devices (e.g. PureCoolLink and PureCool) will have the same interface.

- Zeroconf based auto connection will be decoupled from device classes so that we can use only one zeroconf service to to auto connection for more than one device.

- The main purpose of this library is to support the HomeAssistant Dyson integration so that it'll only support Python 3.7+ and there is no plan for older versions of Python.
