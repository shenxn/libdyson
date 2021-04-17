"""Setup script."""
import setuptools

REQUIRES = [
    "paho_mqtt",
    "cryptography>=3.1",
    "requests",
    "zeroconf",
    "attrs",
]

setuptools.setup(
    include_package_data=True,
    install_requires=REQUIRES,
)
