import random
from faker import Faker
import pytest
from database.models import CityModel
from enums.city import City
from enums.region import Region
from tests.api.constants import DEFAULT_WEIGHT_MIN_G

fake = Faker("ru_RU")

@pytest.fixture
def region():
    return random.choice(list(Region)).value


@pytest.fixture
def city():
    return random.choice(list(City)).value


@pytest.fixture
def payment() -> dict:
    value = fake.pyfloat(left_digits=7, right_digits=2, min_value=0)
    if value:
        vat_rate = random.choice([0, 5, 7, 10, 12, 20])
        vat_sum = round(value * vat_rate / 100, 2)
        payment = {"value": value, "vat_sum": vat_sum, "vat_rate": vat_rate}
    else:
        payment = {"value": value}
    return payment


@pytest.fixture
def items(payment):
    def _items(weight):
        max_item_weight = int(weight / 100)
        item_list = []
        item_count = fake.pyint(min_value=1, max_value=10)
        for item_id in range(item_count):
            item = {
                    "name": fake.bothify("Item ##??"),
                    "amount": fake.pyint(min_value=1, max_value=10),
                    "item_id": str(item_id),
                    "feacn_code": str(fake.random_number(digits=10, fix_len=True)),
                    "ware_key": str(fake.random_number(digits=fake.pyint(min_value=6, max_value=12), fix_len=True)),
                    "payment": payment,
                    "cost": payment["value"],
                    "weight": fake.pyint(min_value=DEFAULT_WEIGHT_MIN_G, max_value=max_item_weight, step=10),
                }
            item_list.append(item)
        return item_list
    return _items


@pytest.fixture()
def packages(packages_weight, items):
    def _packages(city_from: CityModel, city_to: CityModel):
        weight = packages_weight(city_from, city_to)
        item_list = items(weight)
        package_list = []
        package_count = fake.pyint(min_value=1, max_value=10)
        for number in range(package_count):
            package = {
                "number": str(number),
                "weight": weight,
                "length": 30,
                "width": 50,
                "height": 20,
                "package_id": 1,
                "comment": "For lovely user",
                "items": item_list,
            }
            package_list.append(package)
        return package_list
    return _packages

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
