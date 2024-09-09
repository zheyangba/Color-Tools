import os
from PIL import Image

def batch_tiff_to_png(input_folder, output_folder):
    try:
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)

        # 遍历输入文件夹中的所有文件
        for filename in os.listdir(input_folder):
            if filename.endswith(".tif") or filename.endswith(".tiff"):
                # 构建输入文件路径
                input_path = os.path.join(input_folder, filename)

                # 构建输出文件路径
                output_filename = os.path.splitext(filename)[0] + ".png"
                output_path = os.path.join(output_folder, output_filename)

                # 打开TIFF图像并将其转换为PNG图像
                tiff_image = Image.open(input_path)
                tiff_image.save(output_path, 'PNG')

        print("批量转换完成！")
    except Exception as e:
        print(f"转换失败：{e}")

# 调用函数进行批量转换
batch_tiff_to_png('D:\\0\\test\images', 'D:\\0\\test\images')
