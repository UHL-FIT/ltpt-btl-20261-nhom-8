from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def center_window(window: tk.Toplevel, parent: tk.Misc | None = None) -> None:
    window.update_idletasks()
    if parent:
        x = parent.winfo_rootx() + max((parent.winfo_width() - window.winfo_width()) // 2, 40)
        y = parent.winfo_rooty() + max((parent.winfo_height() - window.winfo_height()) // 2, 40)
    else:
        x = (window.winfo_screenwidth() - window.winfo_width()) // 2
        y = (window.winfo_screenheight() - window.winfo_height()) // 2
    window.geometry(f"+{x}+{y}")


def configure_tree_style() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


def make_tree(parent: tk.Misc, columns: list[str]) -> ttk.Treeview:
    configure_tree_style()
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)
    scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
    tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)
    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_tree(tree, c, False))
        width = 180 if col in {"HoTen", "TenHocPhan", "XepLoai"} else 110
        tree.column(col, width=width, anchor=tk.W if col in {"HoTen", "TenHocPhan"} else tk.CENTER)
    return tree


def sort_tree(tree: ttk.Treeview, col: str, reverse: bool) -> None:
    values = [(tree.set(item, col), item) for item in tree.get_children("")]
    try:
        values.sort(key=lambda item: float(item[0]), reverse=reverse)
    except ValueError:
        values.sort(key=lambda item: item[0].lower(), reverse=reverse)
    for index, (_, item) in enumerate(values):
        tree.move(item, "", index)
    tree.heading(col, command=lambda: sort_tree(tree, col, not reverse))


def replace_tree_rows(tree: ttk.Treeview, columns: list[str], rows: list[dict]) -> None:
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", tk.END, values=[row.get(col, "") for col in columns])
