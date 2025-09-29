# pylint: disable=redefined-outer-name
from faker import Faker
import pytest
from tests.api.constants import DEFAULT_WEIGHT_MAX_G, DEFAULT_WEIGHT_MIN_G

fake = Faker("ru_RU")


@pytest.fixture
def get_delivery_point_min_weight():
    def _get_delivery_point_min_weight(delivery_point: dict):
        return delivery_point.get("weight_min", DEFAULT_WEIGHT_MIN_G / 1000)

    return _get_delivery_point_min_weight


@pytest.fixture
def get_delivery_point_max_weight():
    def _get_delivery_point_max_weight(delivery_point: dict):
        return delivery_point.get("weight_max", DEFAULT_WEIGHT_MAX_G / 1000)

    return _get_delivery_point_max_weight


@pytest.fixture
def get_min_delivery_weight():
    def _get_min_delivery_weight(weight_from, weight_to):
        return weight_from if weight_from > weight_to else weight_to

    return _get_min_delivery_weight


@pytest.fixture
def get_max_delivery_weight():
    def _get_max_delivery_weight(weight_from, weight_to):
        return weight_from if weight_from < weight_to else weight_to


@pytest.fixture
def get_delivery_weight(
    get_delivery_points_by_city_code,
    get_delivery_point_min_weight,
    get_delivery_point_max_weight,
    get_min_delivery_weight,
    get_max_delivery_weight,
):
    def _get_delivery_weight(from_location, to_location):
        from_delivery_point = get_delivery_points_by_city_code(
            from_location["city_code"]
        )
        to_delivery_point = get_delivery_points_by_city_code(to_location["city_code"])
        min_weight = get_min_delivery_weight(
            get_delivery_point_min_weight(from_delivery_point),
            get_delivery_point_min_weight(to_delivery_point),
        )
        max_weight = get_max_delivery_weight(
            get_delivery_point_max_weight(from_delivery_point),
            get_delivery_point_max_weight(to_delivery_point),
        )
        weight = fake.pyfloat(
            min_value=min_weight, max_value=max_weight, right_digits=3
        )
        return weight

    return _get_delivery_weight
