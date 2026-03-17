from py3dbp import Packer, Bin, Item

from services.fill_to_capacity_service import fill_single_item_to_capacity


class PackingService:
    @staticmethod
    def get_container_config(name, width, height, depth, max_weight, corner):
        return {
            "name": name or "MainBin",
            "WHD": [width, height, depth],
            "max_weight": max_weight,
            "corner": corner,
        }

    @staticmethod
    def validate_items(items):
        if not items:
            raise ValueError("Add at least one item before packing.")

        auto_items = [item for item in items if item.get("fill_to_max", False)]

        if len(auto_items) > 1:
            raise ValueError("Only one 'Fill to Max' item is supported right now.")

        if len(items) > 1 and auto_items:
            raise ValueError(
                "'Fill to Max' currently works only when it is the only item in the list."
            )

        return auto_items

    @staticmethod
    def apply_fill_to_max(container, items):
        auto_items = [item for item in items if item.get("fill_to_max", False)]
        if not auto_items:
            return items

        auto_item = auto_items[0]
        result = fill_single_item_to_capacity(
            container,
            dict(auto_item),
            max_search_qty=10000,
            bigger_first=True,
            distribute_items=False,
            fix_point=True,
            check_stable=False,
            support_surface_ratio=0.75,
            number_of_decimals=0,
        )
        auto_item["qty"] = int(result.fitted_count)
        return items

    @staticmethod
    def build_bin(container):
        return Bin(
            bin_id=container["name"],
            WHD=tuple(container["WHD"]),
            max_weight=container["max_weight"],
            corner=container["corner"],
            put_type=0,
        )

    @staticmethod
    def add_items_to_packer(packer, items):
        for item in items:
            for i in range(item["qty"]):
                packer.addItem(
                    Item(
                        item_id=f"{item['name']}-{i + 1}",
                        item_name=item["name"],
                        typeof="cube",
                        WHD=item["WHD"],
                        weight=item["weight"],
                        priority_level=1,
                        loadbear=100,
                        updown=item["updown"],
                        color=item["color"],
                    )
                )

    @staticmethod
    def pack(container, items):
        packer = Packer()
        box = PackingService.build_bin(container)
        packer.addBin(box)

        PackingService.add_items_to_packer(packer, items)

        packer.pack(
            bigger_first=True,
            distribute_items=False,
            fix_point=True,
            check_stable=False,
            support_surface_ratio=0.75,
            number_of_decimals=0,
        )

        return packer.bins[0]