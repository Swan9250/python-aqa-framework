# pyright: reportReturnType=false
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import desc, exists
from sqlalchemy.orm import Session
from database.models import (
    CityModel,
    DeliveryPointModel,
    OrderModel,
    AuthTokenModel,
    TariffModel,
)


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_order(self, order_data: dict) -> OrderModel:
        order = OrderModel(**order_data)
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def get_all_orders(self) -> List[OrderModel]:
        return (
            self.session.query(OrderModel)
            .where(OrderModel.created_at.isnot(None))
            .all()
        )


class TokenRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def write_token(self, token_data: dict) -> AuthTokenModel:
        token_data["expired_at"] = datetime.now() + timedelta(
            seconds=int(token_data["expires_in"])
        )
        del token_data["expires_in"]
        auth_token = AuthTokenModel(**token_data)
        self.session.add(auth_token)
        self.session.commit()
        self.session.refresh(auth_token)
        return auth_token

    def get_last_token_row(self) -> AuthTokenModel:
        return self.session.query(AuthTokenModel).order_by(desc("expired_at")).first()

    def is_expired(self, token_row: AuthTokenModel) -> bool:
        if token_row.expired_at is None:
            return True
        return token_row.expired_at < datetime.now()

    def get_last_token(self) -> str | None:
        token_row: AuthTokenModel = self.get_last_token_row()
        if token_row and not self.is_expired(token_row):
            return str(token_row.access_token)


class CityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def write_cities(self, cities) -> List[CityModel]:
        city_models = []
        for city_data in cities:
            if not self.exists(city_data["city_uuid"]):
                city = CityModel(**city_data)
                city_models.append(city)
                self.session.add(city)
                self.session.commit()
                self.session.refresh(city)
        return city_models

    def exists(self, uuid):
        return self.session.query(exists().where(CityModel.city_uuid == uuid)).scalar()

    def get_row_by_city(self, city: str) -> CityModel:
        return (
            self.session.query(CityModel).where(CityModel.city.contains(city)).first()
        )

    def get_code_by_city(self, city: str) -> int | None:
        city_row = self.get_row_by_city(city)
        if city_row:
            return city_row.code

    def all(self) -> List[CityModel]:
        return self.session.query(CityModel).all()


class DeliveryPointRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def write_delivery_points(
        self, delivery_points, city_code: int
    ) -> List[DeliveryPointModel]:
        delivery_point_models = []
        for point_data in delivery_points:
            point_data["city_code"] = city_code
            point = DeliveryPointModel(**point_data)
            delivery_point_models.append(point)
            self.session.add(point)
            self.session.commit()
            self.session.refresh(point)
        return delivery_point_models

    def get_delivery_points_by_city_code(self, city_code: int):
        return (
            self.session.query(DeliveryPointModel)
            .where(DeliveryPointModel.city_code == city_code)
            .all()
        )


class TariffRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def write_tariff_list(self, tariff_data: list, from_city_code, to_city_code):
        tariff_models = []
        for tariff_payload in tariff_data:
            tariff_payload["from_city_code"] = from_city_code
            tariff_payload["to_city_code"] = to_city_code
            tariff = TariffModel(**tariff_payload)
            tariff_models.append(tariff)
            self.session.add(tariff)
            self.session.commit()
            self.session.refresh(tariff)
        return tariff_models

    def get_tariff_list_by_city_codes(self, from_city_code, to_city_code):
        return (
            self.session.query(TariffModel)
            .where(
                TariffModel.from_city_code == from_city_code
                and TariffModel.to_city_code == to_city_code
            )
            .all()
        )

    def all(self) -> List[TariffModel]:
        return self.session.query(TariffModel).all()
