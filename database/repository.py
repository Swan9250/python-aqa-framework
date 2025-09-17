from datetime import datetime, timedelta
from typing import List
from sqlalchemy import desc
from sqlalchemy.orm import Session
from database.models import OrderModel, AuthTokenModel


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
        return (
            token_row.expired_at < datetime.now()
        )  # pyright: ignore[reportReturnType]

    def get_last_token(self) -> str | None:
        token_row: AuthTokenModel = self.get_last_token_row()
        if token_row and not self.is_expired(token_row):
            return str(token_row.access_token)
