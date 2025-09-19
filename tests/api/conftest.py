# pylint: disable=redefined-outer-name
# pyright: reportArgumentType=false
import json
import os
import random
from typing import Callable, List
import allure
import pytest
import requests
from yarl import URL
from database.db_session import ScopedSession, engine
from database.models import OrderModel
from database.repository import (
    CityRepository,
    OrderRepository,
    PostalCodeRepository,
    TokenRepository,
)
from enums.city import City
from enums.region import Region
from tests.api.api_urls import ApiUrls
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S


@pytest.fixture(scope="session")
def endpoints() -> ApiUrls:
    base_url = URL(os.getenv("API_BASE_URL"))
    return ApiUrls(base_url)


@pytest.fixture(scope="session")
def auth_header(endpoints: ApiUrls, token_repository: TokenRepository) -> dict:
    token = token_repository.get_last_token()
    if token is None:
        response = requests.post(
            url=endpoints.token(),
            params={
                "grant_type": "client_credentials",
                "client_id": os.getenv("ACCOUNT"),
                "client_secret": os.getenv("PASSWORD"),
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        token_repository.write_token(response.json())
        token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def region():
    return random.choice(list(Region)).value


@pytest.fixture
def city():
    return random.choice(list(City)).value


@pytest.fixture
def attach_info():
    def _attach_info(response):
        allure.attach(
            str(response.request.headers),
            name="Request headers",
            attachment_type=allure.attachment_type.TEXT,
        )

        allure.attach(
            str(response.request.method),
            name="Request method",
            attachment_type=allure.attachment_type.TEXT,
        )

        allure.attach(
            str(response.request.body),
            name="Request body",
            attachment_type=allure.attachment_type.TEXT,
        )

        allure.attach(
            str(response.headers),
            name="Response headers",
            attachment_type=allure.attachment_type.TEXT,
        )

        allure.attach(
            json.dumps(response.json(), indent=4, ensure_ascii=False),
            name="Response body",
            attachment_type=allure.attachment_type.JSON,
        )

    return _attach_info


@pytest.fixture
def get_city_code(
    auth_header, endpoints: ApiUrls, city_repository: CityRepository
) -> Callable[[str], int]:
    def _get_city_code(city: str) -> int:
        city_code = city_repository.get_code_by_city(city)
        if city_code is None:
            response = requests.get(
                url=endpoints.suggest_cities(),
                headers=auth_header,
                params={"name": city},
                timeout=100,
            )
            city_repository.write_city(response.json())
            city_code = int(response.json()[0].get("code"))
        return city_code

    return _get_city_code


@pytest.fixture
def get_postal_code(auth_header, endpoints, postal_code_repository):
    def _get_postal_code(city_code):
        postal_codes: list = postal_code_repository.get_codes_by_city_code(city_code)
        if postal_codes:
            return random.choice(postal_codes)
        response = requests.get(
            url=endpoints.postal_codes(),
            headers=auth_header,
            params={"code": city_code},
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        postal_code_repository.write_postal_code(response.json())
        return random.choice(response.json()["postal_codes"])

    return _get_postal_code


@pytest.fixture
def get_delivery_points(
    auth_header, endpoints: ApiUrls, get_postal_code, get_city_code
):
    def _get_delivery_points(city):
        return requests.get(
            url=endpoints.delivery_points(),
            headers=auth_header,
            params={
                "postal_code": get_postal_code(get_city_code(city)),
            },
            timeout=100,
        ).json()

    return _get_delivery_points


@pytest.fixture
def get_tariff_code(
    auth_header,
    endpoints,
    get_delivery_points,
    packages,
):
    def _get_tariff_code(city):
        delivery_points = get_delivery_points(city)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
        return requests.post(
            url=endpoints.tariff_list(),
            headers=auth_header,
            json={
                "from_location": from_location,
                "to_location": to_location,
                "packages": packages,
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        ).json()["tariff_codes"][0]["tariff_code"]

    return _get_tariff_code


@pytest.fixture()
def packages():
    return [
        {
            "number": 1,
            "weight": 300,
            "length": 30,
            "width": 50,
            "height": 20,
            "package_id": 1,
            "comment": "For lovely user",
            "items": [
                {
                    "name": "item1",
                    "amount": 1,
                    "item_id": "1",
                    "feacn_code": "1",
                    "ware_key": "123456",
                    "payment": {"value": 30.00, "vat_sum": 5.00, "vat_rate": 20},
                    "cost": 30.0,
                    "weight": 295,
                }
            ],
        }
    ]


@pytest.fixture
def recipient():
    return {
        "name": "Vov Swan",
        "phones": [{"number": "88005553535"}],
    }


@pytest.fixture
def sender():
    return {
        "name": "Swan Vov",
        "company": "ООО Рога и Копыта",
        "phones": [{"number": "88005553535"}],
    }


@pytest.fixture
def get_order_uuid(
    auth_header,
    endpoints,
    get_tariff_code,
    get_delivery_points,
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
            tariff_code = get_tariff_code(city)
            delivery_points = get_delivery_points(city)
            from_location = delivery_points[0].get("location")
            to_location = delivery_points[-1].get("location")
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


@pytest.fixture(scope="session")
def db_session():
    connection = engine.connect()

    session = ScopedSession(bind=connection)

    yield session

    session.close()
    connection.close()
    ScopedSession.remove()


@pytest.fixture(scope="session")
def order_repository(db_session):
    return OrderRepository(db_session)


@pytest.fixture(scope="session")
def token_repository(db_session):
    return TokenRepository(db_session)


@pytest.fixture(scope="session")
def city_repository(db_session):
    return CityRepository(db_session)


@pytest.fixture(scope="session")
def postal_code_repository(db_session):
    return PostalCodeRepository(db_session)
