import pytest
import requests
from tests.enums.city import City


@pytest.mark.parametrize("city", [city.value for city in City])
def test_country_code_by_city(auth_token, api_url, city):
    city_url = api_url / "v2/location/suggest/cities"
    res = requests.get(
        url=city_url,
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"name": city},
        timeout=100,
    )
    assert res.json()[0].get("country_code") == "RU"
