from dataclasses import dataclass


@dataclass
class ContainerSpec:
    name: str
    width: float
    height: float
    depth: float
    max_weight: float
    corner: float = 0.0


@dataclass
class ItemSpec:
    name: str
    width: float
    height: float
    depth: float
    weight: float
    quantity: int = 1
    color: str = "#cccccc"
    updown: bool = True