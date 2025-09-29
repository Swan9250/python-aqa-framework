from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Enum,
    Text,
    func,
    DateTime,
)
from sqlalchemy.dialects.mysql import INTEGER, BIGINT
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

    access_token = Column(Text, nullable=False)
    token_type = Column(String(100))
    expired_at = Column(DateTime, nullable=False)
    scope = Column(String(100))
    jti = Column(String(100), primary_key=True, nullable=False)

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
    country_code = Column(Enum(CountryCode))
    city = Column(String(100))
    fias_guid = Column(String(36))
    region = Column(String(100))
    region_code = Column(INTEGER(unsigned=True))
    fias_region_guid = Column(String(36))
    sub_region = Column(String(100))
    longitude = Column(Float)
    latitude = Column(Float)
    time_zone = Column(String(100))
    payment_limit = Column(Float)
    country = Column(String(100))
    kladr_code = Column(BIGINT(unsigned=True))

    def to_dict(self):
        return {
            "city_uuid": self.city_uuid,
            "code": self.code,
            "country_code": self.country_code.value if self.country_code else None,
            "city": self.city,
            "fias_guid": self.fias_guid,
            "region": self.region,
            "region_code": self.region_code,
            "fias_region_guid": self.fias_region_guid,
            "sub_region": self.sub_region,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "time_zone": self.time_zone,
            "payment_limit": self.payment_limit,
            "country": self.country,
            "kladr_code": self.kladr_code,
        }


class PostalCodeModel(Base):
    __tablename__ = "postal_codes"

    city_code = Column(INTEGER(unsigned=True), ForeignKey("cities.code"))
    postal_code = Column(String(100), primary_key=True)
    # связь для orm, чтобы можно было делать так: postal_code.city.full_name
    city = relationship("CityModel", backref="postal_codes")


class DeliveryPointModel(Base):
    __tablename__ = "delivery_points"

    code = Column(String(255), primary_key=True)
    uuid = Column(String(255), unique=True)
    address_comment = Column(String(255))
    nearest_station = Column(String(255))
    nearest_metro_station = Column(String(255))
    work_time = Column(String(255))
    phones = Column(JSON)
    email = Column(String(255))
    note = Column(String(255))
    type = Column(Enum("PVZ", "POSTAMAT"))
    owner_code = Column(String(255))
    take_only = Column(Boolean)
    is_handout = Column(Boolean)
    is_reception = Column(Boolean)
    is_dressing_room = Column(Boolean)
    is_marketplace = Column(Boolean)
    is_ltl = Column(Boolean)
    have_cashless = Column(Boolean)
    have_cash = Column(Boolean)
    have_fast_payment_system = Column(Boolean)
    allowed_cod = Column(Boolean)
    site = Column(String(255))
    office_image_list = Column(JSON)
    work_time_list = Column(JSON)
    work_time_exception_list = Column(JSON)
    weight_min = Column(Float)
    weight_max = Column(Float)
    dimensions = Column(JSON)
    errors = Column(JSON)
    warnings = Column(JSON)
    location = Column(JSON)
    distance = Column(INTEGER(unsigned=True))
    fulfillment = Column(Boolean)
    city_code = Column(INTEGER(unsigned=True), ForeignKey("cities.code"))
    city = relationship("CityModel", backref="delivery_points")


def to_dict(self):
    return {
        "code": self.code,
        "uuid": self.uuid,
        "address_comment": self.address_comment,
        "nearest_station": self.nearest_station,
        "nearest_metro_station": self.nearest_metro_station,
        "work_time": self.work_time,
        "phones": self.phones,
        "email": self.email,
        "note": self.note,
        "type": self.type,
        "owner_code": self.owner_code,
        "take_only": self.take_only,
        "is_handout": self.is_handout,
        "is_reception": self.is_reception,
        "is_dressing_room": self.is_dressing_room,
        "is_marketplace": self.is_marketplace,
        "is_ltl": self.is_ltl,
        "have_cashless": self.have_cashless,
        "have_cash": self.have_cash,
        "have_fast_payment_system": self.have_fast_payment_system,
        "allowed_cod": self.allowed_cod,
        "site": self.site,
        "office_image_list": self.office_image_list,
        "work_time_list": self.work_time_list,
        "work_time_exception_list": self.work_time_exception_list,
        "weight_min": self.weight_min,
        "weight_max": self.weight_max,
        "dimensions": self.dimensions,
        "errors": self.errors,
        "warnings": self.warnings,
        "location": self.location,
        "distance": self.distance,
        "fulfillment": self.fulfillment,
    }


class TariffModel(Base):
    __tablename__ = "tariffs"

    tariff_code = Column(INTEGER(unsigned=True), primary_key=True)
    tariff_name = Column(String(255))
    tariff_description = Column(String(255))
    delivery_mode = Column(Integer)
    delivery_sum = Column(Float)
    period_min = Column(Integer)
    period_max = Column(Integer)
    calendar_min = Column(Integer)
    calendar_max = Column(Integer)
    delivery_date_range = Column(JSON)
    from_city_code = Column(INTEGER(unsigned=True), ForeignKey("cities.code"))
    to_city_code = Column(INTEGER(unsigned=True), ForeignKey("cities.code"))
    from_city = relationship(
        "CityModel", foreign_keys=[from_city_code], backref="tariffs_from"
    )
    to_city = relationship(
        "CityModel", foreign_keys=[to_city_code], backref="tariffs_to"
    )
