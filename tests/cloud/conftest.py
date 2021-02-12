"""Dyson cloud test configuration."""

from unittest.mock import patch

import pytest

from .mocked_requests import MockedRequests


@pytest.fixture(params=["US"])
def mocked_requests(request) -> MockedRequests:
    """Return mocked requests library."""
    country = request.param
    mocked_requests = MockedRequests(country)

    with patch("libdyson.cloud.account.requests.request", mocked_requests.request):
        yield mocked_requests


@pytest.fixture
def country(mocked_requests: MockedRequests) -> str:
    """Return country."""
    return mocked_requests.country
