import csv
from pathlib import Path


class ExportService:
    @staticmethod
    def export_results_csv(
        box,
        file_path,
        dim_formatter=lambda value: value,
        weight_formatter=lambda value: value,
        number_formatter=lambda value: value,
        units="Metric (cm)",
    ):
        summary_row = ExportService.build_summary_row(
            box,
            dim_formatter=dim_formatter,
            weight_formatter=weight_formatter,
            number_formatter=number_formatter,
            units=units,
        )
        ExportService.write_csv(file_path, summary_row)
        return 1

    @staticmethod
    def build_summary_row(box, dim_formatter, weight_formatter, number_formatter, units):
        packed_items = list(getattr(box, "items", []))
        unfitted_items = list(getattr(box, "unfitted_items", []))

        box_width = float(getattr(box, "width", 0))
        box_height = float(getattr(box, "height", 0))
        box_depth = float(getattr(box, "depth", 0))
        max_weight = float(getattr(box, "max_weight", 0))

        total_volume = box_width * box_height * box_depth
        used_volume = sum(float(i.width) * float(i.height) * float(i.depth) for i in packed_items)
        packed_weight = sum(float(getattr(i, "weight", 0)) for i in packed_items)

        volume_utilization = (used_volume / total_volume * 100) if total_volume else 0
        weight_utilization = (packed_weight / max_weight * 100) if max_weight else 0

        return {
            "container_id": getattr(box, "bin_id", ""),
            "container_width": number_formatter(dim_formatter(box_width)),
            "container_height": number_formatter(dim_formatter(box_height)),
            "container_depth": number_formatter(dim_formatter(box_depth)),
            "max_weight": number_formatter(weight_formatter(max_weight)),
            "fitted_items": len(packed_items),
            "unfitted_items": len(unfitted_items),
            "used_volume": number_formatter(dim_formatter(used_volume)),
            "total_volume": number_formatter(dim_formatter(total_volume)),
            "space_utilization_percent": number_formatter(round(volume_utilization, 2)),
            "packed_weight": number_formatter(weight_formatter(packed_weight)),
            "weight_utilization_percent": number_formatter(round(weight_utilization, 2)),
            "gravity_distribution": str(getattr(box, "gravity", "")),
            "units": units,
        }

    @staticmethod
    def write_csv(file_path, summary_row):
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            # ===== RESULTS FIRST =====
            "units",
            "fitted_items",
            "unfitted_items",
            "packed_weight",
            "weight_utilization_percent",
            "used_volume",
            "total_volume",
            "space_utilization_percent",
            "gravity_distribution",

            # ===== CONTAINER INFO =====
            "container_id",
            "container_width",
            "container_height",
            "container_depth",
            "max_weight",
        ]

        with file_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(summary_row)