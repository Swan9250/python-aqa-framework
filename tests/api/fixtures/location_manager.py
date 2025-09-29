# pylint: disable=redefined-outer-name
# pyright: reportArgumentType=false
# pyright: reportGeneralTypeIssues=false

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

    def get_city_payload(self, city_name: str = None) -> CityModel:
        if city_name is None:
            return self.get_random_city_payload()
        return self.get_city_payload_by_name(city_name)

    def get_city_payload_by_name(self, name: str) -> CityModel | None:
        city_payloads = self.get_city_payloads()
        for city_payload in city_payloads:
            if name in city_payload.city:
                return city_payload
        pytest.raises("Fail to get city payload by city name")

    def get_random_city_payload(self) -> dict:
        return random.choice(self.get_city_payloads()).to_dict()

    def get_delivery_points_by_city_code(
        self, city_code: int
    ) -> List[DeliveryPointModel]:
        delivery_point_payloads = self.point_repo.get_delivery_points_by_city_code(
            city_code
        )
        if not delivery_point_payloads:
            delivery_point_payloads = self.point_repo.write_delivery_points(
                self._fetch_delivery_point_payloads(city_code), city_code
            )
        return delivery_point_payloads

    def _fetch_delivery_point_payloads(self, city_code):
        try:
            response = requests.get(
                url=self.token_manager.endpoints.delivery_points(),
                headers=self.token_manager.auth_header,
                params={"city_code": city_code},
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            return response.json()
        except (requests.RequestException, ValueError) as e:
            pytest.raises(f"Fail to fetch delivery points from API: {e}")

    def _fetch_city_payloads(self):
        try:
            response = requests.get(
                url=self.token_manager.endpoints.cities(),
                headers=self.token_manager.auth_header,
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            pytest.raises(f"Fail to fetch cities from API: {e}")


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
    return location_manager.get_city_payload


@pytest.fixture(scope="session")
def city_code(city_payload):
    def _city_code(city_name: str = None) -> int:
        return city_payload(city_name).code

    return _city_code


@pytest.fixture
def get_delivery_points_by_city_code(location_manager: LocationManager, city_code):
    def _get_delivery_points_by_city_code(city_name: str = None):
        return location_manager.get_delivery_points_by_city_code(city_code(city_name))

    return _get_delivery_points_by_city_code
