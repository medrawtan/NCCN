import os
from pdf2image import convert_from_path

def convert_pdf_to_images(pdf_path, output_folder):
    """
    将PDF文件的每一页转换为图片。

    参数:
    pdf_path (str): 输入的PDF文件路径。
    output_folder (str): 保存输出图片的文件夹。
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 将PDF转换为一个PIL Image对象的列表
    # 对于Windows用户，如果poppler没有在环境变量中，需要指定poppler_path
    # images = convert_from_path(pdf_path, poppler_path=r"C:\poppler-24.02.0\bin")
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"转换失败，请确保Poppler已经正确安装并配置在系统路径中。错误信息: {e}")
        return

    # 遍历所有图片并保存
    for i, image in enumerate(images):
        # 构建输出图片的文件名
        image_name = f"page_{i + 1}.png"
        image_path = os.path.join(output_folder, image_name)
        
        # 保存图片
        image.save(image_path, "PNG")
        print(f"已保存: {image_path}")

# --- 使用示例 ---
if __name__ == "__main__":
    # 定义输入的PDF文件路径
    pdf_file = "/home/ubuntu/NCCN/NCCN_DATA/EsophagealandEsophagogastricJunctionCancers_2025.V3_EN.pdf"  # <--- 请将此替换为您的PDF文件路径

    # 定义输出图片的文件夹
    output_dir = "/home/ubuntu/NCCN/NCCN_DATA/EsophagealandEsophagogastricJunctionCancers_2025.V3_EN"

    # 检查PDF文件是否存在
    if not os.path.exists(pdf_file):
        print(f"错误: 文件 '{pdf_file}' 不存在。")
    else:
        convert_pdf_to_images(pdf_file, output_dir)
        print("\n所有页面转换完成！")