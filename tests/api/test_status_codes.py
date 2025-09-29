from time import sleep
import allure
import pytest
import requests
from enums.city import City
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S, DEFAULT_WAIT_TIMEOUT_S


@allure.feature("CDEK API status code validation")
@allure.story("location")
@allure.title("Check suggest cities response is ok")
@pytest.mark.parametrize("city", [city.value for city in City])
def test_location_suggest_cities(auth_header, endpoints, city, request):
    with allure.step("Send request to API"):
        request_params = {"name": city}
        request.node.user_properties.append(("request_params", request_params))
        response = requests.get(
            url=endpoints.suggest_cities(),
            headers=auth_header,
            params=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
    with allure.step("Check Status Code < 400"):
        assert response.ok


@allure.story("location")
@allure.title("Check get regions info response is ok")
def test_location_regions(auth_header, endpoints, request):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.regions(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
    with allure.step("Check Status Code < 400"):
        assert response.ok


@allure.story("location")
@allure.title("Check get location postal codes response is ok")
def test_location_postal_codes(auth_header, endpoints, city_code, city, request):
    with allure.step("Send request to API"):
        request_params = {"code": city_code(city)}
        request.node.user_properties.append(("request_params", request_params))
        response = requests.get(
            url=endpoints.postal_codes(),
            headers=auth_header,
            params=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
    with allure.step("Check Status Code < 400"):
        assert response.ok


@allure.story("location")
@allure.title("Check get location cities response is ok")
def test_location_cities(auth_header, endpoints, request):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.cities(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
    with allure.step("Check Status Code < 400"):
        assert response.ok


# @pytest.mark.parametrize("delivery_point", [DeliveryPoint("PSK1", 180005, True)])
@allure.story("location")
def test_delivery_points(auth_header, endpoints, request):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.delivery_points(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
    with allure.step("Check Status Code < 400"):
        assert response.ok


@allure.story("calculation")
@allure.title("Check tariff list response is ok")
def test_calculate_tariff_list(auth_header, endpoints, city_payload, packages, request):
    with allure.step("Collect data: location from, location to"):
        from_location = city_payload()
        to_location = city_payload()
    with allure.step("Send request to API"):
        request_params = {
            "from_location": from_location,
            "to_location": to_location,
            "packages": packages,
        }
        request.node.user_properties.append(("request_params", request_params))
        response = requests.post(
            url=endpoints.tariff_list(),
            headers=auth_header,
            json=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
    with allure.step("Check Status Code < 400"):
        assert response.ok


def test_calculate_tariff(
    auth_header,
    endpoints,
    city_payload,
    tariff_code,
    packages,
    request,
):
    with allure.step("Collect data: tariff_code, location from, location to"):
        from_location = city_payload()
        to_location = city_payload()
        tariff_code = tariff_code(from_location, to_location, packages)
    with allure.step("Send request to API"):
        request_params = {
            "tariff_code": tariff_code,
            "from_location": from_location,
            "to_location": to_location,
            "packages": packages,
        }
        request.node.user_properties.append(("request_params", request_params))
        response = requests.post(
            url=endpoints.tariff(),
            headers=auth_header,
            json=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        request.node.user_properties.append(("response", response))
        print(response.json())
    with allure.step("Check Status Code < 400"):
        assert response.ok


def test_calculate_tariff_and_service(
    auth_header, endpoints, get_random_city, packages, attach_info
):
    with allure.step("Collect data: location from, location to"):
        from_location = get_random_city()
        to_location = get_random_city()
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
    auth_header, endpoints, get_random_city, get_tariff_code, packages, attach_info
):
    with allure.step("Collect data: tariff_code, location from, location to, packages"):
        from_location = get_random_city()
        to_location = get_random_city()
        tariff_code = get_tariff_code(from_location, to_location)
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
    get_random_city,
    get_tariff_code,
    packages,
    recipient,
    sender,
    order_repository,
    attach_info,
):
    with allure.step("Collect data: tariff_code, location from, location to"):
        from_location = get_random_city()
        to_location = get_random_city()
        tariff_code = get_tariff_code(from_location, to_location)
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
    get_random_city,
    get_tariff_code,
    packages,
    recipient,
    sender,
    attach_info,
):
    with allure.step("Collect data: tariff_code, location from, location to"):
        from_location = get_random_city()
        to_location = get_random_city()
        tariff_code = get_tariff_code(from_location, to_location)
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
