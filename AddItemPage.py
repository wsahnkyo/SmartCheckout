import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class AddItemPage(tk.Toplevel):
    def __init__(self, parent, controller):
        tk.Toplevel.__init__(self, parent)
        self.title("Add Item")
        self.controller = controller

        # 商品名称输入框
        tk.Label(self, text="商品名称:").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        # 数量输入框
        tk.Label(self, text="数量:").grid(row=1, column=0, padx=10, pady=5)
        self.quantity_entry = ttk.Entry(self)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        # 完成按钮
        complete_button = tk.Button(self, text="完成", command=self.on_complete)
        complete_button.grid(row=2, column=0, columnspan=2, pady=10)

    def on_complete(self):
        name = str(self.name_entry.get().strip())
        try:
            quantity = int(self.quantity_entry.get())
            if not name or quantity <= 0:
                raise ValueError("无效的商品名称或数量")

            # 查找库存信息
            inventory_df = self.controller.data.get('Inventory', pd.DataFrame())
            item_info = inventory_df[inventory_df['商品名称'] == name]

            if item_info.empty:
                messagebox.showerror("错误", f"找不到商品 {name}")
                return

            if item_info['库存数量'].values[0] < quantity:
                messagebox.showerror("错误", f"{name} 库存不足")
                return

            # 将商品信息添加到CheckoutPage的表格中
            price = item_info['单价'].values[0]
            total = price * quantity
            self.controller.checkout_page.add_item_to_tree(name, quantity, price, total)

            # 关闭窗口
            self.destroy()

        except ValueError as e:
            messagebox.showerror("错误", str(e))
