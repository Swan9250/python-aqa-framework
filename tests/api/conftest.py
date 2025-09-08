import os
import pytest
import requests
from yarl import URL


API_URL = URL(os.getenv("API_BASE_URL"))


@pytest.fixture(scope="session")
def auth_token():
    auth_url = API_URL / "v2/oauth/token"
    response = requests.post(
        url=auth_url,
        params={
            "grant_type": "client_credentials",
            "client_id": os.getenv("ACCOUNT"),
            "client_secret": os.getenv("PASSWORD"),
        },
        timeout=100,
    )
    token = response.json().get("access_token")
    yield token


@pytest.fixture(scope="session")
def api_url():
    return API_URL
