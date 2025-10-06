# pylint: disable=redefined-outer-name
from typing import List
from faker import Faker
import pytest
from database.models import CityModel, DeliveryPointModel
from tests.api.constants import DEFAULT_WEIGHT_MAX_G, DEFAULT_WEIGHT_MIN_G

fake = Faker("ru_RU")


def get_city_weight_range(points: List[DeliveryPointModel]):
    min_weight_list = []
    max_weight_list = []
    for point in points:
        if point.weight_min:
            min_weight_list.append(int(point.weight_min) * 1000)
        if point.weight_max:
            max_weight_list.append(int(point.weight_max) * 1000)
    min_weight = max(min_weight_list) if min_weight_list else DEFAULT_WEIGHT_MIN_G
    max_weight = min(max_weight_list) if max_weight_list else DEFAULT_WEIGHT_MAX_G
    return (min_weight, max_weight)

@pytest.fixture
def packages_weight(get_city_delivery_points):
    def _packages_weight(from_city: CityModel, to_city: CityModel):
        from_points = get_city_delivery_points(from_city)
        to_points = get_city_delivery_points(to_city)
        from_min_weight, from_max_weight = get_city_weight_range(from_points)
        to_min_weight, to_max_weight = get_city_weight_range(to_points)
        min_weight = from_min_weight if from_min_weight > to_min_weight else to_min_weight
        max_weight = from_max_weight if from_max_weight < to_max_weight else to_max_weight
        return fake.pyint(min_value=min_weight, max_value=max_weight, step=10)
    return _packages_weight
