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


def make_tree(parent: tk.Misc, columns: list[str], use_checkbox: bool = False) -> ttk.Treeview:
    configure_tree_style()
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)
    scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)

    all_cols = (["Chọn"] if use_checkbox else []) + columns
    tree = ttk.Treeview(frame, columns=all_cols, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)
    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    for col in all_cols:
        tree.heading(col, text=col, command=lambda c=col: sort_tree(tree, c, False))
        if col == "Chọn":
            tree.column(col, width=50, anchor=tk.CENTER)
            tree.heading(col, text="☐")  # Nút chọn tất cả (giả lập)
        else:
            width = 180 if col in {"HoTen", "TenHocPhan", "XepLoai"} else 110
            tree.column(col, width=width, anchor=tk.W if col in {"HoTen", "TenHocPhan"} else tk.CENTER)

    if use_checkbox:

        def toggle_checkbox(event):
            region = tree.identify_region(event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                if column == "#1":  # Cột "Chọn" là cột đầu tiên
                    item = tree.identify_row(event.y)
                    current = tree.set(item, "Chọn")
                    tree.set(item, "Chọn", "☑" if current == "☐" else "☐")
            elif region == "heading":
                column = tree.identify_column(event.x)
                if column == "#1":
                    # Toggle all
                    items = tree.get_children()
                    if not items:
                        return
                    current_head = tree.heading("Chọn")["text"]
                    new_val = "☑" if current_head == "☐" else "☐"
                    tree.heading("Chọn", text=new_val)
                    for item in items:
                        tree.set(item, "Chọn", new_val)

        tree.bind("<ButtonRelease-1>", toggle_checkbox)

    return tree


def sort_tree(tree: ttk.Treeview, col: str, reverse: bool) -> None:
    # Bỏ qua sắp xếp cho cột Chọn
    if col == "Chọn":
        return
    values = [(tree.set(item, col), item) for item in tree.get_children("")]
    try:
        # Thử sắp xếp theo số
        values.sort(key=lambda item: float(item[0]), reverse=reverse)
    except ValueError:
        # Sắp xếp theo chuỗi
        values.sort(key=lambda item: str(item[0]).lower(), reverse=reverse)
    for index, (_, item) in enumerate(values):
        tree.move(item, "", index)
    tree.heading(col, command=lambda: sort_tree(tree, col, not reverse))


def replace_tree_rows(tree: ttk.Treeview, columns: list[str], rows: list[dict]) -> None:
    for item in tree.get_children():
        tree.delete(item)
    use_checkbox = "Chọn" in tree["columns"]
    for row in rows:
        vals = []
        if use_checkbox:
            vals.append("☐")
        vals.extend([row.get(col, "") for col in columns])
        tree.insert("", tk.END, values=vals)
