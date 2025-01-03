import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from CheckoutPage import CheckoutPage
from InventoryPage import InventoryPage
from TransactionRecordPage import TransactionRecordPage




class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("SmartCheckout")

        # 初始化图像分类模型
        self.init_image_classification_model()

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

    def init_image_classification_model(self):
        '''初始化图像分类模型'''
        try:
            # 指定本地模型的路径
            local_model_dir = r'C:\model\iic\cv_vit-base_image-classification_Dailylife-labels'
            # 加载本地模型进行图像分类
            self.image_classification = pipeline(
                task=Tasks.image_classification,
                model=local_model_dir  # 使用本地模型路径代替模型ID
            )
        except Exception as e:
            messagebox.showerror("错误", f"初始化图像分类模型失败: {e}")

    def get_image_classification_model(self):
        '''提供对图像分类模型的访问'''
        return self.image_classification

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


# 定义常量
EXCEL_FILE = 'data.xlsx'
SHEET_NAMES = ['TransactionRecord', 'Inventory']

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()