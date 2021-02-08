"""Tests for DysonAccount."""

from typing import Optional, Tuple
from unittest.mock import patch

import pytest
import requests
from requests.auth import AuthBase, HTTPBasicAuth

from libdyson.dyson_account import API_PATH_DEVICES, API_PATH_LOGIN, DysonAccount
from libdyson.exceptions import (
    DysonAuthRequired,
    DysonInvalidAuth,
    DysonLoginFailure,
    DysonNetworkError,
    DysonServerError,
)

from .mocked_requests import MockedRequests
from .utils import encrypt_credential

EMAIL = "user@example.com"
PASSWORD = "password"

AUTH_ACCOUNT = "fe011372-8949-4fe4-a815-06a9992126e0"
AUTH_PASSWORD = "jvDII/gIG8MXCaWydBalT1Uo4KxM4NOfUaXqd5mwe6OKb5cjQJUyjC1+g0bVi2nJO4TN0ZS2PawMqc6+ITB4fA=="
AUTH_INFO = {
    "Account": AUTH_ACCOUNT,
    "Password": AUTH_PASSWORD,
}

DEVICE1_SERIAL = "NK6-CN-HAA0000A"
DEVICE1_NAME = "Device1"
DEVICE1_VERSION = "10.01.01CN"
DEVICE1_PRODUCT_TYPE = "475"
DEVICE1_CREDENTIAL = "aoWJM1kpL79MN2dPMlL5ysQv/APG+HAv+x3HDk0yuT3gMfgA3mLuil4O3d+q6CcyU+D1Hoir38soKoZHshYFeQ=="

DEVICE2_SERIAL = "JH1-US-HBB1111A"
DEVICE2_NAME = "Device2"
DEVICE2_VERSION = "11.02.02"
DEVICE2_PRODUCT_TYPE = "N223"
DEVICE2_CREDENTIAL = "KVjUpJoKwK7E9FDe5LN5JbUqDEfEDh5PlcNC7GJH1Ib2gGEpXwKEFszORFS8+tL8CNlvZTRmsUhf+kS37B7qAg=="

DEVICES = [
    {
        "Active": True,
        "Serial": DEVICE1_SERIAL,
        "Name": DEVICE1_NAME,
        "Version": DEVICE1_VERSION,
        "LocalCredentials": encrypt_credential(
            DEVICE1_SERIAL,
            DEVICE1_CREDENTIAL,
        ),
        "AutoUpdate": True,
        "NewVersionAvailable": False,
        "ProductType": DEVICE1_PRODUCT_TYPE,
        "ConnectionType": "wss",
    },
    {
        "Serial": DEVICE2_SERIAL,
        "Name": DEVICE2_NAME,
        "Version": DEVICE2_VERSION,
        "LocalCredentials": encrypt_credential(
            DEVICE2_SERIAL,
            DEVICE2_CREDENTIAL,
        ),
        "AutoUpdate": False,
        "NewVersionAvailable": True,
        "ProductType": DEVICE2_PRODUCT_TYPE,
        "ConnectionType": "wss",
    },
]


@pytest.fixture(params=["CN", "US"])
def mocked_requests(request):
    """Return mocked requests library."""
    country = request.param
    mocked_requests = MockedRequests(country)

    def _login_handler(
        params: dict, data: dict, auth: Optional[AuthBase]
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        assert params == {"country": country}
        if data["Email"] == EMAIL and data["Password"] == PASSWORD:
            return (200, AUTH_INFO)
        return (401, {"Message": "Unable to authenticate user."})

    def _devices_handler(
        auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        if (
            not isinstance(auth, HTTPBasicAuth)
            or auth.username != AUTH_ACCOUNT
            or auth.password != AUTH_PASSWORD
        ):
            return (401, None)
        return (200, DEVICES)

    mocked_requests.register_handler("POST", API_PATH_LOGIN, _login_handler)
    mocked_requests.register_handler("GET", API_PATH_DEVICES, _devices_handler)

    with patch("libdyson.dyson_account.requests.request", mocked_requests.request):
        yield mocked_requests


@pytest.fixture
def country(mocked_requests: MockedRequests) -> str:
    """Return country."""
    return mocked_requests.country


def test_account(country: str):
    """Test account functionalities."""
    account = DysonAccount(country)

    # Login failure
    with pytest.raises(DysonLoginFailure):
        account.login(EMAIL, "wrong_pass")
    assert account.auth_info is None
    with pytest.raises(DysonAuthRequired):
        account.devices()

    # Login succeed
    account.login(EMAIL, PASSWORD)
    assert account.auth_info == AUTH_INFO

    # Devices
    devices = account.devices()
    assert devices[0].active is True
    assert devices[0].serial == DEVICE1_SERIAL
    assert devices[0].name == DEVICE1_NAME
    assert devices[0].version == DEVICE1_VERSION
    assert devices[0].credential == DEVICE1_CREDENTIAL
    assert devices[0].product_type == DEVICE1_PRODUCT_TYPE
    assert devices[0].auto_update is True
    assert devices[0].new_version_available is False
    assert devices[1].active is None
    assert devices[1].serial == DEVICE2_SERIAL
    assert devices[1].name == DEVICE2_NAME
    assert devices[1].version == DEVICE2_VERSION
    assert devices[1].credential == DEVICE2_CREDENTIAL
    assert devices[1].product_type == DEVICE2_PRODUCT_TYPE
    assert devices[1].auto_update is False
    assert devices[1].new_version_available is True


def test_account_auth_info(country: str):
    """Test initialize account with auth info."""
    account = DysonAccount(country, auth_info=AUTH_INFO)
    devices = account.devices()
    assert len(devices) == 2

    # Invalid auth
    account = DysonAccount(
        country,
        auth_info={
            "Account": "invalid",
            "Password": "invalid",
        },
    )
    with pytest.raises(DysonInvalidAuth):
        account.devices()

    # No auth
    account = DysonAccount(country)
    with pytest.raises(DysonAuthRequired):
        account.devices()


def test_network_error(mocked_requests: MockedRequests, country: str):
    """Test network error handling."""

    def _handler_network_error(**kwargs):
        raise requests.RequestException

    mocked_requests.register_handler("POST", API_PATH_LOGIN, _handler_network_error)
    mocked_requests.register_handler("GET", API_PATH_DEVICES, _handler_network_error)

    account = DysonAccount(country)
    with pytest.raises(DysonNetworkError):
        account.login(EMAIL, PASSWORD)
    account = DysonAccount(country, auth_info=AUTH_INFO)
    with pytest.raises(DysonNetworkError):
        account.devices()


def test_server_error(mocked_requests: MockedRequests, country: str):
    """Test cloud server error handling."""

    def _handler_network_error(**kwargs):
        return (500, None)

    mocked_requests.register_handler("POST", API_PATH_LOGIN, _handler_network_error)
    mocked_requests.register_handler("GET", API_PATH_DEVICES, _handler_network_error)

    account = DysonAccount(country)
    with pytest.raises(DysonServerError):
        account.login(EMAIL, PASSWORD)
    account = DysonAccount(country, auth_info=AUTH_INFO)
    with pytest.raises(DysonServerError):
        account.devices()
