import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

from py3dbp import Packer, Bin, Item, Painter

from fill_to_capacity import fill_single_item_to_capacity


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

    def is_metric_display(self):
        return self.unit_system.get() == "Metric (cm)"

    def display_to_metric_dim(self, value):
        value = float(value)
        if self.is_metric_display():
            return value
        return value * 2.54

    def metric_to_display_dim(self, value):
        value = float(value)
        if self.is_metric_display():
            return value
        return value / 2.54

    def display_to_metric_weight(self, value):
        value = float(value)
        if self.is_metric_display():
            return value
        return value * 0.45359237

    def metric_to_display_weight(self, value):
        value = float(value)
        if self.is_metric_display():
            return value
        return value / 0.45359237

    def fmt_display(self, value):
        value = round(float(value), 4)

        # Snap very-close whole numbers to the whole number
        if abs(value - round(value)) < 0.0002:
            value = round(value)

        return f"{value:.4f}".rstrip("0").rstrip(".")
        
    def convert_display_dim_value(self, value, from_unit, to_unit):
        try:
            value = float(value)
        except Exception:
            return value

        if from_unit == to_unit:
            return self.fmt_display(value)

        if from_unit == "Imperial (in)" and to_unit == "Metric (cm)":
            return self.fmt_display(value * 2.54)

        if from_unit == "Metric (cm)" and to_unit == "Imperial (in)":
            return self.fmt_display(value / 2.54)

        return self.fmt_display(value)

    def convert_display_weight_value(self, value, from_unit, to_unit):
        try:
            value = float(value)
        except Exception:
            return value

        if from_unit == to_unit:
            return self.fmt_display(value)

        if from_unit == "Imperial (in)" and to_unit == "Metric (cm)":
            return self.fmt_display(value * 0.45359237)

        if from_unit == "Metric (cm)" and to_unit == "Imperial (in)":
            return self.fmt_display(value / 0.45359237)

        return self.fmt_display(value)

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
            display_w = self.fmt_display(self.metric_to_display_dim(item["WHD"][0]))
            display_h = self.fmt_display(self.metric_to_display_dim(item["WHD"][1]))
            display_d = self.fmt_display(self.metric_to_display_dim(item["WHD"][2]))
            display_weight = self.fmt_display(self.metric_to_display_weight(item["weight"]))

            self.tree.insert(
                "",
                "end",
                values=(
                    item["name"],
                                f"{display_d} x {display_w} x {display_h}",                                                display_weight,
                    "AUTO" if item.get("fill_to_max", False) else item["qty"],
                    item["color"],
                    item["updown"],
                ),
            )

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

        if selected_unit == "Metric (cm)":
            dim_unit = "cm"
            weight_unit = "kg"
        else:
            dim_unit = "in"
            weight_unit = "lb"

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

    def add_item(self):
        try:
            item = {
                "name": self.item_name.get().strip(),
                "WHD": (
                    self.display_to_metric_dim(self.item_w.get()),
                    self.display_to_metric_dim(self.item_h.get()),
                    self.display_to_metric_dim(self.item_d.get()),
                ),
                "weight": self.display_to_metric_weight(self.item_weight.get()),
                "qty": 1 if self.item_fill_to_max.get() else int(self.item_qty.get()),
                "color": self.item_color.get().strip() or "#4F81BD",
                "updown": self.item_updown.get(),
                "fill_to_max": self.item_fill_to_max.get(),
            }

            if not item["name"]:
                raise ValueError("Item name is required.")

            self.items.append(item)
            self.refresh_item_tree()
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
        samples = [
            {"name": "BoxA", "WHD": (20, 20, 20), "weight": 5, "qty": 3, "color": "#FF6666", "updown": True},
            {"name": "BoxB", "WHD": (30, 20, 10), "weight": 4, "qty": 2, "color": "#66CC66", "updown": True},
            {"name": "TallItem", "WHD": (15, 40, 15), "weight": 6, "qty": 1, "color": "#6699FF", "updown": False},
        ]

        self.items.extend(samples)
        self.refresh_item_tree()

        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "Loaded sample items.")

    def run_packing(self):
        try:
            if not self.items:
                raise ValueError("Add at least one item before packing.")

            auto_items = [item for item in self.items if item.get("fill_to_max", False)]
            if len(auto_items) > 1:
                raise ValueError("Only one 'Fill to Max' item is supported right now.")

            if len(self.items) > 1 and auto_items:
                raise ValueError(
                    "'Fill to Max' currently works only when it is the only item in the list."
                )

            if auto_items:
                container = self._get_container_config()
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

            packer = Packer()
            box = Bin(
                partno=self.bin_name.get().strip() or "MainBin",
                WHD=(
                    self.display_to_metric_dim(self.bin_w.get()),
                    self.display_to_metric_dim(self.bin_h.get()),
                    self.display_to_metric_dim(self.bin_d.get()),
                ),
                max_weight=self.display_to_metric_weight(self.bin_weight.get()),
                corner=self.display_to_metric_dim(self.bin_corner.get()),
                put_type=0,
            )
            packer.addBin(box)

            for item in self.items:
                for i in range(item["qty"]):
                    packer.addItem(
                        Item(
                            partno=f"{item['name']}-{i + 1}",
                            name=item["name"],
                            typeof="cube",
                            WHD=item["WHD"],
                            weight=item["weight"],
                            level=1,
                            loadbear=100,
                            updown=item["updown"],
                            color=item["color"],
                        )
                    )

            packer.pack(
                bigger_first=True,
                distribute_items=False,
                fix_point=True,
                check_stable=False,
                support_surface_ratio=0.75,
                number_of_decimals=0,
            )

            self.last_box = packer.bins[0]
            self.refresh_item_tree()
            self.render_results(self.last_box)

        except Exception as exc:
            messagebox.showerror("Packing Error", str(exc))
    
    def render_results(self, box):
        fitted = len(box.items)
        unfitted = len(box.unfitted_items)
        used_volume = sum(float(i.width) * float(i.height) * float(i.depth) for i in box.items)
        total_volume = float(box.width) * float(box.height) * float(box.depth)
        utilization = (used_volume / total_volume * 100) if total_volume else 0

        disp_box_w = self.fmt_display(self.metric_to_display_dim(box.width))
        disp_box_h = self.fmt_display(self.metric_to_display_dim(box.height))
        disp_box_d = self.fmt_display(self.metric_to_display_dim(box.depth))
        disp_box_weight = self.fmt_display(self.metric_to_display_weight(box.max_weight))

        lines = [
            f"Container: {box.partno}",
            f"Size (L x W x H): {disp_box_d} x {disp_box_w} x {disp_box_h}",
            f"Max Weight: {disp_box_weight}",
            "",
            f"Fitted Items: {fitted}",
            f"Unfitted Items: {unfitted}",
            f"Space Utilization: {utilization:.2f}%",
            f"Gravity Distribution: {box.gravity}",
            "",
            "=== FITTED ===",
        ]

        for item in box.items:
            disp_w = self.fmt_display(self.metric_to_display_dim(item.width))
            disp_h = self.fmt_display(self.metric_to_display_dim(item.height))
            disp_d = self.fmt_display(self.metric_to_display_dim(item.depth))
            lines.append(
                f"{item.partno} | pos={item.position} | size(LxWxH)={disp_d}x{disp_w}x{disp_h} | rot={item.rotation_type}"
            )

        lines.append("")
        lines.append("=== UNFITTED ===")

        for item in box.unfitted_items:
            disp_w = self.fmt_display(self.metric_to_display_dim(item.width))
            disp_h = self.fmt_display(self.metric_to_display_dim(item.height))
            disp_d = self.fmt_display(self.metric_to_display_dim(item.depth))
            lines.append(f"{item.partno} | size(LxWxH)={disp_d}x{disp_w}x{disp_h}")

        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "\n".join(lines))

    def show_plot(self):
        if not self.last_box:
            messagebox.showinfo("No Results", "Pack a box first.")
            return

        painter = Painter(self.last_box)
        fig = painter.plotBoxAndItems(
            title=self.last_box.partno,
            alpha=0.35,
            write_num=True,
            fontsize=9,
        )
        fig.show()

    # =========================
    # Fill to Max Helpers
    # =========================

    def on_fill_to_max_toggle(self):
        if self.item_fill_to_max.get():
            self.item_qty.set("")
            self.item_qty_entry.state(["disabled"])
        else:
            self.item_qty_entry.state(["!disabled"])
            self.item_qty.set("1")

    def _get_container_config(self):
        return {
            "name": self.bin_name.get().strip() or "MainBin",
            "WHD": [
                self.display_to_metric_dim(self.bin_w.get()),
                self.display_to_metric_dim(self.bin_h.get()),
                self.display_to_metric_dim(self.bin_d.get()),
            ],
            "max_weight": self.display_to_metric_weight(self.bin_weight.get()),
            "corner": self.display_to_metric_dim(self.bin_corner.get() or 0),
        }


# --
# Jason your a G homie
# --

    def export_json(self):
        try:
            data = {
                "bin": {
                    "name": self.bin_name.get().strip(),
                    "WHD": [
                        self.display_to_metric_dim(self.bin_w.get()),
                        self.display_to_metric_dim(self.bin_h.get()),
                        self.display_to_metric_dim(self.bin_d.get()),
                    ],
                    "max_weight": self.display_to_metric_weight(self.bin_weight.get()),
                    "corner": self.display_to_metric_dim(self.bin_corner.get()),
                },
                "items": [
                    {
                        "name": item["name"],
                        "WHD": list(item["WHD"]),
                        "weight": item["weight"],
                        "qty": item["qty"],
                        "color": item["color"],
                        "updown": item["updown"],
                    }
                    for item in self.items
                ],
            }

            file_path = filedialog.asksaveasfilename(
                title="Save Box Diagram",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialfile="box_diagram.json",
            )

            if not file_path:
                return

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

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
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            bin_data = data.get("bin", {})
            items_data = data.get("items", [])
            whd = bin_data.get("WHD", [100, 100, 100])

            self.bin_name.set(str(bin_data.get("name", "MainBin")))
            self.bin_w.set(self.fmt_display(self.metric_to_display_dim(whd[0])))
            self.bin_h.set(self.fmt_display(self.metric_to_display_dim(whd[1])))
            self.bin_d.set(self.fmt_display(self.metric_to_display_dim(whd[2])))
            self.bin_weight.set(
                self.fmt_display(self.metric_to_display_weight(bin_data.get("max_weight", 1000)))
            )
            self.bin_corner.set(
                self.fmt_display(self.metric_to_display_dim(bin_data.get("corner", 0)))
            )

            self.clear_all_items()

            for item in items_data:
                item_whd = item.get("WHD", [0, 0, 0])

                normalized_item = {
                    "name": str(item.get("name", "")).strip(),
                    "WHD": (
                        float(item_whd[0]),
                        float(item_whd[1]),
                        float(item_whd[2]),
                    ),
                    "weight": float(item.get("weight", 1)),
                    "qty": int(item.get("qty", 1)),
                    "color": str(item.get("color", "#4F81BD")),
                    "updown": bool(item.get("updown", True)),
                    "fill_to_max": bool(item.get("fill_to_max", False)),
                }

                self.items.append(normalized_item)

            self.refresh_item_tree()
            self.run_packing()
            self.results.insert(tk.END, f"\n\nLoaded from:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Load Error", f"Failed to load file:\n{exc}")

    def save_item_json(self):
        try:
            item_data = {
                "name": self.item_name.get().strip(),
                "WHD": [
                    self.display_to_metric_dim(self.item_w.get()),
                    self.display_to_metric_dim(self.item_h.get()),
                    self.display_to_metric_dim(self.item_d.get()),
                ],
                "weight": self.display_to_metric_weight(self.item_weight.get()),
                "qty": 1 if self.item_fill_to_max.get() else int(self.item_qty.get()),
                "color": self.item_color.get().strip() or "#4F81BD",
                "updown": self.item_updown.get(),
                "fill_to_max": self.item_fill_to_max.get(),
            }

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

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(item_data, f, indent=2)

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
            with open(file_path, "r", encoding="utf-8") as f:
                item_data = json.load(f)

            whd = item_data.get("WHD", [0, 0, 0])

            self.item_name.set(str(item_data.get("name", "")))
            self.item_w.set(self.fmt_display(self.metric_to_display_dim(whd[0])))
            self.item_h.set(self.fmt_display(self.metric_to_display_dim(whd[1])))
            self.item_d.set(self.fmt_display(self.metric_to_display_dim(whd[2])))
            self.item_weight.set(
                self.fmt_display(self.metric_to_display_weight(item_data.get("weight", 1)))
            )
            self.item_color.set(str(item_data.get("color", "#4F81BD")))
            self.item_updown.set(bool(item_data.get("updown", True)))
            self.item_fill_to_max.set(bool(item_data.get("fill_to_max", False)))

            if self.item_fill_to_max.get():
                self.item_qty.set("")
            else:
                self.item_qty.set(str(item_data.get("qty", 1)))

            self.on_fill_to_max_toggle()

            self.results.delete("1.0", tk.END)
            self.results.insert(tk.END, f"Loaded item from:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Load Item Error", f"Failed to load item:\n{exc}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BinPackingGUI(root)
    root.mainloop()