from sqlalchemy import Column, String, Enum, Text, func, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"

    uuid = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=func.now())  # pylint: disable=not-callable
    state = Column(Enum("ACCEPTED", "INVALID"))

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "created_at": self.created_at,
            "state": self.state,
        }


class AuthTokenModel(Base):
    __tablename__ = "auth_tokens"

    access_token = Column(Text)
    token_type = Column(String(100))
    expired_at = Column(DateTime)
    scope = Column(String(100))
    jti = Column(String(100), primary_key=True)

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expired_at": self.expired_at,
            "scope": self.scope,
            "jti": self.jti,
        }
