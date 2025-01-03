import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

from AddItemPage import AddItemPage


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

        for col in columns:
            self.tree.column(col, width=100, anchor='center')

        self.tree.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # 新增按钮，现在用于选择图片并识别商品
        add_item_button = tk.Button(self, text="选择图片识别商品", command=self.select_image_and_recognize_items)
        add_item_button.pack(pady=10)

        # 结账按钮
        checkout_button = tk.Button(self, text="结账", command=self.checkout)
        checkout_button.pack(pady=10)

    def select_image_and_recognize_items(self):
        '''选择图片并尝试从中识别商品'''
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if not file_path:
            return  # 用户取消选择

        try:
            image_classification = self.controller.get_image_classification_model()
            result = image_classification(file_path)
            print(result)  # 打印识别结果，以便调试

            # 解析识别结果（这里简化了实际解析过程）
            item_names = []

            # 匹配库存中的商品
            inventory_df = self.controller.data.get('Inventory', pd.DataFrame())
            for name in item_names:
                mask = inventory_df['商品名称'].str.contains(name, case=False, na=False)
                if mask.any():
                    matched_item = inventory_df[mask].iloc[0]
                    self.add_item_to_tree(
                        matched_item['商品名称'],
                        1,  # 默认数量为1
                        matched_item['单价'],  # 假设库存中有单价字段
                        matched_item['单价']  # 总价等于单价
                    )

            if not any(mask):
                messagebox.showwarning("警告", "没有找到匹配的商品")

        except Exception as e:
            messagebox.showerror("错误", f"图片识别失败: {e}")

    def add_item_to_tree(self, name, quantity, price, total):
        '''向Treeview中添加商品信息'''
        self.tree.insert('', 'end', values=(name, quantity, f'{price:.2f}', f'{total:.2f}'))

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