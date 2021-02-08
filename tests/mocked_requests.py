"""Mocked requests library."""

import json
from typing import Callable

import requests

from libdyson.dyson_account import (
    DYSON_API_HEADERS,
    DYSON_API_URL,
    DYSON_API_URL_CN,
    DYSON_CERT,
)


class MockedRequests:
    """Mocked requests library."""

    def __init__(self, country):
        """Initialize the mock."""
        self._country = country
        self._handlers = {}

    @property
    def country(self) -> str:
        """Return the country."""
        return self._country

    def register_handler(self, method: str, path: str, handler: Callable) -> None:
        """Register request handler."""
        self._handlers[(method, path)] = handler

    def request(
        self, method: str, url: str, headers=None, verify=None, **kwargs
    ) -> requests.Response:
        """Run mocked request function."""
        assert headers == DYSON_API_HEADERS
        assert verify == DYSON_CERT
        if self._country == "CN":
            url_base = DYSON_API_URL_CN
        else:
            url_base = DYSON_API_URL
        assert url.startswith(url_base)
        path = url[len(url_base) :]
        status_code, payload = self._handlers[(method, path)](**kwargs)
        response = requests.Response()
        response.status_code = status_code
        response.encoding = "utf-8"
        if payload is not None:
            content = json.dumps(payload).encode("utf-8")
            response._content = content
        return response
