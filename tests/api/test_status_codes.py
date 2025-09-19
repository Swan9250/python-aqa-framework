from time import sleep
import allure
import pytest
import requests
from data_classes.delivery_point import DeliveryPoint
from enums.city import City
from enums.country_code import CountryCode
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S, DEFAULT_WAIT_TIMEOUT_S


@allure.feature("CDEK API Tests")
@allure.story("Status Code Validation")
@allure.title("Check suggest cities response is ok")
@pytest.mark.parametrize("city", [city.value for city in City])
def test_location_suggest_cities(auth_header, endpoints, city, attach_info):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.suggest_cities(),
            headers=auth_header,
            params={"name": city},
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


@allure.title("Check get regions info response is ok")
def test_location_regions(auth_header, endpoints, attach_info):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.regions(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


@allure.title("Check get location postal codes response is ok")
def test_location_postal_codes(
    auth_header, endpoints, get_city_code, city, attach_info
):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.postal_codes(),
            headers=auth_header,
            params={"code": get_city_code(city)},
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


@allure.title("Check get location cities response is ok")
def test_location_cities(
    auth_header, endpoints, city, get_postal_code, get_city_code, attach_info
):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.cities(),
            headers=auth_header,
            params={
                "country_codes": [CountryCode.RU.value],
                "postal_code": get_postal_code(get_city_code(city)),
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


@pytest.mark.parametrize("delivery_point", [DeliveryPoint("PSK1", 180005, True)])
def test_delivery_points(auth_header, endpoints, delivery_point, attach_info):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.delivery_points(),
            headers=auth_header,
            params={
                "code": delivery_point.code,
                "postal_code": delivery_point.postal_code,
                "is_dressing_room": delivery_point.is_dressing_room,
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_calculate_tariff_list(
    auth_header, endpoints, get_delivery_points, packages, attach_info
):
    with allure.step("Collect data: location from, location to, packages"):
        delivery_points = get_delivery_points(City.PSKOV.value)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
    with allure.step("Send request to API"):
        response = requests.post(
            url=endpoints.tariff_list(),
            headers=auth_header,
            json={
                "from_location": from_location,
                "to_location": to_location,
                "packages": packages,
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_calculate_tariff(
    auth_header,
    endpoints,
    get_tariff_code,
    get_delivery_points,
    packages,
    attach_info,
):
    with allure.step("Collect data: tariff_code, location from, location to, packages"):
        tariff_code = get_tariff_code(City.PSKOV.value)
        delivery_points = get_delivery_points(City.PSKOV.value)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
    with allure.step("Send request to API"):
        response = requests.post(
            url=endpoints.tariff(),
            headers=auth_header,
            json={
                "tariff_code": tariff_code,
                "from_location": from_location,
                "to_location": to_location,
                "packages": packages,
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_calculate_tariff_and_service(
    auth_header, endpoints, get_delivery_points, packages, attach_info
):
    with allure.step("Collect data: location from, location to, packages"):
        delivery_points = get_delivery_points(City.PSKOV.value)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
    with allure.step("Send request to API"):
        response = requests.post(
            url=endpoints.tariff_and_service(),
            headers=auth_header,
            json={
                "services": [{"code": "CARTON_BOX_XS", "parameter": 1}],
                "from_location": from_location,
                "to_location": to_location,
                "packages": packages,
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_all_tariffs(auth_header, endpoints, attach_info):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.all_tariffs(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_international_package_restrictions(
    auth_header, endpoints, get_tariff_code, get_delivery_points, packages, attach_info
):
    with allure.step("Collect data: tariff_code, location from, location to, packages"):
        delivery_points = get_delivery_points(City.MOSCOW.value)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
        tariff_code = get_tariff_code(City.MOSCOW.value)
    with allure.step("Send request to API"):
        response = requests.post(
            url=endpoints.restrictions(),
            headers=auth_header,
            json={
                "tariff_code": int(tariff_code),
                "from_location": from_location,
                "to_location": to_location,
                "packages": packages,
            },
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_register_order(
    auth_header,
    endpoints,
    get_tariff_code,
    get_delivery_points,
    packages,
    recipient,
    sender,
    order_repository,
    attach_info,
):
    with allure.step("Collect data: tariff_code, location from, location to, packages"):
        tariff_code = get_tariff_code(City.MOSCOW.value)
        delivery_points = get_delivery_points(City.MOSCOW.value)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
    with allure.step("Send request to API"):
        response = requests.post(
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
        )
        order_repository.create_order(
            {
                "uuid": response.json()["entity"]["uuid"],
                "state": response.json()["requests"][0]["state"],
            }
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_order(auth_header, endpoints, get_order_uuid, attach_info):
    with allure.step("Collect data: uuid"):
        uuid = get_order_uuid(City.MOSCOW.value)
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.order(uuid),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_get_orders(
    auth_header,
    endpoints,
    get_order_uuid,
    get_cdek_number,
    get_order_state,
    attach_info,
):
    with allure.step("Collect data: order_uuid, order_state, cdek_number"):
        order_uuid = get_order_uuid(City.MOSCOW.value)
        order_state = get_order_state(order_uuid)
        while order_state != "SUCCESSFUL":
            sleep(DEFAULT_WAIT_TIMEOUT_S)
            order_state = get_order_state(order_uuid)
        cdek_number = get_cdek_number(order_uuid)
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.orders(),
            headers=auth_header,
            params={"cdek_number": cdek_number},
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)


def test_change_order(
    auth_header,
    endpoints,
    get_tariff_code,
    get_delivery_points,
    packages,
    recipient,
    sender,
    attach_info,
):
    with allure.step("Collect data: tariff_code, location from, location to, packages"):
        tariff_code = get_tariff_code(City.MOSCOW.value)
        delivery_points = get_delivery_points(City.MOSCOW.value)
        from_location = delivery_points[0].get("location")
        to_location = delivery_points[-1].get("location")
    with allure.step("Send request to API"):
        response = requests.post(
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
        )

    with allure.step("Check Status Code < 400"):
        assert response.ok

    attach_info(response)
