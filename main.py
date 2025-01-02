import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# 定义常量
EXCEL_FILE = 'data.xlsx'
SHEET_NAMES = ['TransactionRecord', 'Inventory']


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("SmartCheckout")

        # 初始化时读取或创建Excel文件
        self.load_or_create_excel_data()

        # 创建Notebook（选项卡容器）
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        # 创建各个页面并添加到Notebook中
        self.transaction_page = TransactionRecordPage(parent=notebook, controller=self)
        self.inventory_page = InventoryPage(parent=notebook, controller=self)
        self.checkout_page = CheckoutPage(parent=notebook, controller=self)

        notebook.add(self.transaction_page, text="交易记录")
        notebook.add(self.inventory_page, text="商品库存")
        notebook.add(self.checkout_page, text="结账")

    def load_or_create_excel_data(self):
        if not os.path.exists(EXCEL_FILE):
            # 如果文件不存在，则创建一个新的Excel文件，并初始化必要的数据结构
            empty_data = {
                'TransactionRecord': pd.DataFrame(columns=['交易时间', '交易金额', '交易内容']),
                'Inventory': pd.DataFrame(columns=['商品名称', '库存数量', '单价'])  # 确保有正确的列名
            }
            with pd.ExcelWriter(EXCEL_FILE) as writer:
                for sheet_name, df in empty_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            messagebox.showinfo("Info", "Data file created.")

        try:
            self.data = pd.read_excel(EXCEL_FILE, sheet_name=None)  # 读取所有工作表
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read data file: {e}")
            self.data = {
                'TransactionRecord': pd.DataFrame(columns=['交易时间', '交易金额', '交易内容']),
                'Inventory': pd.DataFrame(columns=['商品名称', '库存数量', '单价'])
            }

    def update_excel_data(self):
        with pd.ExcelWriter(EXCEL_FILE) as writer:
            for sheet_name, df in self.data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)


class TransactionRecordPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        # 设置页面标题
        label = tk.Label(self, text="Transaction Record Page")
        label.pack(side="top", fill="x", pady=10)

        # 创建Treeview以显示交易记录
        columns = ('time', 'amount', 'content')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('time', text='交易时间')
        self.tree.heading('amount', text='交易金额')
        self.tree.heading('content', text='交易内容')
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
        '''从控制器加载交易记录数据并更新Treeview'''
        try:
            df = self.controller.data.get('TransactionRecord', pd.DataFrame())
            if not df.empty:
                # 清除当前数据
                for i in self.tree.get_children():
                    self.tree.delete(i)

                # 插入新数据
                for index, row in df.iterrows():
                    self.tree.insert('', 'end', values=tuple(row))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transaction records: {e}")


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


class CheckoutPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        # 设置页面标题
        label = tk.Label(self, text="Checkout Page")
        label.pack(side="top", fill="x", pady=10)

        # 创建Treeview以显示和编辑商品信息
        columns = ('name', 'quantity', 'price', 'total')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('name', text='商品名称')
        self.tree.heading('quantity', text='数量')
        self.tree.heading('price', text='单价')
        self.tree.heading('total', text='总价')

        # 启用单元格编辑
        for col in columns:
            self.tree.column(col, width=100, anchor='center')
        self.tree.bind('<Double-1>', self.on_cell_double_click)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # 新增按钮
        add_item_button = tk.Button(self, text="新增商品", command=self.open_add_item_window)
        add_item_button.pack(pady=10)

        # 结账按钮
        checkout_button = tk.Button(self, text="结账", command=self.checkout)
        checkout_button.pack(pady=10)

    def open_add_item_window(self):
        '''打开新增商品窗口'''
        AddItemPage(self, self.controller)

    def add_item_to_tree(self, name, quantity, price, total):
        '''向Treeview中添加商品信息'''
        self.tree.insert('', 'end', values=(name, quantity, f'{price:.2f}', f'{total:.2f}'))


    def on_cell_double_click(self, event):
        '''允许双击编辑单元格'''
        column = self.tree.identify_column(event.x)  # 列
        item_id = self.tree.identify_row(event.y)  # 行

        if not item_id or column == '#4':  # 不允许直接编辑总价列
            return

        x, y, width, height = self.tree.bbox(item_id, column)
        value = self.tree.item(item_id, 'values')[int(column[1]) - 1]

        entry_edit = ttk.Entry(self)  # 使用CheckoutPage作为父容器
        entry_edit.place(x=x+self.winfo_x(), y=y+self.winfo_y()+self.tree.winfo_y(), width=width, height=height)
        entry_edit.insert(0, value)
        entry_edit.select_range(0, tk.END)

        def save_edit(event):
            new_value = entry_edit.get()
            try:
                # 如果是数量或单价，尝试转换为数字
                float(new_value) if column != '#1' else None
                self.tree.set(item_id, column, new_value)
                self.update_total(item_id)  # 更新该行的总价
                entry_edit.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数值")
                entry_edit.focus_set()  # 保留焦点以便用户修正输入

        entry_edit.bind("<Return>", save_edit)
        entry_edit.bind("<Escape>", lambda e: entry_edit.destroy())
        entry_edit.focus_set()

    def update_total(self, item_id):
        '''根据数量和单价更新总价'''
        try:
            quantity = float(self.tree.item(item_id, 'values')[1])
            price = float(self.tree.item(item_id, 'values')[2])
            total = quantity * price
            self.tree.set(item_id, '#4', f'{total:.2f}')
        except (ValueError, TypeError):
            pass  # 如果无法转换为数字，保持原样

    def checkout(self):
        '''处理结账逻辑：更新库存并添加交易记录'''
        try:
            items = []
            for item in self.tree.get_children():
                name, quantity, price, total = self.tree.item(item, 'values')
                items.append({
                    '商品名称': name,
                    '数量': int(quantity),
                    '单价': float(price),
                    '总价': float(total)
                })

            if not items:
                messagebox.showwarning("警告", "没有商品可以结账")
                return

            # 更新库存
            inventory_df = self.controller.data.get('Inventory', pd.DataFrame())
            for item in items:
                mask = inventory_df['商品名称'] == item['商品名称']
                if mask.any():
                    inventory_df.loc[mask, '库存数量'] -= item['数量']
                    if any(inventory_df.loc[mask, '库存数量'] < 0):
                        messagebox.showerror("错误", f"{item['商品名称']} 库存不足")
                        return
                else:
                    messagebox.showerror("错误", f"找不到商品 {item['商品名称']}")
                    return

            # 添加交易记录
            transaction_df = self.controller.data.get('TransactionRecord', pd.DataFrame())
            now = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            new_transactions = [
                {
                    '交易时间': now,
                    '交易金额': item['总价'],
                    '交易内容': f"{item['商品名称']} x {item['数量']}"
                }
                for item in items
            ]

            # 使用 pd.concat 添加新交易记录
            transaction_df = pd.concat([transaction_df, pd.DataFrame(new_transactions)], ignore_index=True)

            # 更新数据字典
            self.controller.data['Inventory'] = inventory_df
            self.controller.data['TransactionRecord'] = transaction_df

            # 更新Excel文件
            self.controller.update_excel_data()

            messagebox.showinfo("成功", "结账成功")

            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)

        except Exception as e:
            messagebox.showerror("错误", f"结账失败: {e}")

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

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()