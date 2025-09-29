# pylint: disable=redefined-outer-name
# pyright: reportArgumentType=false
import random
from typing import List
import pytest
import requests

from database.models import OrderModel

from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S


pytest_plugins = [
    "fixtures.database",
    "fixtures.token_manager",
    "fixtures.data_generators",
    "fixtures.location_manager",
    "fixtures.tariff_calculator",
    "fixtures.hooks",
    "fixtures.helpers",
]


@pytest.fixture
def get_order_uuid(
    auth_header,
    endpoints,
    get_random_city,
    get_tariff_code,
    packages,
    recipient,
    sender,
    order_repository,
):
    def _get_order_uuid(city):
        last_order_uuid = ""
        orders: List[OrderModel] = order_repository.get_all_orders()
        if orders:
            last_order_uuid = orders[0].uuid
        else:
            from_location = get_random_city()
            to_location = get_random_city()
            tariff_code = get_tariff_code(from_location, to_location)
            last_order_uuid = requests.post(
                url=endpoints.orders(),
                headers=auth_header,
                json={
                    "type": 1,
                    "tariff_code": tariff_code,
                    "from_location": from_location,
                    "to_location": to_location,
                    "packages": packages,
                    "recipient": recipient,
                    "sender": sender,
                },
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            ).json()["entity"]["uuid"]
        return last_order_uuid

    return _get_order_uuid


@pytest.fixture
def get_order_state(auth_header, endpoints):
    def _get_order_state(uuid):
        return requests.get(
            url=endpoints.order(uuid),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        ).json()["requests"][0]["state"]

    return _get_order_state


@pytest.fixture
def get_cdek_number(auth_header, endpoints):
    def _get_cdek_number(uuid):
        return requests.get(
            url=endpoints.order(uuid),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        ).json()["entity"]["cdek_number"]

    return _get_cdek_number
