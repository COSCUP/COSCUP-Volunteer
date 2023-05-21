"""This module is used to query TRA info through https://tdx.transportdata.tw/
"""
#!/usr/bin/env python3

import logging
from dataclasses import dataclass
from time import time
from typing import Any

import requests

from module.rail_api_enum import CabinClass, FareClass, TicketType, TrainType


@dataclass
class TrainStation:
    """Base Class for train station data"""

    def __init__(self, station: dict[str, Any]) -> None:
        self.station_uid = station["StationUID"]
        self.station_id = station["StationID"]
        self.zh_station_name = station["StationName"]["Zh_tw"]
        self.en_station_name = station["StationName"]["En"]
        self.station_class = station["StationClass"]


@dataclass
class TrainStations:
    """Class for all stations"""

    def __init__(self, station_list: list[dict[str, Any]]) -> None:
        self._station_list = []
        self._name_mapping = {}
        for i in station_list:
            station = TrainStation(i)
            self._station_list.append(station)
            self._name_mapping[station.en_station_name] = station
            self._name_mapping[station.zh_station_name] = station

    def __getitem__(self, name: str) -> TrainStation:
        return self._name_mapping[name]


@dataclass
class Fare:
    """Class for Ticket Fare Info"""
    def __init__(self, fare: dict[str, Any]) -> None:
        self.ticket_type = TicketType(fare["TicketType"])
        self.fare_class = FareClass(fare["FareClass"])
        self.cabin_class = CabinClass(fare["CabinClass"])
        self.price = fare["Price"]


class RailApi:
    """Api Client for querying train information"""

    api_url = "https://tdx.transportdata.tw/api/basic"
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    _auth_expiration = 0
    _access_token = ""

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._init_stations()

    def _get_auth(self) -> str:
        logging.debug("Authenticating...")
        if not self._auth_expiration or self._auth_expiration <= time():
            res = requests.post(
                self.auth_url,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "client_credentials",
                },
                headers={"content-type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            if not res.ok:
                raise Exception(res.text)
            self._access_token = res.json()["access_token"]
            self._auth_expiration = time() + res.json()["expires_in"]
        return self._access_token

    def call(self,
             endpoint: str,
             params: dict[str, str] | None = None) -> dict[str, Any]:
        """Call API endpoint directly

        Args:
            endpoint (str): Endponit for API. Should start with `/`.
            params (dict | None): Parameters when calling API.

        Raises:
            Exception: Response text if not OK.

        Returns:
            dict: Response JSON
        """
        api_url = "https://tdx.transportdata.tw/api/basic"
        res = requests.get(
            api_url + endpoint,
            params=params,
            timeout=30,
            headers={"authorization": f"Bearer {self._get_auth()}"},
        )
        if not res.ok:
            raise Exception(res.text)
        ret: dict[str, Any] = res.json()
        return ret

    def _init_stations(self) -> None:
        endpoint = "/v3/Rail/TRA/Station"
        logging.debug("Getting Train Station Info")

        ret = self.call(endpoint, params={"$format": "json"})
        self._train_station_list = TrainStations(ret["Stations"])

    def get_stations(self) -> TrainStations:
        """Get all station info

        Returns:
            TrainStations: Train stations
        """
        return self._train_station_list

    def get_fares(self, sta1: TrainStation,
                  sta2: TrainStation) -> list[dict[str, Any]]:
        """Get fare price between stations

        Args:
            sta1 (TrainStation): From staion
            sta2 (TrainStation): To staion

        Returns:
            list: Return a list of price fare
        """
        endpoint = (
            f"/v3/Rail/TRA/ODFare/{sta1.station_id}/to/{sta2.station_id}"
        )
        ret: list[dict[str, Any]] = self.call(endpoint)["ODFares"]
        return ret

    def get_fares_by_type(
        self, sta1: TrainStation, sta2: TrainStation, train_type: TrainType
    ) -> list[Fare]:
        """Get fare list by certain train type

        Args:
            sta1 (TrainStation): from station
            sta2 (TrainStation): to station
            train_type (TrainType): Type of train

        Returns:
            list: Fare list
        """

        fares = [
            x["Fares"]
            for x in self.get_fares(sta1, sta2)
            if x["TrainType"] == train_type
        ]
        ret: list[Fare] = [Fare(y) for x in fares for y in x]
        return ret
