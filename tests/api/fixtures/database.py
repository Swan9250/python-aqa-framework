# pylint: disable=redefined-outer-name
import pytest
from database.db_session import ScopedSession, engine
from database.repository import (
    CityRepository,
    DeliveryModeRepository,
    DeliveryPointRepository,
    OrderRepository,
    TariffRepository,
    TokenRepository,
)


@pytest.fixture(scope="session")
def db_session():
    connection = engine.connect()
    session = ScopedSession(bind=connection)

    yield session

    session.close()
    connection.close()
    ScopedSession.remove()


@pytest.fixture(scope="session")
def order_repository(db_session):
    return OrderRepository(db_session)


@pytest.fixture(scope="session")
def token_repository(db_session):
    return TokenRepository(db_session)


@pytest.fixture(scope="session")
def city_repository(db_session):
    return CityRepository(db_session)


@pytest.fixture(scope="session")
def delivery_point_repository(db_session):
    return DeliveryPointRepository(db_session)


@pytest.fixture(scope="session")
def tariff_repository(db_session):
    return TariffRepository(db_session)

@pytest.fixture(scope="session")
def delivery_mode_repository(db_session):
    return DeliveryModeRepository(db_session)
