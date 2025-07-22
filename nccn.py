import os
import base64
from openai import OpenAI

# --- 配置部分 ---
# API凭证和基础URL
API_KEY = "sk-24b2db2c803045138672958e7197d510"  # 您的API Key
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1" # 您的API Base URL

# 图片文件所在的目录
IMAGE_DIRECTORY = "/home/ubuntu/NCCN/NCCN_DATA/lungcancer/"

# 要处理的图片范围 (例如，从 1 到 20)
START_IMAGE_NUM = 1
END_IMAGE_NUM = 57

# 输出的文本文件名
OUTPUT_FILENAME = "nccn_lung_cancer_summary.txt"

# --- 函数定义 ---

def image_to_base64(image_path):
    """将图片文件转换为base64编码的字符串。"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"警告: 文件未找到 {image_path}")
        return None

def analyze_image(client, image_base64):
    """调用AI模型分析单个图片并返回总结文本。"""
    try:
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    },
                    {"type": "text", "text": "下面让你阅读的是NCCN指南里的内容，每张图片都是其中一页，请详细阅读图片里的医学信息，并将其总结成清晰的中文知识。如果内容是诊疗指南的流程图，请准确理解图中的诊疗步骤、判断条件和分支逻辑，然后用文本形式将其完整地描述出来。"},
                ]}
            ],
            # 您可以根据需要调整其他参数，例如 temperature
            # temperature=0.0,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"调用API时发生错误: {e}")
        return None

# --- 主程序 ---

def main():
    """主执行函数，遍历图片，分析并保存结果。"""
    # 初始化OpenAI客户端
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    all_summaries = []
    print("开始处理NCCN指南图片...")

    # 遍历指定范围的图片
    for i in range(START_IMAGE_NUM, END_IMAGE_NUM + 1):
        image_filename = f"page_{i}.png"
        image_path = os.path.join(IMAGE_DIRECTORY, image_filename)
        
        print(f"\n--- 正在处理: {image_path} ---")

        # 1. 将图片转换为Base64
        image_base64 = image_to_base64(image_path)
        
        if image_base64:
            # 2. 调用API进行分析
            summary = analyze_image(client, image_base64)
            
            if summary:
                # 3. 将结果添加到汇总列表中
                print(f"成功获取 '{image_filename}' 的总结。")
                all_summaries.append(f"=============== {image_filename} 总结 ===============\n")
                all_summaries.append(summary)
                all_summaries.append("\n\n") # 添加一些空行以分隔不同页面的内容
            else:
                print(f"未能获取 '{image_filename}' 的总结。")
    
    # 4. 检查是否收集到了任何总结
    if not all_summaries:
        print("\n处理完成，但没有生成任何有效的总结内容。请检查图片路径和API连接。")
        return

    # 5. 将所有总结写入一个文件
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write("".join(all_summaries))
        print(f"\n🎉 全部处理完成！所有总结已统一保存到文件: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"\n写入文件时出错: {e}")


# 运行主程序
if __name__ == "__main__":
    main()