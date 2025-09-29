# pylint: disable=unused-argument
import json
import shutil
import os
import allure
import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Очистка при старте сессии тестов"""
    allure_results = "allure-results"
    if os.path.exists(allure_results):
        print(f"Очищаю {allure_results}")
        shutil.rmtree(allure_results)
    os.makedirs(allure_results, exist_ok=True)


# item == request.node в тесте
def pytest_runtest_teardown(item, nextitem):
    if hasattr(item, "callspec"):
        allure.attach(
            str(item.callspec.params),
            name="Test params",
            attachment_type=allure.attachment_type.TEXT,
        )
    for name, value in item.user_properties:
        if name == "request_params":
            allure.attach(
                json.dumps(value, indent=4, ensure_ascii=False),
                name="Request params",
                attachment_type=allure.attachment_type.JSON,
            )
        elif name == "response":
            allure.attach(
                str(value.request.headers),
                name="Request headers",
                attachment_type=allure.attachment_type.TEXT,
            )

            allure.attach(
                str(value.request.method),
                name="Request method",
                attachment_type=allure.attachment_type.TEXT,
            )

            allure.attach(
                str(value.request.body),
                name="Request body",
                attachment_type=allure.attachment_type.TEXT,
            )

            allure.attach(
                str(value.headers),
                name="Response headers",
                attachment_type=allure.attachment_type.TEXT,
            )

            allure.attach(
                json.dumps(value.json(), indent=4, ensure_ascii=False),
                name="Response body",
                attachment_type=allure.attachment_type.JSON,
            )
