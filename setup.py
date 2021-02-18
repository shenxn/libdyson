"""Setup script."""
import setuptools

REQUIRES = [
    "paho_mqtt",
    "cryptography",
    "requests",
    "zeroconf",
    "attr",
]

setuptools.setup(
    include_package_data=True,
    install_requires=REQUIRES,
)
