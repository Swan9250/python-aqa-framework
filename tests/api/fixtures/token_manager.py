# pylint: disable=redefined-outer-name
# pyright: reportArgumentType=false
import os
import pytest
import requests

from yarl import URL
from database.repository import TokenRepository
from tests.api.api_urls import ApiUrls
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S


class TokenManager:

    def __init__(self, base_url: URL, token_repository: TokenRepository):
        self.base_url = base_url
        self.token_repo = token_repository
        self.endpoints = ApiUrls(base_url)
        self._token = None
        self._auth_header = None

    def get_token(self) -> str | None:
        auth_token = self.token_repo.get_last_token()
        if auth_token:
            return auth_token
        token_payload = self._fetch_new_token()
        if token_payload and token_payload.get("access_token"):
            self.token_repo.write_token(token_payload)
            return token_payload["access_token"]
        return None

    @property
    def token(self) -> str:
        if self._token is None:
            self._token = self.get_token()
            if not self._token:
                raise ValueError("Authentification token not available")
        return self._token

    @property
    def auth_header(self) -> dict[str, str]:
        if self._auth_header is None:
            self._auth_header = {"Authentification": f"Bearer {self.token}"}
        return self._auth_header.copy()

    def _fetch_new_token(self) -> dict:
        try:
            response = requests.post(
                url=self.endpoints.token(),
                params={
                    "grant_type": "client_credentials",
                    "client_id": os.getenv("ACCOUNT"),
                    "client_secret": os.getenv("PASSWORD"),
                },
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            pytest.fail(f"Failed to fetch token: {e}")
            return None


@pytest.fixture(scope="session")
def api_base_url() -> URL:
    return URL(os.getenv("API_BASE_URL"))


@pytest.fixture(scope="session")
def endpoints(api_base_url) -> ApiUrls:
    return ApiUrls(api_base_url)


@pytest.fixture(scope="session")
def token_manager(api_base_url: URL, token_repository: TokenRepository) -> TokenManager:
    return TokenManager(api_base_url, token_repository)


@pytest.fixture(scope="session")
def token(token_manager: TokenManager) -> str:
    auth_token = token_manager.get_token()
    if not auth_token:
        pytest.fail("Failed to obtain authentification token")
    return auth_token


@pytest.fixture(scope="session")
def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
