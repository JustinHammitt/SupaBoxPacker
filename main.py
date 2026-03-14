import tkinter as tk
from gui import BinPackingGUI


def main():
    root = tk.Tk()
    app = BinPackingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()