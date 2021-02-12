"""Dyson cloud account client."""

import pathlib
from typing import Callable, List, Optional

import requests
from requests.auth import AuthBase, HTTPBasicAuth

from libdyson.exceptions import (
    DysonAuthRequired,
    DysonInvalidAccountStatus,
    DysonInvalidAuth,
    DysonLoginFailure,
    DysonNetworkError,
    DysonOTPTooFrequently,
    DysonServerError,
)

from .device_info import DysonDeviceInfo

DYSON_API_HOST = "https://appapi.cp.dyson.com"
DYSON_API_HOST_CN = "https://appapi.cp.dyson.cn"
DYSON_API_HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0; Android SDK built for x86_64 Build/MASTER)"
}

API_PATH_USER_STATUS = "/v1/userregistration/userstatus"
API_PATH_LOGIN = "/v1/userregistration/authenticate"
API_PATH_MOBILE_REQUEST = "/v3/userregistration/mobile/auth"
API_PATH_MOBILE_VERIFY = "/v3/userregistration/mobile/verify"
API_PATH_DEVICES = "/v2/provisioningservice/manifest"

FILE_PATH = pathlib.Path(__file__).parent.absolute()

DYSON_CERT = f"{FILE_PATH}/certs/DigiCert-chain.crt"


class HTTPBearerAuth(AuthBase):
    """Attaches HTTP Bearder Authentication to the given Request object."""

    def __init__(self, token):
        """Initialize the auth."""
        self.token = token

    def __eq__(self, other):
        """Return if equal."""
        self.token == getattr(other, "token", None)

    def __ne__(self, other):
        """Return if not equal."""
        return not self == other

    def __call__(self, r):
        """Attach the authentication."""
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class DysonAccount:
    """Dyson account."""

    _HOST = DYSON_API_HOST

    def __init__(
        self,
        auth_info: Optional[dict] = None,
    ):
        """Create a new Dyson account."""
        self._auth_info = auth_info

    @property
    def auth_info(self) -> Optional[dict]:
        """Return the authentication info."""
        return self._auth_info

    @property
    def _auth(self) -> Optional[AuthBase]:
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
        if auth and self._auth is None:
            raise DysonAuthRequired
        try:
            response = requests.request(
                method,
                self._HOST + path,
                params=params,
                json=data,
                headers=DYSON_API_HEADERS,
                auth=self._auth if auth else None,
                verify=DYSON_CERT,
            )
        except requests.RequestException:
            raise DysonNetworkError
        if response.status_code in [401, 403]:
            raise DysonInvalidAuth
        if 500 <= response.status_code < 600:
            raise DysonServerError
        return response

    def login_email_password(self, email: str, password: str, region: str) -> None:
        """Login to Dyson cloud account using traditional email and password."""
        response = self.request(
            "GET",
            API_PATH_USER_STATUS,
            params={"country": region, "email": email},
            auth=False,
        )
        account_status = response.json()["accountStatus"]
        if account_status != "ACTIVE":
            raise DysonInvalidAccountStatus(account_status)

        try:
            response = self.request(
                "POST",
                API_PATH_LOGIN,
                params={"country": region},
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
            devices.append(DysonDeviceInfo.from_raw(raw))
        return devices


class DysonAccountCN(DysonAccount):
    """Dyson account in Mainland China."""

    _HOST = DYSON_API_HOST_CN

    @property
    def _auth(self) -> Optional[AuthBase]:
        if self.auth_info is None:
            return None
        if "Password" in self.auth_info:
            return super()._auth
        elif self.auth_info.get("tokenType") == "Bearer":
            return HTTPBearerAuth(self.auth_info["token"])
        return None

    def login_mobile_otp(self, mobile: str) -> Callable[[str], None]:
        """Login using phone number and OTP code."""
        response = self.request(
            "POST",
            API_PATH_MOBILE_REQUEST,
            data={"mobile": mobile},
            auth=False,
        )
        if response.status_code == 429:
            raise DysonOTPTooFrequently

        challenge_id = response.json()["challengeId"]

        def _verify(otp_code: str):
            response = self.request(
                "POST",
                API_PATH_MOBILE_VERIFY,
                data={
                    "mobile": mobile,
                    "challengeId": challenge_id,
                    "otpCode": otp_code,
                },
                auth=False,
            )
            if response.status_code == 400:
                raise DysonLoginFailure
            body = response.json()
            self._auth_info = body

        return _verify
