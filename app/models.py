from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: int
    url: str
    image_url: str | None
    suction_pa: int | None
    has_mop: bool | None
    has_obstacle_avoidance: bool | None
    can_handle_rugs: bool | None
    rating: float | None
    source: str