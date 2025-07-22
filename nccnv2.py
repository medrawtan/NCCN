import os
import base64
from openai import OpenAI
import json  # <-- 修改点 1: 引入json库

# --- 配置部分 (保持不变) ---
API_KEY = "sk-24b2db2c803045138672958e7197d510"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
IMAGE_DIRECTORY = "/home/ubuntu/NCCN/NCCN_DATA/Non-SmallCellLungCancer_2025.V5_EN/"
START_IMAGE_NUM = 1
END_IMAGE_NUM = 218
# --- 修改点 2: 更改输出文件名，使用.jsonl后缀 ---
OUTPUT_FILENAME = "NCCN_Non-SmallCellLungCancer_Summary.jsonl"

# --- image_to_base64 函数 (保持不变) ---
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"警告: 文件未找到 {image_path}")
        return None

# --- 修改点 3: 大幅优化 analyze_image 函数 ---
def analyze_image(client, image_base64):
    """
    调用AI模型分析图片，并要求返回包含原文和总结的JSON对象。
    """
    # 优化后的Prompt，要求模型同时进行OCR和总结，并以JSON格式返回
    # 这是您可以用在 analyze_image 函数中的、重写后的 prompt_text
    prompt_text = """
    您将看到一页NCCN指南的图片。您的任务是分析这张图片，并严格按照要求返回一个JSON对象。

    请执行以下两个【独立】的任务：

    1. **英文原文提取 (用于后续匹配)**:
    - **目标**: 为后续的超链接匹配提供一个可靠的文本索引。
    - **操作**: 请精确地从图片中提取所有可见的英文文字。尽可能保持原文的词语和大致顺序，这对于匹配至关重要。

    2. **综合中文总结 (基于图片理解)**:
    - **目标**: 生成一份人类易于理解的、包含完整逻辑的中文知识。
    - **操作**: 请【综合理解整张图片的所有信息】，包括文字、箭头、线条和整体布局。对于流程图，您必须理解图中的分支、判断条件和逻辑流向。基于您对【整张图片】的理解，生成一段详细、准确的中文总结，清晰地描述页面上的医学知识或诊疗流程。

    请将这两个独立任务的结果整合进一个JSON对象中，并严格按以下格式输出，不要包含任何额外的解释或代码块标记：
    {
    "original_text": "这里是任务1提取出的完整英文原文...",
    "chinese_summary": "这里是任务2生成的综合中文总结..."
    }
    """
    try:
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant that strictly follows user instructions and outputs in JSON format."}]},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    },
                    {"type": "text", "text": prompt_text},
                ]}
            ],
            # 您可以根据需要调整其他参数
        )
        
        # 获取模型返回的原始字符串
        response_content = completion.choices[0].message.content
        
        # 解析模型返回的JSON字符串
        # 增加json.loads的错误处理，以防模型返回非JSON格式
        try:
            # 找到JSON对象的部分，避免被可能存在的 ```json ... ``` 包围
            if '```json' in response_content:
                json_part = response_content.split('```json')[1].split('```')[0].strip()
            else:
                json_part = response_content.strip()
            
            parsed_json = json.loads(json_part)
            return parsed_json
        except (json.JSONDecodeError, IndexError) as e:
            print(f"错误: 模型返回的内容不是合法的JSON格式。错误详情: {e}")
            print(f"模型原始返回: {response_content}")
            return None

    except Exception as e:
        print(f"调用API时发生错误: {e}")
        return None

# --- 修改点 4: 大幅优化 main 函数 ---
def main():
    """主执行函数，遍历图片，分析并以JSON Lines格式保存结果。"""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 不再使用字符串拼接，而是创建一个结果列表来存放字典
    all_results = []
    print("开始处理NCCN指南图片...")

    for i in range(START_IMAGE_NUM, END_IMAGE_NUM + 1):
        image_filename = f"page_{i}.png"
        image_path = os.path.join(IMAGE_DIRECTORY, image_filename)
        
        print(f"\n--- 正在处理: {image_path} ---")

        image_base64 = image_to_base64(image_path)
        
        if image_base64:
            # 调用API进行分析，期望返回一个字典
            result_data = analyze_image(client, image_base64)
            
            if result_data and 'original_text' in result_data and 'chinese_summary' in result_data:
                print(f"成功获取并解析了 '{image_filename}' 的内容。")
                # 将页码和其他信息一起存入一个完整的字典中
                page_result = {
                    "page_number": i,
                    "title": f"page_{i}",
                    "chinese_summary": result_data["chinese_summary"],
                    "original_text": result_data["original_text"]
                }
                all_results.append(page_result)
            else:
                print(f"未能获取或解析 '{image_filename}' 的有效内容。")
    
    if not all_results:
        print("\n处理完成，但没有生成任何有效的JSON结果。请检查图片路径、API连接和Prompt。")
        return

    # 将所有结果逐行写入JSON Lines文件
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            for item in all_results:
                # json.dumps将字典转为JSON字符串
                # ensure_ascii=False 确保中文字符能被正确写入
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"\n🎉 全部处理完成！所有结构化结果已保存到文件: {OUTPUT_FILENAME}")
    except IOError as e:
        print(f"\n写入文件时出错: {e}")


# 运行主程序
if __name__ == "__main__":
    main()