from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 指定本地模型的路径
local_model_dir = 'C:\model\iic\cv_vit-base_image-classification_Dailylife-labels'

# 加载本地模型进行图像分类
image_classification = pipeline(
    task=Tasks.image_classification,
    model=local_model_dir  # 使用本地模型路径代替模型ID
)

img_path = r'C:\Users\sesa755454\Pictures\1.jpg'
result = image_classification(img_path)
print(result)