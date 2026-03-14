# fill_to_capacity.py
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy

from py3dbp import Packer, Bin, Item


@dataclass
class FillResult:
    qty: int
    fitted_count: int
    unfitted_count: int
    utilization_pct: float
    packed_bin: object | None = None


class FillToCapacityError(Exception):
    pass


def _build_bin(container: dict) -> Bin:
    return Bin(
        partno=container["name"],
        WHD=tuple(container["WHD"]),
        max_weight=float(container["max_weight"]),
        corner=float(container.get("corner", 0)),
    )


def _build_item_copy(template: dict, copy_index: int) -> Item:
    return Item(
        partno=f'{template["name"]}-{copy_index + 1}',
        name=template["name"],
        typeof=template.get("typeof", "cube"),
        WHD=tuple(template["WHD"]),
        weight=float(template.get("weight", 0)),
        level=int(template.get("level", 1)),
        loadbear=float(template.get("loadbear", 999999)),
        updown=bool(template.get("updown", True)),
        color=template.get("color", "#FF6666"),
    )


def _run_pack(
    container: dict,
    item_template: dict,
    qty: int,
    *,
    bigger_first: bool = True,
    distribute_items: bool = False,
    fix_point: bool = True,
    check_stable: bool = True,
    support_surface_ratio: float = 0.75,
    number_of_decimals: int = 0,
) -> FillResult:
    packer = Packer()
    bin_obj = _build_bin(container)
    packer.addBin(bin_obj)

    for i in range(qty):
        packer.addItem(_build_item_copy(item_template, i))

    packer.pack(
        bigger_first=bigger_first,
        distribute_items=distribute_items,
        fix_point=fix_point,
        check_stable=check_stable,
        support_surface_ratio=support_surface_ratio,
        number_of_decimals=number_of_decimals,
    )

    fitted_count = len(bin_obj.items)
    unfitted_count = len(bin_obj.unfitted_items)

    bin_volume = float(bin_obj.width) * float(bin_obj.height) * float(bin_obj.depth)
    used_volume = 0.0
    for packed_item in bin_obj.items:
        used_volume += (
            float(packed_item.width)
            * float(packed_item.height)
            * float(packed_item.depth)
        )

    utilization_pct = (used_volume / bin_volume * 100.0) if bin_volume > 0 else 0.0

    return FillResult(
        qty=qty,
        fitted_count=fitted_count,
        unfitted_count=unfitted_count,
        utilization_pct=utilization_pct,
        packed_bin=bin_obj,
    )


def fill_single_item_to_capacity(
    container: dict,
    item_template: dict,
    *,
    max_search_qty: int = 10000,
    bigger_first: bool = True,
    distribute_items: bool = False,
    fix_point: bool = True,
    check_stable: bool = True,
    support_surface_ratio: float = 0.75,
    number_of_decimals: int = 0,
) -> FillResult:
    """
    Find the highest qty for a single repeated item that fully fits the container.

    Strategy:
      1. Exponential search to find an upper bound
      2. Binary search to find best fully-fitted qty
    """
    if max_search_qty < 1:
        raise FillToCapacityError("max_search_qty must be >= 1")

    base_item = deepcopy(item_template)
    base_item["qty"] = 1

    first = _run_pack(
        container,
        base_item,
        1,
        bigger_first=bigger_first,
        distribute_items=distribute_items,
        fix_point=fix_point,
        check_stable=check_stable,
        support_surface_ratio=support_surface_ratio,
        number_of_decimals=number_of_decimals,
    )
    if first.fitted_count < 1:
        return FillResult(qty=0, fitted_count=0, unfitted_count=1, utilization_pct=0.0)

    best = first
    low = 1
    high = 2

    while high <= max_search_qty:
        trial = _run_pack(
            container,
            base_item,
            high,
            bigger_first=bigger_first,
            distribute_items=distribute_items,
            fix_point=fix_point,
            check_stable=check_stable,
            support_surface_ratio=support_surface_ratio,
            number_of_decimals=number_of_decimals,
        )

        if trial.fitted_count == high:
            best = trial
            low = high
            high *= 2
        else:
            break

    if high > max_search_qty:
        high = max_search_qty

    while low + 1 <= high:
        mid = (low + high) // 2

        trial = _run_pack(
            container,
            base_item,
            mid,
            bigger_first=bigger_first,
            distribute_items=distribute_items,
            fix_point=fix_point,
            check_stable=check_stable,
            support_surface_ratio=support_surface_ratio,
            number_of_decimals=number_of_decimals,
        )

        if trial.fitted_count == mid:
            best = trial
            low = mid + 1
        else:
            high = mid - 1

    final_qty = best.fitted_count
    return _run_pack(
        container,
        base_item,
        final_qty,
        bigger_first=bigger_first,
        distribute_items=distribute_items,
        fix_point=fix_point,
        check_stable=check_stable,
        support_surface_ratio=support_surface_ratio,
        number_of_decimals=number_of_decimals,
    )