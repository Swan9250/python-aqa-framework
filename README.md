# python-aqa-framework

## Simple UI test

```python
from pages.main import MainPage


def test_open_main_page(browser):
    main_page = MainPage(browser)
    browser.get(main_page.URL.human_repr())
    assert main_page.get_header().is_displayed(), "Header is not displayed"
    assert main_page.get_work_area().is_displayed(), "Work area is not displayed"
    assert main_page.get_footer().is_displayed(), "Footer is not displayed"
    assert main_page.get_logo().is_displayed(), "Logo is not displayed"
```

## Simple API test

```python
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
```

## Allure report example
<img width="1918" height="952" alt="Снимок экрана от 2025-09-09 17-06-21" src="https://github.com/user-attachments/assets/e744098a-4638-4c6f-9490-bd1abb2f8339" />
