"""Dyson cloud account."""
import json
import base64
from typing import List, Optional
from aiohttp.client import ClientSession
from libdyson.exceptions import DysonLoginFailure, DysonNetworkError
import aiohttp
from Crypto.Cipher import AES

DYSON_API_URL = "https://appapi.cp.dyson.com"
DYSON_API_URL_CN = "https://appapi.cp.dyson.cn"
DYSON_API_HEADERS = {"User-Agent": "DysonLink/29019 CFNetwork/1188 Darwin/20.0.0"}


class DysonDeviceInfo():
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
        email: str,
        password: str,
        country: str,
        aiohttp_sesison: Optional[aiohttp.ClientSession]=None,
    ):
        """Create a new Dyson account."""
        self._email = email
        self._password = password
        self._country = country
        self._auth = None
        self._aiohttp_session = aiohttp_sesison

    @property
    def _url(self):
        if self._country == "CN":
            return DYSON_API_URL_CN
        return DYSON_API_URL

    @property
    def _session(self):
        if self._aiohttp_session is not None:
            return self._aiohttp_session
        return aiohttp.ClientSession()

    async def _async_close_session(self, session: aiohttp.ClientSession):
        if self._aiohttp_session is None:
            await session.close()

    async def async_login(self) -> None:
        """Login to Dyson cloud account."""
        session = self._session
        try:
            async with session.post(
                f"{self._url}/v1/userregistration/authenticate",
                params={"country": self._country},
                data={
                    "Email": self._email,
                    "Password": self._password,
                },
                headers=DYSON_API_HEADERS,
                verify_ssl=False,  # Dyson uses a self signed certificate
            ) as response:
                if response.ok:
                    body = await response.json()
                    self._auth = aiohttp.BasicAuth(
                        body["Account"],
                        body["Password"],
                    )
                else:
                    raise DysonLoginFailure
        except aiohttp.ClientError as err:
            raise DysonNetworkError from err
        finally:
            await self._async_close_session(session)
   

    async def async_devices(self) -> List[DysonDeviceInfo]:
        session = self._session
        try:
            devices = []
            async with session.get(
                f"{self._url}/v1/provisioningservice/manifest",
                auth=self._auth,
                headers=DYSON_API_HEADERS,
                verify_ssl=False,
            ) as response:
                for raw in await response.json():
                    devices.append(DysonDeviceInfo(raw))
            # TODO: v2 devices
            return devices
        except aiohttp.ClientError as err:
            raise DysonNetworkError from err
        finally:
            await self._async_close_session(session)


def _unpad(string):
    """Un pad string."""
    return string[:-ord(string[len(string) - 1:])]


def _decrypt_passwrd(encrypted_password):
    key = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10' \
          b'\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f '
    init_vector = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                  b'\x00\x00\x00\x00'
    cipher = AES.new(key, AES.MODE_CBC, init_vector)
    json_password = json.loads(_unpad(
        cipher.decrypt(base64.b64decode(encrypted_password)).decode('utf-8')))
    return json_password["apPasswordHash"]
