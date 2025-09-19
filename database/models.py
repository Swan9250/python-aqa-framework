from sqlalchemy import Column, ForeignKey, String, Enum, Text, func, DateTime
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import declarative_base, relationship

from enums.country_code import CountryCode

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


class CityModel(Base):
    __tablename__ = "cities"

    city_uuid = Column(String(36), primary_key=True, nullable=False)
    code = Column(INTEGER(unsigned=True), unique=True)
    full_name = Column(Text)
    country_code = Column(Enum(CountryCode))

    def to_dict(self):
        return {
            "city_uuid": self.city_uuid,
            "code": self.code,
            "full_name": self.full_name,
            "country_code": self.country_code,
        }


class PostalCodeModel(Base):
    __tablename__ = "postal_codes"

    city_code = Column(INTEGER(unsigned=True), ForeignKey("cities.code"))
    postal_code = Column(String(100), primary_key=True)
    # связь для orm, чтобы можно было делать так: postal_code.city.full_name
    city = relationship("CityModel", backref="postal_codes")
