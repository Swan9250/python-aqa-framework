# pyright: reportArgumentType=false
import random
import requests
import pytest

from database.repository import TariffRepository
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S
from tests.api.fixtures.location_manager import LocationManager
from tests.api.fixtures.token_manager import TokenManager


class TariffCalculator:
    def __init__(
        self,
        tariff_repo: TariffRepository,
        location_manager: LocationManager,
        token_manager: TokenManager,
    ) -> None:
        self.tariff_repo = tariff_repo
        self.location_manager = location_manager
        self.token_manager = token_manager
        self._tariff_payload_list = None

    def get_tariff_payload_list(self, from_location, to_location, packages):
        if self._tariff_payload_list:
            return self._tariff_payload_list
        tariff_payload_list = self.tariff_repo.all()
        if not tariff_payload_list:
            tariff_payload_list = self.tariff_repo.write_tariff_list(
                self._fetch_tariff_payload_list(from_location, to_location, packages),
                from_location["code"],
                to_location["code"],
            )
        self._tariff_payload_list = tariff_payload_list
        return tariff_payload_list

    def _fetch_tariff_payload_list(self, from_location, to_location, packages):
        try:
            response = requests.post(
                url=self.token_manager.endpoints.tariff_list(),
                headers=self.token_manager.auth_header,
                json={
                    "from_location": from_location,
                    "to_location": to_location,
                    "packages": packages,
                },
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            return response.json()["tariff_codes"]
        except (requests.RequestException, ValueError) as e:
            pytest.raises(f"Fail to fetch tariff codes {e}")


@pytest.fixture
def tariff_calculator(location_manager, token_manager, tariff_repository):
    return TariffCalculator(tariff_repository, location_manager, token_manager)


@pytest.fixture
def tariff_code(tariff_calculator: TariffCalculator):
    def _tariff_code(from_location, to_location, packages):
        tariff_payload_list = tariff_calculator.get_tariff_payload_list(
            from_location, to_location, packages
        )
        return random.choice(tariff_payload_list).tariff_code

    return _tariff_code
