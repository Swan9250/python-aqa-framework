import json
import os
import random
import allure
import pytest
import requests
from yarl import URL
from enums.region import Region
from tests.api.api_urls import ApiUrls


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
