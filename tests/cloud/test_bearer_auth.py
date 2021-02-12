"""Tests for HTTPBearerAuth."""

from unittest.mock import MagicMock

import requests

from libdyson.cloud.account import HTTPBearerAuth


def test_bearer_auth():
    """Test HTTPBearerAuth."""
    auth1 = HTTPBearerAuth("token")
    auth2 = HTTPBearerAuth("token")
    auth3 = HTTPBearerAuth("token3")

    assert auth1 == auth2
    assert auth1 != auth3
    request = MagicMock(spec=requests.Request)
    request.headers = {"Key": "value"}
    request = auth1(request)
    assert request.headers == {
        "Key": "value",
        "Authorization": "Bearer token",
    }
