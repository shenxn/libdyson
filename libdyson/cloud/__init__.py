"""Dyson cloud client."""
import pathlib
from typing import List, Optional

import requests
from requests.auth import HTTPBasicAuth

from libdyson.exceptions import (
    DysonAuthRequired,
    DysonInvalidAuth,
    DysonLoginFailure,
    DysonNetworkError,
    DysonServerError,
)

from .device_info import DysonDeviceInfo

DYSON_API_URL = "https://appapi.cp.dyson.com"
DYSON_API_URL_CN = "https://appapi.cp.dyson.cn"
DYSON_API_HEADERS = {"User-Agent": "DysonLink/29019 CFNetwork/1188 Darwin/20.0.0"}

API_PATH_LOGIN = "/v1/userregistration/authenticate"
API_PATH_DEVICES = "/v2/provisioningservice/manifest"

FILE_PATH = pathlib.Path(__file__).parent.absolute()

DYSON_CERT = f"{FILE_PATH}/certs/DigiCert-chain.crt"


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

    @property
    def auth_info(self) -> Optional[dict]:
        """Return the authentication info."""
        return self._auth_info

    @property
    def _auth(self) -> None:
        if self.auth_info is None:
            return None
        return HTTPBasicAuth(
            self.auth_info["Account"],
            self.auth_info["Password"],
        )

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        auth: bool = True,
    ) -> requests.Response:
        """Make API request."""
        if self._country == "CN":
            url = DYSON_API_URL_CN
        else:
            url = DYSON_API_URL
        if auth and self._auth is None:
            raise DysonAuthRequired
        try:
            response = requests.request(
                method,
                url + path,
                params=params,
                data=data,
                headers=DYSON_API_HEADERS,
                auth=self._auth if auth else None,
                verify=DYSON_CERT,
            )
        except requests.RequestException:
            raise DysonNetworkError
        if response.status_code == 401:
            raise DysonInvalidAuth
        if 500 <= response.status_code < 600:
            raise DysonServerError
        return response

    def login(self, email: str, password: str) -> None:
        """Login to Dyson cloud account."""
        try:
            response = self.request(
                "POST",
                API_PATH_LOGIN,
                params={"country": self._country},
                data={
                    "Email": email,
                    "Password": password,
                },
                auth=False,
            )
        except DysonInvalidAuth:
            raise DysonLoginFailure
        body = response.json()
        self._auth_info = body

    def devices(self) -> List[DysonDeviceInfo]:
        """Get device info from cloud account."""
        devices = []
        response = self.request("GET", API_PATH_DEVICES)
        for raw in response.json():
            devices.append(DysonDeviceInfo(raw))
        return devices
