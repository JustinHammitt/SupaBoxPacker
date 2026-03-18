import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

from py3dbp import Painter

from services.unit_service import UnitService
from services.save_object_service import SaveObjectService
from services.packing_service import PackingService
from services.result_service import ResultService
from services.object_builder_service import ObjectBuilderService
from services.render_service import RenderService
from services.validation_service import ValidationService
from services.export_service import ExportService

class BinPackingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SupaBoxPacker")
        self.root.geometry("980x700")

        self.items = []
        self.last_box = None
        self.unit_system = tk.StringVar(value="Metric (cm)")
        self.previous_unit_system = "Metric (cm)"

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # =========================
        # Bin / Container Section
        # =========================
        bin_frame = ttk.LabelFrame(main, text="Container", padding=10)
        bin_frame.pack(fill="x", pady=(0, 10))

        self.bin_name = tk.StringVar(value="MainBin")
        self.bin_w = tk.StringVar(value="100")
        self.bin_h = tk.StringVar(value="100")
        self.bin_d = tk.StringVar(value="100")
        self.bin_weight = tk.StringVar(value="1000")
        self.bin_corner = tk.StringVar(value="0")

        self._add_labeled_entry(bin_frame, "Name", self.bin_name, 0, 0)

        self.bin_length_label = ttk.Label(bin_frame, text="Length (in)")
        self.bin_length_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(bin_frame, textvariable=self.bin_d, width=14).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.bin_width_label = ttk.Label(bin_frame, text="Width (in)")
        self.bin_width_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ttk.Entry(bin_frame, textvariable=self.bin_w, width=14).grid(row=0, column=5, padx=5, pady=5, sticky="w")

        self.bin_height_label = ttk.Label(bin_frame, text="Height (in)")
        self.bin_height_label.grid(row=0, column=6, padx=5, pady=5, sticky="e")
        ttk.Entry(bin_frame, textvariable=self.bin_h, width=14).grid(row=0, column=7, padx=5, pady=5, sticky="w")

        self.bin_weight_label = ttk.Label(bin_frame, text="Max Weight (lb)")
        self.bin_weight_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(bin_frame, textvariable=self.bin_weight, width=14).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self._add_labeled_entry(bin_frame, "Corner", self.bin_corner, 1, 2)
        
        ttk.Label(bin_frame, text="Units").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.unit_combo = ttk.Combobox(
            bin_frame,
            textvariable=self.unit_system,
            values=["Imperial (in)", "Metric (cm)"],
            state="readonly",
            width=14
        )
        
        self.unit_combo.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        self.unit_combo.bind("<<ComboboxSelected>>", self.on_unit_changed)
        ttk.Label(
            bin_frame,
            text="Display units only. Saved data remains metric/unitless internally."
        ).grid(row=2, column=0, columnspan=8, padx=5, pady=(5, 0), sticky="w")
        
        # =========================
        # Item Entry Section
        # =========================
        item_frame = ttk.LabelFrame(main, text="Add Item", padding=10)
        item_frame.pack(fill="x", pady=(0, 10))

        self.item_name = tk.StringVar()
        self.item_w = tk.StringVar()
        self.item_h = tk.StringVar()
        self.item_d = tk.StringVar()
        self.item_weight = tk.StringVar(value="1")
        self.item_fill_to_max = tk.BooleanVar(value=False)
        self.item_qty = tk.StringVar(value="1")
        self.item_color = tk.StringVar(value="#4F81BD")
        self.item_updown = tk.BooleanVar(value=True)

        self._add_labeled_entry(item_frame, "Name", self.item_name, 0, 0)

        self.item_length_label = ttk.Label(item_frame, text="Length (in)")
        self.item_length_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(item_frame, textvariable=self.item_d, width=14).grid(
            row=0, column=3, padx=5, pady=5, sticky="w"
        )

        self.item_width_label = ttk.Label(item_frame, text="Width (in)")
        self.item_width_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ttk.Entry(item_frame, textvariable=self.item_w, width=14).grid(
            row=0, column=5, padx=5, pady=5, sticky="w"
        )

        self.item_height_label = ttk.Label(item_frame, text="Height (in)")
        self.item_height_label.grid(row=0, column=6, padx=5, pady=5, sticky="e")
        ttk.Entry(item_frame, textvariable=self.item_h, width=14).grid(
            row=0, column=7, padx=5, pady=5, sticky="w"
        )

        self.item_weight_label = ttk.Label(item_frame, text="Weight (lb)")
        self.item_weight_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(item_frame, textvariable=self.item_weight, width=14).grid(
            row=1, column=1, padx=5, pady=5, sticky="w"
        )

        qty_frame = ttk.Frame(item_frame)
        qty_frame.grid(row=1, column=2, columnspan=3, padx=5, pady=5, sticky="w")

        ttk.Checkbutton(
            qty_frame,
            text="Fill to Max",
            variable=self.item_fill_to_max,
            command=self.on_fill_to_max_toggle,
        ).pack(side="left", padx=(0, 8))

        ttk.Label(qty_frame, text="Qty").pack(side="left", padx=(0, 4))

        self.item_qty_entry = ttk.Entry(qty_frame, textvariable=self.item_qty, width=8)
        self.item_qty_entry.pack(side="left")

        ttk.Label(item_frame, text="Color").grid(row=1, column=4, padx=(2, 4), pady=5, sticky="e")
        ttk.Entry(item_frame, textvariable=self.item_color, width=14).grid(
            row=1, column=5, padx=5, pady=5, sticky="w"
        )

        ttk.Checkbutton(
            item_frame,
            text="Can rotate upside down",
            variable=self.item_updown
        ).grid(row=1, column=7, padx=5, pady=5, sticky="w")

        ttk.Button(item_frame, text="Add Item", command=self.add_item).grid(
            row=2, column=0, padx=5, pady=10, sticky="w"
        )
        ttk.Button(item_frame, text="Save Item", command=self.save_item_json).grid(
            row=2, column=1, padx=5, pady=10, sticky="w"
        )
        ttk.Button(item_frame, text="Load Item", command=self.load_item_json).grid(
            row=2, column=2, padx=5, pady=10, sticky="w"
        )
        ttk.Button(item_frame, text="Clear Item Fields", command=self.clear_item_fields).grid(
            row=2, column=3, padx=5, pady=10, sticky="w"
        )

        # =========================
        # Item List Section
        # =========================
        list_frame = ttk.LabelFrame(main, text="Items To Pack", padding=10)
        list_frame.pack(fill="both", expand=False, pady=(0, 10))

        columns = ("name", "size", "weight", "qty", "color", "updown")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        for col, width in [
            ("name", 180),
            ("size", 180),
            ("weight", 80),
            ("qty", 60),
            ("color", 100),
            ("updown", 100),
        ]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="x", expand=True)

        btn_row = ttk.Frame(list_frame)
        btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(btn_row, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Clear All Items", command=self.clear_all_items).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Load Sample Items", command=self.load_sample_items).pack(side="left", padx=5)

        # =========================
        # Action Buttons
        # =========================
        action_frame = ttk.Frame(main)
        action_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(action_frame, text="Load Box Diagram", command=self.load_json).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Pack Box", command=self.run_packing).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Show 3D Diagram", command=self.show_plot).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Save Box Diagram", command=self.export_json).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Export CSV Report", command=self.export_csv).pack(side="left", padx=5)

        # =========================
        # Results Section
        # =========================
        results_frame = ttk.LabelFrame(main, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True)

        self.results = scrolledtext.ScrolledText(results_frame, wrap="word", height=14)
        self.results.pack(fill="both", expand=True)
        
        self.update_unit_labels()

    # =========================
    # Unit display + Conversion
    # Internal storage is metric/unitless:
    # - dimensions in cm
    # - weights in kg
    # =========================

    def display_to_metric_dim(self, value):
        return UnitService.display_to_metric_dim(value, self.unit_system.get())

    def metric_to_display_dim(self, value):
        return UnitService.metric_to_display_dim(value, self.unit_system.get())

    def display_to_metric_weight(self, value):
        return UnitService.display_to_metric_weight(value, self.unit_system.get())

    def metric_to_display_weight(self, value):
        return UnitService.metric_to_display_weight(value, self.unit_system.get())

    def fmt_display(self, value):
        return UnitService.fmt_display(value)

    def convert_display_dim_value(self, value, from_unit, to_unit):
        return UnitService.convert_display_dim_value(value, from_unit, to_unit)

    def convert_display_weight_value(self, value, from_unit, to_unit):
        return UnitService.convert_display_weight_value(value, from_unit, to_unit)

    def convert_visible_entry_fields(self, from_unit, to_unit):
        # Container fields
        self.bin_w.set(self.convert_display_dim_value(self.bin_w.get(), from_unit, to_unit))
        self.bin_h.set(self.convert_display_dim_value(self.bin_h.get(), from_unit, to_unit))
        self.bin_d.set(self.convert_display_dim_value(self.bin_d.get(), from_unit, to_unit))
        self.bin_weight.set(self.convert_display_weight_value(self.bin_weight.get(), from_unit, to_unit))
        self.bin_corner.set(self.convert_display_dim_value(self.bin_corner.get(), from_unit, to_unit))

        # Temporary item entry fields
        self.item_w.set(self.convert_display_dim_value(self.item_w.get(), from_unit, to_unit))
        self.item_h.set(self.convert_display_dim_value(self.item_h.get(), from_unit, to_unit))
        self.item_d.set(self.convert_display_dim_value(self.item_d.get(), from_unit, to_unit))
        self.item_weight.set(self.convert_display_weight_value(self.item_weight.get(), from_unit, to_unit))

    def refresh_item_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in self.items:
            row_values = RenderService.build_item_tree_row(
                item,
                dim_formatter=self.metric_to_display_dim,
                weight_formatter=self.metric_to_display_weight,
                number_formatter=self.fmt_display,
            )

            self.tree.insert("", "end", values=row_values)

    # =========================
    # Fill to max
    # =========================

    def on_fill_to_max_toggle(self):
        if self.item_fill_to_max.get():
            self.item_qty.set("")
            self.item_qty_entry.state(["disabled"])
        else:
            self.item_qty_entry.state(["!disabled"])
            self.item_qty.set("1")

    # =========================
    # label updates
    # =========================

    def on_unit_changed(self, event=None):
        selected_unit = self.unit_system.get()
        previous_unit = self.previous_unit_system

        if selected_unit != previous_unit:
            self.convert_visible_entry_fields(previous_unit, selected_unit)

        self.update_unit_labels()
        self.previous_unit_system = selected_unit

    def update_unit_labels(self, event=None):
        selected_unit = self.unit_system.get()
        dim_unit, weight_unit = UnitService.get_label_units(selected_unit)

        self.bin_length_label.config(text=f"Length ({dim_unit})")
        self.bin_width_label.config(text=f"Width ({dim_unit})")
        self.bin_height_label.config(text=f"Height ({dim_unit})")
        self.bin_weight_label.config(text=f"Max Weight ({weight_unit})")

        self.item_length_label.config(text=f"Length ({dim_unit})")
        self.item_width_label.config(text=f"Width ({dim_unit})")
        self.item_height_label.config(text=f"Height ({dim_unit})")
        self.item_weight_label.config(text=f"Weight ({weight_unit})")

        self.refresh_item_tree()

        if self.last_box:
            self.render_results(self.last_box)

    def _add_labeled_entry(self, parent, label, var, row, col):
        ttk.Label(parent, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
        ttk.Entry(parent, textvariable=var, width=14).grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")

    # =========================
    # Data Validation
    # =========================
 
    def _get_validated_item_data(self):
        name = ValidationService.require_text(self.item_name.get(), "Item name")

        width = ValidationService.require_float(
            self.item_w.get(), "Item width", min_value=0, allow_zero=False
        )
        height = ValidationService.require_float(
            self.item_h.get(), "Item height", min_value=0, allow_zero=False
        )
        length = ValidationService.require_float(
            self.item_d.get(), "Item length", min_value=0, allow_zero=False
        )
        weight = ValidationService.require_float(
            self.item_weight.get(), "Item weight", min_value=0, allow_zero=False
        )

        if self.item_fill_to_max.get():
            qty = 1
        else:
            qty = ValidationService.require_int(
                self.item_qty.get(), "Item quantity", min_value=1
            )

        return {
            "name": name,
            "width": self.display_to_metric_dim(width),
            "height": self.display_to_metric_dim(height),
            "depth": self.display_to_metric_dim(length),
            "weight": self.display_to_metric_weight(weight),
            "qty": qty,
            "color": self.item_color.get(),
            "updown": self.item_updown.get(),
            "fill_to_max": self.item_fill_to_max.get(),
        }

    def _get_validated_container_values(self):
        name = ValidationService.require_text(self.bin_name.get(), "Container name")

        width = ValidationService.require_float(
            self.bin_w.get(), "Container width", min_value=0, allow_zero=False
        )
        height = ValidationService.require_float(
            self.bin_h.get(), "Container height", min_value=0, allow_zero=False
        )
        length = ValidationService.require_float(
            self.bin_d.get(), "Container length", min_value=0, allow_zero=False
        )
        max_weight = ValidationService.require_float(
            self.bin_weight.get(), "Container max weight", min_value=0, allow_zero=False
        )
        corner = ValidationService.require_float(
            self.bin_corner.get(), "Container corner", min_value=0, allow_zero=True
        )

        return {
            "name": name,
            "width": self.display_to_metric_dim(width),
            "height": self.display_to_metric_dim(height),
            "depth": self.display_to_metric_dim(length),
            "max_weight": self.display_to_metric_weight(max_weight),
            "corner": self.display_to_metric_dim(corner),
        }


    def add_item(self):
        try:
            item_data = self._get_validated_item_data()

            item = ObjectBuilderService.build_item(
                name=item_data["name"],
                width=item_data["width"],
                height=item_data["height"],
                depth=item_data["depth"],
                weight=item_data["weight"],
                qty=item_data["qty"],
                color=item_data["color"],
                updown=item_data["updown"],
                fill_to_max=item_data["fill_to_max"],
            )

            ObjectBuilderService.validate_item(item)

            self.items.append(item)
            self.refresh_item_tree()
            self.clear_item_fields()
            self.last_box = None

        except Exception as exc:
            messagebox.showerror("Invalid Item", str(exc))

    def clear_item_fields(self):
        self.item_name.set("")
        self.item_w.set("")
        self.item_h.set("")
        self.item_d.set("")
        self.item_weight.set("1")
        self.item_qty.set("1")
        self.item_color.set("#4F81BD")
        self.item_updown.set(True)
        self.item_fill_to_max.set(False)
        self.item_qty_entry.state(["!disabled"])

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        indexes = [self.tree.index(item_id) for item_id in selected]

        for item_id in selected:
            self.tree.delete(item_id)

        for idx in sorted(indexes, reverse=True):
            del self.items[idx]

        self.last_box = None

    def clear_all_items(self):
        self.items.clear()
        self.last_box = None
        for row in self.tree.get_children():
            self.tree.delete(row)

    def load_sample_items(self):
        self.clear_all_items()
        self.items.extend(ObjectBuilderService.build_sample_items())
        self.refresh_item_tree()

        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "Loaded sample items.")

    def _get_container_config(self):
        values = self._get_validated_container_values()

        return PackingService.get_container_config(
            name=values["name"],
            width=values["width"],
            height=values["height"],
            depth=values["depth"],
            max_weight=values["max_weight"],
            corner=values["corner"],
        )

    def run_packing(self):
        try:
            PackingService.validate_items(self.items)

            container = self._get_container_config()
            PackingService.apply_fill_to_max(container, self.items)

            self.last_box = PackingService.pack(container, self.items)
            self.refresh_item_tree()
            self.render_results(self.last_box)

        except Exception as exc:
            messagebox.showerror("Packing Error", str(exc))

    def render_results(self, box):
        results_text = ResultService.build_results_text(
            box,
            dim_formatter=self.metric_to_display_dim,
            weight_formatter=self.metric_to_display_weight,
            number_formatter=self.fmt_display,
        )

        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, results_text)

    def show_plot(self):
        if not self.last_box:
            messagebox.showinfo("No Results", "Pack a box first.")
            return

        painter = Painter(self.last_box)
        fig = painter.plotBoxAndItems(
            title=self.last_box.bin_id,
            alpha=0.35,
            write_num=True,
            fontsize=9,
        )
        fig.show()

        # Exporting the plot
    def export_csv(self):
        if not self.last_box:
            messagebox.showinfo("No Results", "Pack a box first.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Packing Results",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
           initialfile="packing_results.csv",
        )

        if not file_path:
            return

        try:
            row_count = ExportService.export_results_csv(
                self.last_box,
                file_path,
                dim_formatter=self.metric_to_display_dim,
                weight_formatter=self.metric_to_display_weight,
                number_formatter=self.fmt_display,
            )

            self.results.delete("1.0", tk.END)
            self.results.insert(
                tk.END,
                f"Exported packing results to CSV:\n{file_path}\n"
                f"Rows written: {row_count}"
            )

        except Exception as exc:
            messagebox.showerror("CSV Export Error", f"Failed to export CSV:\n{exc}")

    def export_json(self):
        try:
            data = SaveObjectService.build_box_data(
                bin_name=self.bin_name.get().strip(),
                bin_w=self.display_to_metric_dim(self.bin_w.get()),
                bin_h=self.display_to_metric_dim(self.bin_h.get()),
                bin_d=self.display_to_metric_dim(self.bin_d.get()),
                bin_weight=self.display_to_metric_weight(self.bin_weight.get()),
                bin_corner=self.display_to_metric_dim(self.bin_corner.get()),
                items=self.items,
            )

            file_path = filedialog.asksaveasfilename(
                title="Save Box Diagram",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialfile="box_diagram.json",
            )

            if not file_path:
                return

            SaveObjectService.save_json_file(file_path, data)

            self.results.delete("1.0", tk.END)
            self.results.insert(tk.END, f"Saved box diagram to:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Export Error", f"Failed to save file:\n{exc}")
    
    def load_json(self):
        file_path = filedialog.askopenfilename(
            title="Load Box Diagram",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            data = SaveObjectService.load_json_file(file_path)
            box_parts = SaveObjectService.extract_box_parts(data)

            whd = box_parts["bin_whd"]

            self.bin_name.set(box_parts["bin_name"])
            self.bin_w.set(self.fmt_display(self.metric_to_display_dim(whd[0])))
            self.bin_h.set(self.fmt_display(self.metric_to_display_dim(whd[1])))
            self.bin_d.set(self.fmt_display(self.metric_to_display_dim(whd[2])))
            self.bin_weight.set(
                self.fmt_display(self.metric_to_display_weight(box_parts["bin_weight"]))
            )
            self.bin_corner.set(
                self.fmt_display(self.metric_to_display_dim(box_parts["bin_corner"]))
            )

            self.clear_all_items()

            for item_data in box_parts["items"]:
                self.items.append(SaveObjectService.normalize_loaded_item(item_data))

            self.refresh_item_tree()
            self.run_packing()
            self.results.insert(tk.END, f"\n\nLoaded from:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Load Error", f"Failed to load file:\n{exc}")

    def save_item_json(self):
        try:
            item_data = SaveObjectService.build_item_data(
                name=self.item_name.get().strip(),
                w=self.display_to_metric_dim(self.item_w.get()),
                h=self.display_to_metric_dim(self.item_h.get()),
                d=self.display_to_metric_dim(self.item_d.get()),
                weight=self.display_to_metric_weight(self.item_weight.get()),
                qty=1 if self.item_fill_to_max.get() else int(self.item_qty.get()),
                color=self.item_color.get().strip() or "#4F81BD",
                updown=self.item_updown.get(),
                fill_to_max=self.item_fill_to_max.get(),
            )

            if not item_data["name"]:
                raise ValueError("Item name is required.")

            file_path = filedialog.asksaveasfilename(
                title="Save Item",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialfile=f"{item_data['name']}.json",
            )

            if not file_path:
                return

            SaveObjectService.save_json_file(file_path, item_data)

            self.results.delete("1.0", tk.END)
            self.results.insert(tk.END, f"Saved item to:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Save Item Error", f"Failed to save item:\n{exc}")

    def load_item_json(self):
        file_path = filedialog.askopenfilename(
            title="Load Item",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            item_data = SaveObjectService.load_json_file(file_path)
            normalized_item = SaveObjectService.normalize_loaded_item(item_data)
            whd = normalized_item["WHD"]

            self.item_name.set(normalized_item["name"])
            self.item_w.set(self.fmt_display(self.metric_to_display_dim(whd[0])))
            self.item_h.set(self.fmt_display(self.metric_to_display_dim(whd[1])))
            self.item_d.set(self.fmt_display(self.metric_to_display_dim(whd[2])))
            self.item_weight.set(
                self.fmt_display(self.metric_to_display_weight(normalized_item["weight"]))
            )
            self.item_color.set(normalized_item["color"])
            self.item_updown.set(normalized_item["updown"])
            self.item_fill_to_max.set(normalized_item["fill_to_max"])

            if self.item_fill_to_max.get():
                self.item_qty.set("")
            else:
                self.item_qty.set(str(normalized_item["qty"]))

            self.on_fill_to_max_toggle()

            self.results.delete("1.0", tk.END)
            self.results.insert(tk.END, f"Loaded item from:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Load Item Error", f"Failed to load item:\n{exc}")