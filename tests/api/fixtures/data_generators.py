import random
import pytest
from enums.city import City
from enums.region import Region


@pytest.fixture
def region():
    return random.choice(list(Region)).value


@pytest.fixture
def city():
    return random.choice(list(City)).value


@pytest.fixture()
def packages():
    return [
        {
            "number": 1,
            "weight": 300,
            "length": 30,
            "width": 50,
            "height": 20,
            "package_id": 1,
            "comment": "For lovely user",
            "items": [
                {
                    "name": "item1",
                    "amount": 1,
                    "item_id": "1",
                    "feacn_code": "1",
                    "ware_key": "123456",
                    "payment": {"value": 30.00, "vat_sum": 5.00, "vat_rate": 20},
                    "cost": 30.0,
                    "weight": 295,
                }
            ],
        }
    ]


@pytest.fixture
def recipient():
    return {
        "name": "Vov Swan",
        "phones": [{"number": "88005553535"}],
    }


@pytest.fixture
def sender():
    return {
        "name": "Swan Vov",
        "company": "ООО Рога и Копыта",
        "phones": [{"number": "88005553535"}],
    }
