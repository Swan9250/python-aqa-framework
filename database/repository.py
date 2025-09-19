# pyright: reportReturnType=false
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import desc
from sqlalchemy.orm import Session
from database.models import (
    CityModel,
    OrderModel,
    AuthTokenModel,
    PostalCodeModel,
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
        self.sesion = session

    def write_city(self, cities) -> List[CityModel]:
        city_models = []
        for city_data in cities:
            city = CityModel(**city_data)
            city_models.append(city)
            self.sesion.add(city)
            self.sesion.commit()
            self.sesion.refresh(city)
        return city_models

    def get_row_by_city(self, city: str) -> CityModel:
        return (
            self.sesion.query(CityModel)
            .where(CityModel.full_name.contains(city))
            .first()
        )

    def get_code_by_city(self, city: str) -> int | None:
        city_row = self.get_row_by_city(city)
        if city_row:
            return city_row.code


class PostalCodeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def write_postal_code(self, postal_code_data) -> List[PostalCodeModel]:
        postal_code_models = []
        for postal_code in postal_code_data["postal_codes"]:
            postal_code_model = PostalCodeModel(
                city_code=postal_code_data["code"], postal_code=postal_code
            )
            postal_code_models.append(postal_code_model)
            self.session.add(postal_code_model)
            self.session.commit()
            self.session.refresh(postal_code_model)
        return postal_code_models

    def get_codes_by_city_code(self, city_code):
        return (
            self.session.query(PostalCodeModel.postal_code)
            .where(PostalCodeModel.city_code == city_code)
            .all()
        )
