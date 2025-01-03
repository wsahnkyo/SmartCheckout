from modelscope import snapshot_download

# 指定你想要保存模型的本地路径
local_model_dir = '/model'

# 下载模型并指定本地存储位置
model_dir = snapshot_download('iic/cv_vit-base_image-classification_Dailylife-labels',
                              cache_dir=local_model_dir)

print(f'Model downloaded to: {model_dir}')