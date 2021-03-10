"""Tests for DysonAccount."""

from typing import Optional, Tuple

import pytest
import requests
from requests.auth import AuthBase, HTTPBasicAuth

from libdyson.cloud import DysonAccount
from libdyson.cloud.account import (
    API_PATH_DEVICES,
    API_PATH_EMAIL_REQUEST,
    API_PATH_EMAIL_VERIFY,
    API_PATH_MOBILE_REQUEST,
    API_PATH_MOBILE_VERIFY,
    API_PATH_USER_STATUS,
    DYSON_API_HOST_CN,
    DysonAccountCN,
    HTTPBearerAuth,
)
from libdyson.exceptions import (
    DysonAuthRequired,
    DysonInvalidAccountStatus,
    DysonInvalidAuth,
    DysonLoginFailure,
    DysonNetworkError,
    DysonOTPTooFrequently,
    DysonServerError,
)

from . import AUTH_ACCOUNT, AUTH_INFO, AUTH_PASSWORD
from .mocked_requests import MockedRequests
from .utils import encrypt_credential

EMAIL = "user@example.com"
PASSWORD = "password"
REGION = "GB"
MOBILE = "+8613588888888"
OTP = "000000"
CHALLENGE_ID = "2b289d7f-1e0d-41e2-a0cb-56115eab6855"

BEARER_TOKEN = "BEARER_TOKEN"
AUTH_INFO_BEARER = {
    "token": BEARER_TOKEN,
    "tokenType": "Bearer",
    "account": AUTH_ACCOUNT,
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
    {
        "Serial": "YS4-EU-MCA0660A",
        "Name": "Device3",
        "Version": "13.80.22",
        "LocalCredentials": None,
        "AutoUpdate": True,
        "NewVersionAvailable": False,
        "ProductType": "552",
        "ConnectionType": "wss",
    },
]


@pytest.fixture(autouse=True)
def mocked_requests(mocked_requests: MockedRequests) -> MockedRequests:
    """Return mocked requests library."""

    def _user_status_handler(
        params: dict, json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        assert params == {"country": REGION}
        if json["email"] == EMAIL:
            return (200, {"accountStatus": "ACTIVE"})
        return (200, {"accountStatus": "UNREGISTERED"})

    def _email_request_handler(
        json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        assert json == {
            "email": EMAIL,
        }
        return (200, {"challengeId": CHALLENGE_ID})

    def _email_verify_handler(
        json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        assert json["email"] == EMAIL
        assert json["challengeId"] == CHALLENGE_ID
        if json["password"] == PASSWORD and json["otpCode"] == OTP:
            return (200, AUTH_INFO_BEARER)
        return (400, None)

    def _mobile_request_handler(
        json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        assert json == {
            "mobile": MOBILE,
        }
        return (200, {"challengeId": CHALLENGE_ID})

    def _mobile_verify_handler(
        json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        assert json["mobile"] == MOBILE
        assert json["challengeId"] == CHALLENGE_ID
        if json["otpCode"] == OTP:
            return (200, AUTH_INFO_BEARER)
        return (400, None)

    def _devices_handler(
        auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        if (
            not isinstance(auth, HTTPBasicAuth)
            or auth.username != AUTH_ACCOUNT
            or auth.password != AUTH_PASSWORD
        ) and (not isinstance(auth, HTTPBearerAuth) or auth.token != BEARER_TOKEN):
            return (401, None)
        return (200, DEVICES)

    mocked_requests.register_handler("POST", API_PATH_USER_STATUS, _user_status_handler)
    mocked_requests.register_handler(
        "POST", API_PATH_EMAIL_REQUEST, _email_request_handler
    )
    mocked_requests.register_handler(
        "POST", API_PATH_EMAIL_VERIFY, _email_verify_handler
    )
    mocked_requests.register_handler(
        "POST", API_PATH_MOBILE_REQUEST, _mobile_request_handler
    )
    mocked_requests.register_handler(
        "POST", API_PATH_MOBILE_VERIFY, _mobile_verify_handler
    )
    mocked_requests.register_handler("GET", API_PATH_DEVICES, _devices_handler)
    return mocked_requests


def test_account():
    """Test account functionalities."""
    account = DysonAccount()

    # Incorrect email
    with pytest.raises(DysonInvalidAccountStatus):
        account.login_email_otp("unregistered@example.com", REGION)
    assert account.auth_info is None
    with pytest.raises(DysonAuthRequired):
        account.devices()

    # Incorrect password
    with pytest.raises(DysonLoginFailure):
        verify = account.login_email_otp(EMAIL, REGION)
        verify(OTP, "wrong_pass")
    assert account.auth_info is None

    # Incorrect OTP
    with pytest.raises(DysonLoginFailure):
        verify = account.login_email_otp(EMAIL, REGION)
        verify("999999", PASSWORD)
    assert account.auth_info is None

    # Login succeed
    verify = account.login_email_otp(EMAIL, REGION)
    verify(OTP, PASSWORD)
    assert account.auth_info == AUTH_INFO_BEARER

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


def test_account_auth_info():
    """Test initialize account with auth info."""
    account = DysonAccount(AUTH_INFO)
    devices = account.devices()
    assert len(devices) == 2

    # Invalid auth
    account = DysonAccount(
        {
            "Account": "invalid",
            "Password": "invalid",
        },
    )
    with pytest.raises(DysonInvalidAuth):
        account.devices()

    # No auth
    account = DysonAccount()
    with pytest.raises(DysonAuthRequired):
        account.devices()


def test_login_email_request_too_frequently(mocked_requests: MockedRequests):
    """Test request for otp code too frequently."""

    def _handle_email_request(
        json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        return (429, None)

    mocked_requests.register_handler(
        "POST", API_PATH_EMAIL_REQUEST, _handle_email_request
    )

    account = DysonAccount()
    with pytest.raises(DysonOTPTooFrequently):
        account.login_email_otp(EMAIL, REGION)


def test_login_mobile(mocked_requests: MockedRequests):
    """Test logging into account using phone number and otp code."""
    mocked_requests.host = DYSON_API_HOST_CN

    account = DysonAccountCN()
    verify = account.login_mobile_otp(MOBILE)

    # Incorrect OTP
    with pytest.raises(DysonLoginFailure):
        verify("111111")
    assert account.auth_info is None

    # Correct OTP
    verify(OTP)
    assert account.auth_info == AUTH_INFO_BEARER
    account.devices()


def test_login_mobile_request_too_frequently(mocked_requests: MockedRequests):
    """Test request for otp code too frequently."""

    def _handle_mobile_request(
        json: dict, auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is None
        return (429, None)

    mocked_requests.host = DYSON_API_HOST_CN
    mocked_requests.register_handler(
        "POST", API_PATH_MOBILE_REQUEST, _handle_mobile_request
    )

    account = DysonAccountCN()
    with pytest.raises(DysonOTPTooFrequently):
        account.login_mobile_otp(MOBILE)


def test_account_auth_info_bearer(mocked_requests: MockedRequests):
    """Test initialize account with bearer auth info."""
    mocked_requests.host = DYSON_API_HOST_CN
    account = DysonAccountCN(AUTH_INFO_BEARER)
    devices = account.devices()
    assert len(devices) == 2

    # Old auth
    account = DysonAccountCN(AUTH_INFO)
    devices = account.devices()
    assert len(devices) == 2

    # Invalid auth
    account = DysonAccountCN(
        {
            "token": "invalid",
            "tokenType": "Bearer",
            "account": "invalid",
        },
    )
    with pytest.raises(DysonInvalidAuth):
        account.devices()

    # No auth
    account = DysonAccountCN()
    with pytest.raises(DysonAuthRequired):
        account.devices()

    # Not supported auth info
    account = DysonAccountCN({"token": "TOKEN", "tokenType": "Custom"})
    with pytest.raises(DysonAuthRequired):
        account.devices()


def test_network_error(mocked_requests: MockedRequests):
    """Test network error handling."""

    def _handler_network_error(**kwargs):
        raise requests.RequestException

    mocked_requests.register_handler(
        "POST", API_PATH_EMAIL_REQUEST, _handler_network_error
    )
    mocked_requests.register_handler("GET", API_PATH_DEVICES, _handler_network_error)

    account = DysonAccount()
    with pytest.raises(DysonNetworkError):
        account.login_email_otp(EMAIL, REGION)
    account = DysonAccount(AUTH_INFO)
    with pytest.raises(DysonNetworkError):
        account.devices()


def test_server_error(mocked_requests: MockedRequests):
    """Test cloud server error handling."""

    def _handler_network_error(**kwargs):
        return (500, None)

    mocked_requests.register_handler(
        "POST", API_PATH_EMAIL_REQUEST, _handler_network_error
    )
    mocked_requests.register_handler("GET", API_PATH_DEVICES, _handler_network_error)

    account = DysonAccount()
    with pytest.raises(DysonServerError):
        account.login_email_otp(EMAIL, REGION)
    account = DysonAccount(AUTH_INFO)
    with pytest.raises(DysonServerError):
        account.devices()
