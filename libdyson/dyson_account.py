"""Dyson cloud account."""
import base64
import json
from typing import List, Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import requests
from requests.auth import HTTPBasicAuth
import urllib3

from libdyson.exceptions import DysonLoginFailure, DysonNetworkError

DYSON_API_URL = "https://appapi.cp.dyson.com"
DYSON_API_URL_CN = "https://appapi.cp.dyson.cn"
DYSON_API_HEADERS = {"User-Agent": "DysonLink/29019 CFNetwork/1188 Darwin/20.0.0"}


class DysonDeviceInfo:
    """Dyson device info."""

    def __init__(self, raw):
        """Create device info from raw data."""
        if "Active" in raw:
            self.active = raw["Active"]
        else:
            self.active = None
        self.serial = raw["Serial"]
        self.name = raw["Name"]
        self.version = raw["Version"]
        self.credential = _decrypt_passwrd(raw["LocalCredentials"])
        self.auto_update = raw["AutoUpdate"]
        self.new_version_available = raw["NewVersionAvailable"]
        self.product_type = raw["ProductType"]


class DysonAccount:
    """Dyson account."""

    def __init__(
        self,
        country: str,
        auth_info: Optional[dict] = None,
    ):
        """Create a new Dyson account."""
        self._country = country
        self._auth_info = auth_info
        self._auth = None
        if auth_info is not None:
            self._set_auth()

    @property
    def _url(self) -> str:
        if self._country == "CN":
            return DYSON_API_URL_CN
        return DYSON_API_URL

    @property
    def auth_info(self) -> Optional[dict]:
        """Return the authentication info."""
        return self._auth_info

    def _set_auth(self) -> None:
        self._auth = HTTPBasicAuth(
            self.auth_info["Account"],
            self.auth_info["Password"],
        )

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        auth: bool = True,
    ) -> requests.Response:
        return requests.request(
            method,
            self._url + path,
            params=params,
            data=data,
            headers=DYSON_API_HEADERS,
            auth=self._auth if auth else None,
            verify=False,
        )

    def login(self, email: str, password: str) -> None:
        """Login to Dyson cloud account."""
        # Disable insecure request warnings
        # since Dyson uses a self signed certificate
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            response = self._request(
                "POST",
                "/v1/userregistration/authenticate",
                params={"country": self._country},
                data={
                    "Email": email,
                    "Password": password,
                },
                auth=False,
            )
            if response.status_code == requests.codes.ok:
                body = response.json()
                self._auth_info = body
                self._set_auth()
            else:
                raise DysonLoginFailure
        except requests.RequestException as err:
            raise DysonNetworkError from err

    def devices(self) -> List[DysonDeviceInfo]:
        """Get device info from cloud account."""
        try:
            devices = []
            # response = self._request("GET", "/v1/provisioningservice/manifest")
            # for raw in response.json():
            #     devices.append(DysonDeviceInfo(raw))
            response = self._request("GET", "/v2/provisioningservice/manifest")
            for raw in response.json():
                devices.append(DysonDeviceInfo(raw))
            return devices
        except requests.RequestException as err:
            raise DysonNetworkError from err


def _unpad(string):
    """Un pad string."""
    return string[: -ord(string[len(string) - 1 :])]


def _decrypt_passwrd(encrypted_password):
    key = (
        b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"
        b"\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f "
    )
    init_vector = (
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" b"\x00\x00\x00\x00"
    )
    cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector))
    decryptor = cipher.decryptor()
    encrypted = base64.b64decode(encrypted_password)
    decrypted = decryptor.update(encrypted) + decryptor.finalize()
    json_password = json.loads(_unpad(decrypted))
    return json_password["apPasswordHash"]
