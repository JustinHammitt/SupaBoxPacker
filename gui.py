import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

from py3dbp import Packer, Bin, Item, Painter


class BinPackingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Bin Packing - Simple GUI")
        self.root.geometry("980x700")

        self.items = []
        self.last_box = None

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
        self._add_labeled_entry(bin_frame, "Width", self.bin_w, 0, 2)
        self._add_labeled_entry(bin_frame, "Height", self.bin_h, 0, 4)
        self._add_labeled_entry(bin_frame, "Depth", self.bin_d, 0, 6)
        self._add_labeled_entry(bin_frame, "Max Weight", self.bin_weight, 1, 0)
        self._add_labeled_entry(bin_frame, "Corner", self.bin_corner, 1, 2)

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
        self.item_qty = tk.StringVar(value="1")
        self.item_color = tk.StringVar(value="#4F81BD")
        self.item_updown = tk.BooleanVar(value=True)

        self._add_labeled_entry(item_frame, "Name", self.item_name, 0, 0)
        self._add_labeled_entry(item_frame, "Width", self.item_w, 0, 2)
        self._add_labeled_entry(item_frame, "Height", self.item_h, 0, 4)
        self._add_labeled_entry(item_frame, "Depth", self.item_d, 0, 6)
        self._add_labeled_entry(item_frame, "Weight", self.item_weight, 1, 0)
        self._add_labeled_entry(item_frame, "Qty", self.item_qty, 1, 2)
        self._add_labeled_entry(item_frame, "Color", self.item_color, 1, 4)

        ttk.Checkbutton(
            item_frame,
            text="Can rotate upside down",
            variable=self.item_updown
        ).grid(row=1, column=6, padx=5, pady=5, sticky="w")

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

    def _add_labeled_entry(self, parent, label, var, row, col):
        ttk.Label(parent, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
        ttk.Entry(parent, textvariable=var, width=14).grid(row=row, column=col + 1, padx=5, pady=5, sticky="w")

    def add_item(self):
        try:
            item = {
                "name": self.item_name.get().strip(),
                "WHD": (
                    float(self.item_w.get()),
                    float(self.item_h.get()),
                    float(self.item_d.get()),
                ),
                "weight": float(self.item_weight.get()),
                "qty": int(self.item_qty.get()),
                "color": self.item_color.get().strip() or "#4F81BD",
                "updown": self.item_updown.get(),
            }

            if not item["name"]:
                raise ValueError("Item name is required.")

            self.items.append(item)
            self.tree.insert(
                "",
                "end",
                values=(
                    item["name"],
                    f"{item['WHD'][0]} x {item['WHD'][1]} x {item['WHD'][2]}",
                    item["weight"],
                    item["qty"],
                    item["color"],
                    item["updown"],
                ),
            )
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

        for sample in samples:
            self.items.append(sample)
            self.tree.insert(
                "",
                "end",
                values=(
                    sample["name"],
                    f"{sample['WHD'][0]} x {sample['WHD'][1]} x {sample['WHD'][2]}",
                    sample["weight"],
                    sample["qty"],
                    sample["color"],
                    sample["updown"],
                ),
            )

        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "Loaded sample items.")

    def run_packing(self):
        try:
            if not self.items:
                raise ValueError("Add at least one item before packing.")

            packer = Packer()
            box = Bin(
                partno=self.bin_name.get().strip() or "MainBin",
                WHD=(float(self.bin_w.get()), float(self.bin_h.get()), float(self.bin_d.get())),
                max_weight=float(self.bin_weight.get()),
                corner=float(self.bin_corner.get()),
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
            self.render_results(self.last_box)

        except Exception as exc:
            messagebox.showerror("Packing Error", str(exc))

    def render_results(self, box):
        fitted = len(box.items)
        unfitted = len(box.unfitted_items)
        used_volume = sum(float(i.width) * float(i.height) * float(i.depth) for i in box.items)
        total_volume = float(box.width) * float(box.height) * float(box.depth)
        utilization = (used_volume / total_volume * 100) if total_volume else 0

        lines = [
            f"Container: {box.partno}",
            f"Size: {box.width} x {box.height} x {box.depth}",
            f"Max Weight: {box.max_weight}",
            "",
            f"Fitted Items: {fitted}",
            f"Unfitted Items: {unfitted}",
            f"Space Utilization: {utilization:.2f}%",
            f"Gravity Distribution: {box.gravity}",
            "",
            "=== FITTED ===",
        ]

        for item in box.items:
            lines.append(
                f"{item.partno} | pos={item.position} | size={item.width}x{item.height}x{item.depth} | rot={item.rotation_type}"
            )

        lines.append("")
        lines.append("=== UNFITTED ===")

        for item in box.unfitted_items:
            lines.append(f"{item.partno} | size={item.width}x{item.height}x{item.depth}")

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

    def export_json(self):
        try:
            data = {
                "bin": {
                    "name": self.bin_name.get().strip(),
                    "WHD": [
                        float(self.bin_w.get()),
                        float(self.bin_h.get()),
                        float(self.bin_d.get()),
                    ],
                    "max_weight": float(self.bin_weight.get()),
                    "corner": float(self.bin_corner.get()),
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
            self.bin_w.set(str(whd[0]))
            self.bin_h.set(str(whd[1]))
            self.bin_d.set(str(whd[2]))
            self.bin_weight.set(str(bin_data.get("max_weight", 1000)))
            self.bin_corner.set(str(bin_data.get("corner", 0)))

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
                }

                self.items.append(normalized_item)
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        normalized_item["name"],
                        f"{normalized_item['WHD'][0]} x {normalized_item['WHD'][1]} x {normalized_item['WHD'][2]}",
                        normalized_item["weight"],
                        normalized_item["qty"],
                        normalized_item["color"],
                        normalized_item["updown"],
                    ),
                )

            # UX improvement:
            # Automatically pack the box immediately after loading.
            self.run_packing()

            # Optional status note after packing completes.
            self.results.insert(tk.END, f"\n\nLoaded from:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Load Error", f"Failed to load file:\n{exc}")

    def save_item_json(self):
        try:
            item_data = {
                "name": self.item_name.get().strip(),
                "WHD": [
                    float(self.item_w.get()),
                    float(self.item_h.get()),
                    float(self.item_d.get()),
                ],
                "weight": float(self.item_weight.get()),
                "qty": int(self.item_qty.get()),
                "color": self.item_color.get().strip() or "#4F81BD",
                "updown": self.item_updown.get(),
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
            self.item_w.set(str(whd[0]))
            self.item_h.set(str(whd[1]))
            self.item_d.set(str(whd[2]))
            self.item_weight.set(str(item_data.get("weight", 1)))
            self.item_qty.set(str(item_data.get("qty", 1)))
            self.item_color.set(str(item_data.get("color", "#4F81BD")))
            self.item_updown.set(bool(item_data.get("updown", True)))

            self.results.delete("1.0", tk.END)
            self.results.insert(tk.END, f"Loaded item from:\n{file_path}")

        except Exception as exc:
            messagebox.showerror("Load Item Error", f"Failed to load item:\n{exc}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BinPackingGUI(root)
    root.mainloop()