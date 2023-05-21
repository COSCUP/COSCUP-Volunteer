"""Pytest for RailApi"""
import pytest

from module.rail_api import RailApi
from setting import CLIENT_ID, CLIENT_SECRET


@pytest.fixture()
def api_class():
    return RailApi(CLIENT_ID, CLIENT_SECRET)


def test_get_station_info(api_class):
    stations = api_class.get_stations()
    assert stations["臺北"].station_id == '1000'
