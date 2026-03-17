class ResultService:
    @staticmethod
    def calculate_summary(box):
        fitted = len(box.items)
        unfitted = len(box.unfitted_items)
        used_volume = sum(float(i.width) * float(i.height) * float(i.depth) for i in box.items)
        total_volume = float(box.width) * float(box.height) * float(box.depth)
        utilization = (used_volume / total_volume * 100) if total_volume else 0

        return {
            "fitted": fitted,
            "unfitted": unfitted,
            "used_volume": used_volume,
            "total_volume": total_volume,
            "utilization": utilization,
            "gravity": box.gravity,
        }

    @staticmethod
    def build_results_lines(box, dim_formatter, weight_formatter, number_formatter):
        summary = ResultService.calculate_summary(box)

        disp_box_w = number_formatter(dim_formatter(box.width))
        disp_box_h = number_formatter(dim_formatter(box.height))
        disp_box_d = number_formatter(dim_formatter(box.depth))
        disp_box_weight = number_formatter(weight_formatter(box.max_weight))

        lines = [
            f"Container: {box.bin_id}",
            f"Size: {disp_box_w} x {disp_box_h} x {disp_box_d}",
            f"Max Weight: {disp_box_weight}",
            "",
            f"Fitted Items: {summary['fitted']}",
            f"Unfitted Items: {summary['unfitted']}",
            f"Space Utilization: {summary['utilization']:.2f}%",
            f"Gravity Distribution: {summary['gravity']}",
            "",
            "=== FITTED ===",
        ]

        for item in box.items:
            disp_w = number_formatter(dim_formatter(item.width))
            disp_h = number_formatter(dim_formatter(item.height))
            disp_d = number_formatter(dim_formatter(item.depth))
            lines.append(
                f"{item.item_id} | pos={item.position} | size={disp_w}x{disp_h}x{disp_d} | rot={item.rotation_type}"
            )

        lines.append("")
        lines.append("=== UNFITTED ===")

        for item in box.unfitted_items:
            disp_w = number_formatter(dim_formatter(item.width))
            disp_h = number_formatter(dim_formatter(item.height))
            disp_d = number_formatter(dim_formatter(item.depth))
            lines.append(f"{item.item_id} | size={disp_w}x{disp_h}x{disp_d}")

        return lines

    @staticmethod
    def build_results_text(box, dim_formatter, weight_formatter, number_formatter):
        return "\n".join(
            ResultService.build_results_lines(
                box,
                dim_formatter=dim_formatter,
                weight_formatter=weight_formatter,
                number_formatter=number_formatter,
            )
        )