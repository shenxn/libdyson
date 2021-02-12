"""Tests for 360 Eye cloud client."""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from requests.auth import AuthBase

from libdyson.cloud import DysonAccount
from libdyson.cloud.cloud_360_eye import CleaningType, DysonCloud360Eye

from . import AUTH_INFO
from .mocked_requests import MockedRequests

SERIAL = "JH1-US-HBB1111A"


def test_get_cleaning_history(mocked_requests: MockedRequests):
    """Test get cleaning history from the cloud."""
    cleaning1_id = "edcda2c9-5088-455e-b2ee-9422ef70afb2"
    cleaning2_id = "98cf2de1-190f-4e68-97b5-c57e7e0604d0"
    clean_history = {
        "TriviaMessage": "Your robot has cleaned 1000yds²",
        "TriviaArea": 800.1243,
        "Entries": [
            {
                "Clean": cleaning1_id,
                "Started": "2021-02-10T17:02:00",
                "Finished": "2021-02-10T17:02:10",
                "Area": 0.00,
                "Charges": 0,
                "Type": "Immediate",
                "IsInterim": False,
            },
            {
                "Clean": cleaning2_id,
                "Started": "2021-02-09T12:10:07",
                "Finished": "2021-02-09T14:14:11",
                "Area": 34.70,
                "Charges": 1,
                "Type": "Scheduled",
                "IsInterim": True,
            },
        ],
    }

    def _clean_history_handler(
        auth: Optional[AuthBase], **kwargs
    ) -> Tuple[int, Optional[dict]]:
        assert auth is not None
        return (0, clean_history)

    mocked_requests.register_handler(
        "GET", f"/v1/assets/devices/{SERIAL}/cleanhistory", _clean_history_handler
    )

    account = DysonAccount(AUTH_INFO)
    device = DysonCloud360Eye(account, SERIAL)
    cleaning_tasks = device.get_cleaning_history()
    assert len(cleaning_tasks) == 2
    task = cleaning_tasks[0]
    assert task.cleaning_id == cleaning1_id
    assert task.start_time == datetime(2021, 2, 10, 17, 2, 0)
    assert task.finish_time == datetime(2021, 2, 10, 17, 2, 10)
    assert task.cleaning_time == timedelta(seconds=10)
    assert task.area == 0.0
    assert task.charges == 0
    assert task.cleaning_type == CleaningType.Immediate
    assert task.is_interim is False
    task = cleaning_tasks[1]
    assert task.cleaning_id == cleaning2_id
    assert task.start_time == datetime(2021, 2, 9, 12, 10, 7)
    assert task.finish_time == datetime(2021, 2, 9, 14, 14, 11)
    assert task.cleaning_time == timedelta(hours=2, minutes=4, seconds=4)
    assert task.area == 34.7
    assert task.charges == 1
    assert task.cleaning_type == CleaningType.Scheduled
    assert task.is_interim is True


def test_get_cleaning_map(mocked_requests: MockedRequests):
    """Test get cleaning map from the cloud."""
    cleaning_id = "edcda2c9-5088-455e-b2ee-9422ef70afb2"
    cleaning_map = b"mocked_png_image"

    def _clean_history_handler(auth: Optional[AuthBase], **kwargs) -> Tuple[int, bytes]:
        assert auth is not None
        return (0, cleaning_map)

    mocked_requests.register_handler(
        "GET",
        f"/v1/mapvisualizer/devices/{SERIAL}/map/{cleaning_id}",
        _clean_history_handler,
    )

    account = DysonAccount(AUTH_INFO)
    device = DysonCloud360Eye(account, SERIAL)
    assert device.get_cleaning_map(cleaning_id) == cleaning_map

    # Non existed map
    assert device.get_cleaning_map("another_id") is None
