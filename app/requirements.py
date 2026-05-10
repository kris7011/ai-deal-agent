from dataclasses import dataclass


@dataclass
class ProductRequirements:
    product_type: str
    max_price: int
    must_have_mop: bool
    must_have_obstacle_avoidance: bool
    min_suction_pa: int
    must_handle_rugs: bool