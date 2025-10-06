from time import sleep
import allure
import pytest
import requests
from enums.city import City
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S, DEFAULT_WAIT_TIMEOUT_S


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Локации")
@allure.title("Проверка подборки локации по названию города")
@pytest.mark.parametrize("city", [city.value for city in City])
def test_location_suggest_cities(auth_header, endpoints, city, request):
    with allure.step("Отправка запроса к API"):
        request_params = {"name": city}
        response = requests.get(
            url=endpoints.suggest_cities(),
            headers=auth_header,
            params=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Проверка: статус-код < 400"):
        assert response.ok
    with allure.step("Сбор данных для allure отчёта"):
        request.node.user_properties.append(("request_params", request_params))
        request.node.user_properties.append(("response", response))


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Локации")
@allure.title("Проверка получения списка регионов")
def test_location_regions(auth_header, endpoints, request):
    with allure.step("Отправка запроса к API"):
        response = requests.get(
            url=endpoints.regions(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Проверка: статус-код < 400"):
        assert response.ok
    with allure.step("Сбор данных для allure отчёта"):
        request.node.user_properties.append(("response", response))


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Локации")
@allure.title("Проверка получения почтовых индексов города")
def test_location_postal_codes(auth_header, endpoints, city_payload, city, request):
    with allure.step("Отправка запроса к API"):
        request_params = {"code": city_payload(city=city).code}
        response = requests.get(
            url=endpoints.postal_codes(),
            headers=auth_header,
            params=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Проверка: статус-код < 400"):
        assert response.ok
    with allure.step("Сбор данных для allure отчёта"):
        request.node.user_properties.append(("request_params", request_params))
        request.node.user_properties.append(("response", response))


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Локации")
@allure.title("Проверка получения списка населённых пунктов")
def test_location_cities(auth_header, endpoints, request):
    with allure.step("Отправка запроса к API"):
        response = requests.get(
            url=endpoints.cities(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Проверка: статус-код < 400"):
        assert response.ok
    with allure.step("Сбор данных для allure отчёта"):
        request.node.user_properties.append(("response", response))


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Локации")
@allure.title("Проверка получения списка офисов")
def test_delivery_points(auth_header, endpoints, request):
    with allure.step("Отправка запроса к API"):
        response = requests.get(
            url=endpoints.delivery_points(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Проверка: статус-код < 400"):
        assert response.ok
    with allure.step("Сбор данных для allure отчёта"):
        request.node.user_properties.append(("response", response))


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Расчёт стоимости доставки")
@allure.title("Проверка расчёта по доступным тарифам")
def test_calculate_tariff_list(auth_header, endpoints, city_payload, packages, request):
    with allure.step("Отправка запроса к API"):
        from_location = city_payload()
        to_location = city_payload()
        delivery_packages = packages(from_location, to_location)
        request_params = {
            "from_location": from_location.to_dict(),
            "to_location": to_location.to_dict(),
            "packages": delivery_packages,
        }
        response = requests.post(
            url=endpoints.tariff_list(),
            headers=auth_header,
            json=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
    with allure.step("Проверка: статус-код < 400"):
        assert response.ok
    with allure.step("Сбор данных для allure отчёта"):
        request.node.user_properties.append(("request_params", request_params))
        request.node.user_properties.append(("response", response))


@allure.feature("Валидация http статус-кодов СДЕК API")
@allure.story("Расчёт стоимости доставки")
@allure.title("Проверка расчёта по коду тарифа")
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
        delivery_packages = packages(from_location, to_location)
    with allure.step("Send request to API"):
        request_params = {
            "tariff_code": tariff_code,
            "from_location": from_location.to_dict(),
            "to_location": to_location.to_dict(),
            "packages": delivery_packages,
        }
        print(request_params["packages"])
        request.node.user_properties.append(("request_params", request_params))
        response = requests.post(
            url=endpoints.tariff(),
            headers=auth_header,
            json=request_params,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        print(response.json())
        errors = response.json().get("errors")
        if errors:
            for error in errors:
                if error["code"] == "err_result_service_empty":
                    pytest.xfail(error["message"])
                else:
                    assert response.ok
        request.node.user_properties.append(("response", response))
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


def test_all_tariffs(auth_header, endpoints, delivery_mode_repository):
    with allure.step("Send request to API"):
        response = requests.get(
            url=endpoints.all_tariffs(),
            headers=auth_header,
            timeout=DEFAULT_REQUEST_TIMEOUT_S,
        )
        # print(response.json()["tariff_codes"])
        mode_list = []
        for tariff in response.json()["tariff_codes"]:
            mode_list.extend(tariff["delivery_modes"])
        print(mode_list)
        delivery_mode_repository.write_mode_list(mode_list)
    with allure.step("Check Status Code < 400"):
        assert response.ok


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
