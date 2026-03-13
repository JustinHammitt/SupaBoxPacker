# SupaBoxPacker 📦

A simple desktop GUI for experimenting with **3D bin packing algorithms**.

SupaBoxPacker lets you visually test how items fit inside a container and generate a 3D diagram of the packed result.

Built in Python using:

- Tkinter GUI
- py3dbp packing algorithm
- matplotlib 3D visualization

---

# Features

✔ Simple GUI interface  
✔ Add / remove items quickly  
✔ Save and load item presets  
✔ Save and load full box diagrams  
✔ Automatic packing algorithm  
✔ 3D visualization of packed items  
✔ Export layouts to JSON  
✔ Windows EXE build via GitHub Actions  

---

# Screenshots

### Main Interface

![Main GUI](images/gui-main.png)

### Packed 3D Diagram

![3D Diagram](images/gui-diagram.png)

*(screenshots coming soon)*

---

# Download

Download the latest executable from:

**Releases → SupaBoxPacker.exe**

No Python installation required.

---

# Example Workflow

1. Define container size
2. Add items to pack
3. Click **Pack Box**
4. View results
5. Open **3D Diagram**

You can also save layouts and item templates for reuse.

---

# Example Item Template

```json
{
  "name": "BoxA",
  "WHD": [20, 20, 20],
  "weight": 5,
  "qty": 3,
  "color": "#FF6666",
  "updown": true
}
```

---

# Project Structure

```
SupaBoxPacker/
│
├─ simple_gui.py
├─ requirements.txt
│
├─ .github/
│  └─ workflows/
│     └─ build-windows.yml
│
└─ images/
   ├─ gui-main.png
   └─ gui-diagram.png
```

---

# Build From Source

```
pip install -r requirements.txt
python simple_gui.py
```

---

# Build Windows EXE

```
pyinstaller --onefile --windowed simple_gui.py
```

---

# Credits

Packing algorithm powered by:

**py3dbp**

Visualization powered by:

**matplotlib**

---

# License

MIT License