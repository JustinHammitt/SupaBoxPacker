from py3dbp import Packer, Bin, Item

from models import ContainerSpec, ItemSpec


def build_bin(spec: ContainerSpec) -> Bin:
    return Bin(
        partno=spec.name,
        WHD=(spec.width, spec.height, spec.depth),
        max_weight=spec.max_weight,
        corner=spec.corner,
    )


def build_items(items: list[ItemSpec]) -> list[Item]:
    built: list[Item] = []

    for spec in items:
        for i in range(spec.quantity):
            built.append(
                Item(
                    partno=f"{spec.name}-{i + 1}",
                    name=spec.name,
                    typeof="cube",
                    WHD=(spec.width, spec.height, spec.depth),
                    weight=spec.weight,
                    level=1,
                    loadbear=100,
                    updown=spec.updown,
                    color=spec.color,
                )
            )

    return built


def run_packing(container: ContainerSpec, items: list[ItemSpec], bigger_first: bool = True, distribute_items: bool = False):
    packer = Packer()

    box = build_bin(container)
    packer.addBin(box)

    for item in build_items(items):
        packer.addItem(item)

    packer.pack(
        bigger_first=bigger_first,
        distribute_items=distribute_items,
    )

    return box