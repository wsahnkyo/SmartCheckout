import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class InventoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        # 设置页面标题
        label = tk.Label(self, text="Inventory Page")
        label.pack(side="top", fill="x", pady=10)

        # 创建Treeview以显示商品库存
        columns = ('name', 'quantity', 'price')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('name', text='商品名称')
        self.tree.heading('quantity', text='库存数量')
        self.tree.heading('price', text='单价')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # 加载初始数据
        self.load_data()

        # 刷新按钮
        refresh_button = tk.Button(self, text="刷新", command=self.load_data)
        refresh_button.pack(pady=10)

    def load_data(self):
        '''从控制器加载商品库存数据并更新Treeview'''
        try:
            df = self.controller.data.get('Inventory', pd.DataFrame())
            if not df.empty:
                # 清除当前数据
                for i in self.tree.get_children():
                    self.tree.delete(i)

                # 插入新数据
                for index, row in df.iterrows():
                    self.tree.insert('', 'end', values=tuple(row))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory data: {e}")


