# services/unit_service.py

CM_PER_INCH = 2.54
KG_PER_LB = 0.45359237

METRIC = "Metric (cm)"
IMPERIAL = "Imperial (in)"


class UnitService:
    @staticmethod
    def is_metric_display(unit_name):
        return unit_name == METRIC

    @staticmethod
    def display_to_metric_dim(value, unit_name):
        value = float(value)
        if UnitService.is_metric_display(unit_name):
            return value
        return value * CM_PER_INCH

    @staticmethod
    def metric_to_display_dim(value, unit_name):
        value = float(value)
        if UnitService.is_metric_display(unit_name):
            return value
        return value / CM_PER_INCH

    @staticmethod
    def display_to_metric_weight(value, unit_name):
        value = float(value)
        if UnitService.is_metric_display(unit_name):
            return value
        return value * KG_PER_LB

    @staticmethod
    def metric_to_display_weight(value, unit_name):
        value = float(value)
        if UnitService.is_metric_display(unit_name):
            return value
        return value / KG_PER_LB

    @staticmethod
    def fmt_display(value):
        value = round(float(value), 4)

        # Snap very-close whole numbers to the whole number
        if abs(value - round(value)) < 0.0002:
            value = round(value)

        return f"{value:.4f}".rstrip("0").rstrip(".")

    @staticmethod
    def convert_display_dim_value(value, from_unit, to_unit):
        try:
            value = float(value)
        except Exception:
            return value

        if from_unit == to_unit:
            return UnitService.fmt_display(value)

        if from_unit == IMPERIAL and to_unit == METRIC:
            return UnitService.fmt_display(value * CM_PER_INCH)

        if from_unit == METRIC and to_unit == IMPERIAL:
            return UnitService.fmt_display(value / CM_PER_INCH)

        return UnitService.fmt_display(value)

    @staticmethod
    def convert_display_weight_value(value, from_unit, to_unit):
        try:
            value = float(value)
        except Exception:
            return value

        if from_unit == to_unit:
            return UnitService.fmt_display(value)

        if from_unit == IMPERIAL and to_unit == METRIC:
            return UnitService.fmt_display(value * KG_PER_LB)

        if from_unit == METRIC and to_unit == IMPERIAL:
            return UnitService.fmt_display(value / KG_PER_LB)

        return UnitService.fmt_display(value)

    @staticmethod
    def get_label_units(unit_name):
        if unit_name == METRIC:
            return "cm", "kg"
        return "in", "lb"