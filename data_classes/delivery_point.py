from dataclasses import dataclass


@dataclass
class DeliveryPoint:
    code: str = "PSK1"
    postal_code: int = 180005
    is_dressing_room: bool = False
