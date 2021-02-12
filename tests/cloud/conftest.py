"""Dyson cloud test configuration."""

from unittest.mock import patch

import pytest

from .mocked_requests import MockedRequests


@pytest.fixture()
def mocked_requests() -> MockedRequests:
    """Return mocked requests library."""
    mocked_requests = MockedRequests()

    with patch("libdyson.cloud.account.requests.request", mocked_requests.request):
        yield mocked_requests
