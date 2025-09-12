# pylint: disable=redefined-outer-name
import json
import os
import random
import allure
import pytest
import requests
from yarl import URL
from enums.region import Region
from tests.api.api_urls import ApiUrls
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S


API_URL = URL(os.getenv("API_BASE_URL"))


@pytest.fixture(scope="session")
def endpoints():
    return ApiUrls(API_URL)


@pytest.fixture(scope="session")
def auth_header(endpoints: ApiUrls):
    response = requests.post(
        url=endpoints.token(),
        params={
            "grant_type": "client_credentials",
            "client_id": os.getenv("ACCOUNT"),
            "client_secret": os.getenv("PASSWORD"),
        },
        timeout=100,
    )
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def api_url():
    return API_URL


@pytest.fixture
def region():
    return random.choice(list(Region)).value


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
def get_city_code(auth_header, endpoints: ApiUrls):
    def _get_city_code(city):
        return (
            requests.get(
                url=endpoints.suggest_cities(),
                headers=auth_header,
                params={"name": city},
                timeout=100,
            )
            .json()[0]
            .get("code")
        )

    return _get_city_code


@pytest.fixture
def get_postal_code(auth_header, endpoints: ApiUrls, get_city_code):
    def _get_postal_code(city):
        return (
            requests.get(
                url=endpoints.postal_codes(),
                headers=auth_header,
                params={"code": get_city_code(city)},
                timeout=100,
            )
            .json()
            .get("postal_codes")[0]
        )

    return _get_postal_code


@pytest.fixture
def get_delivery_points(auth_header, endpoints: ApiUrls, get_postal_code):
    def _get_delivery_points(city):
        return requests.get(
            url=endpoints.delivery_points(),
            headers=auth_header,
            params={
                "postal_code": get_postal_code(city),
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
):
    def _get_order_uuid(city):
        tariff_code = get_tariff_code(city)
        delivery_points = get_delivery_points(city)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
        return requests.post(
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
