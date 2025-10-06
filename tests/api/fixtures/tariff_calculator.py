# pyright: reportArgumentType=false
import random
from typing import List
import requests
import pytest

from database.models import DeliveryModeModel
from database.repository import DeliveryModeRepository
from tests.api.constants import DEFAULT_REQUEST_TIMEOUT_S
from tests.api.fixtures.token_manager import TokenManager


class TariffCalculator:
    def __init__(
        self,
        mode_repo: DeliveryModeRepository,
        token_manager: TokenManager,
    ) -> None:
        self.mode_repo = mode_repo
        self.token_manager = token_manager
        self._mode_payload_list = None

    def get_delivery_mode_payload_list(self) -> List[DeliveryModeModel]:
        if self._mode_payload_list:
            return self._mode_payload_list
        mode_payload_list = self.mode_repo.all()
        if not mode_payload_list:
            mode_payload_list = self.mode_repo.write_mode_list(self._fetch_mode_payload_list())
        return mode_payload_list

    def get_random_tariff_code(self):
        code_list = []
        mode_list = self.get_delivery_mode_payload_list()
        for mode in mode_list:
            if mode.tariff_code:
                code_list.append(mode.tariff_code)
        return random.choice(code_list)

    def _fetch_mode_payload_list(self):
        try:
            mode_list = []
            response = requests.get(
                url=self.token_manager.endpoints.all_tariffs(),
                headers=self.token_manager.auth_header,
                timeout=DEFAULT_REQUEST_TIMEOUT_S,
            )
            for tariff in response.json()["tariff_codes"]:
                mode_list.extend(tariff["delivery_modes"])
            return mode_list
        except requests.RequestException:
            pytest.raises(requests.RequestException)


@pytest.fixture
def tariff_calculator(token_manager, delivery_mode_repository):
    return TariffCalculator(delivery_mode_repository, token_manager)


@pytest.fixture
def tariff_code(tariff_calculator: TariffCalculator):
    return tariff_calculator.get_random_tariff_code()
