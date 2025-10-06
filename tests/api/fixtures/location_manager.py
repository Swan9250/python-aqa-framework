# pylint: disable=redefined-outer-name
# pyright: reportArgumentType=false
# pyright: reportGeneralTypeIssues=false

import json
import random
from typing import Callable, List
import pytest
import requests
from constants import DEFAULT_REQUEST_TIMEOUT_S
from database.models import CityModel, DeliveryPointModel
from database.repository import CityRepository, DeliveryPointRepository
from tests.api.fixtures.token_manager import TokenManager


class LocationManager:
    def __init__(
        self,
        token_manager: TokenManager,
        city_repository: CityRepository,
        delivery_point_repository: DeliveryPointRepository,
    ) -> None:
        self.city_repo = city_repository
        self.point_repo = delivery_point_repository
        self.token_manager = token_manager
        self._city_payloads = None

    def get_city_payloads(self) -> List[CityModel]:
        # если уже получали ранее, берём полученное
        if self._city_payloads:
            return self._city_payloads
        # пытаемся взять из базы
        city_payloads = self.city_repo.all()
        # если нет в базе, делаем запрос к API и записываем в базу
        if not city_payloads:
            city_payloads = self.city_repo.write_cities(self._fetch_city_payloads())
        self._city_payloads = city_payloads
        return self._city_payloads

    def find_city_payload(self, **criteria) -> CityModel | None:
        payloads = self.get_city_payloads()
        if criteria:
            for payload in payloads:
                if all(getattr(payload, key) == value for key, value in criteria.items()):
                    return payload
            return None
        return random.choice(payloads)

    def find_city_points(self, city: CityModel) -> List[DeliveryPointModel]:
        delivery_point_payloads = city.delivery_points
        if not delivery_point_payloads:
            delivery_point_payloads = self.point_repo.write_points(
                self._fetch_city_points(city.code), city.code
            )
        return delivery_point_payloads

    def _fetch_city_points(self, city_code):
        try:
            response = requests.get(
                url=self.token_manager.endpoints.delivery_points(),
                headers=self.token_manager.auth_header,
                params={"city_code": city_code},
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            pytest.raises(requests.RequestException)
        except ValueError:
            pytest.raises(ValueError)

    def _fetch_city_payloads(self):
        try:
            response = requests.get(
                url=self.token_manager.endpoints.cities(),
                headers=self.token_manager.auth_header,
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            pytest.raises(requests.RequestException)
        except ValueError:
            pytest.raises(ValueError)


@pytest.fixture(scope="session")
def location_manager(
    token_manager: TokenManager,
    city_repository: CityRepository,
    delivery_point_repository: DeliveryPointRepository,
):
    return LocationManager(token_manager, city_repository, delivery_point_repository)


@pytest.fixture(scope="session")
def city_payload(
    location_manager: LocationManager,
) -> Callable:
    return location_manager.find_city_payload


@pytest.fixture
def get_city_delivery_points(location_manager: LocationManager):
    def _get_city_delivery_points(city: CityModel):
        return location_manager.find_city_points(city)

    return _get_city_delivery_points
