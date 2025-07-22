# import fitz  # PyMuPDF库
# import json

# def extract_final_internal_links(pdf_path):
#     """
#     最终优化版：提取PDF中所有内部链接关系，统一处理 GOTO 和 NAMED 类型。
#     """
#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         print(f"错误：无法打开或解析PDF文件 '{pdf_path}'. 错误信息: {e}")
#         return []

#     all_links_data = []

#     # 遍历每一页
#     for page_num, page in enumerate(doc):
#         words = page.get_text("words")
#         links = page.get_links()

#         for link in links:
#             # 核心逻辑变更：只要链接字典中包含 'page' 键，就认定它是内部链接
#             # 这同时涵盖了 kind=1 (GOTO) 和 kind=4 (NAMED) 的情况，因为PyMuPDF都为它们提供了'page'键
#             if 'page' in link:
#                 target_page = link['page']
                
#                 # 如果目标页码无效（例如小于0），则跳过
#                 if target_page < 0:
#                     continue

#                 link_rect = fitz.Rect(link['from'])
#                 anchor_words = [w[4] for w in words if fitz.Rect(w[:4]).intersects(link_rect)]
#                 anchor_text = " ".join(anchor_words)

#                 if not anchor_text:
#                     anchor_text = "[链接在非文本对象上]"

#                 link_data = {
#                     "source_page": page_num + 1,
#                     "anchor_text": anchor_text,
#                     "destination_page": target_page + 1,
#                     # "link_kind": link.get('kind', 0) # 记录链接类型以供参考
#                 }
#                 all_links_data.append(link_data)

#     doc.close()
#     return all_links_data

# # --- 使用示例 ---
# # 请确保这里的路径是正确的
# pdf_file = "/home/ubuntu/NCCN/NCCN_DATA/LungCancerScreening_2025.V1_EN.pdf"

# extracted_links = extract_final_internal_links(pdf_file)

# if extracted_links:
#     print(f"✅ 提取完成！共找到 {len(extracted_links)} 条内部链接。")
#     print("\n--- 提取结果示例 (前5条) ---")
#     for item in extracted_links[:5]:
#         print(json.dumps(item, indent=4, ensure_ascii=False))

#     output_file = "all_internal_links_final.json"
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(extracted_links, f, indent=4, ensure_ascii=False)
#     print(f"\n✅ 所有链接关系已成功保存到文件: {output_file}")
# else:
#     print("ℹ️ 未能从文档中提取到任何内部链接。")

import fitz  # PyMuPDF库
import json

def extract_final_internal_links(pdf_path):
    """
    最终优化版：提取PDF中所有内部链接关系，并过滤掉导航性链接。
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"错误：无法打开或解析PDF文件 '{pdf_path}'. 错误信息: {e}")
        return []

    # --- 修改点 1: 定义一个导航性关键词的“黑名单” ---
    # 您可以根据需要随时增删这个列表中的关键词
    NAVIGATIONAL_KEYWORDS = [
        'table of contents',
        'discussion',
        'index',
        'references',
        'abbreviations',
        'footnote', # 匹配 "footnote" 和 "footnotes"
        'continue',
        'members',
        'panel',
        'categories of evidence',
        'version'
    ]

    all_links_data = []

    # 遍历每一页
    for page_num, page in enumerate(doc):
        words = page.get_text("words")
        links = page.get_links()

        for link in links:
            if 'page' in link:
                target_page = link['page']
                if target_page < 0:
                    continue

                link_rect = fitz.Rect(link['from'])
                anchor_words = [w[4] for w in words if fitz.Rect(w[:4]).intersects(link_rect)]
                anchor_text = " ".join(anchor_words)

                if not anchor_text:
                    anchor_text = "[链接在非文本对象上]"

                # --- 修改点 2: 增加过滤逻辑 ---
                # 将锚文本转为小写，然后检查是否包含任何一个黑名单里的关键词
                # 如果包含，就用 continue 跳过这个链接，不处理它
                is_navigational = any(keyword in anchor_text.lower() for keyword in NAVIGATIONAL_KEYWORDS)
                if is_navigational:
                    print(f"  (已过滤导航链接: '{anchor_text}' -> p.{target_page + 1})")
                    continue
                # --- 过滤逻辑结束 ---

                link_data = {
                    "source_page": page_num + 1,
                    "anchor_text": anchor_text,
                    "destination_page": target_page + 1,
                }
                all_links_data.append(link_data)

    doc.close()
    return all_links_data

# --- 使用示例 (保持不变) ---
# 请确保这里的路径是正确的
pdf_file = "/home/ubuntu/NCCN/NCCN_DATA/Non-SmallCellLungCancer_2025.V5_EN.pdf"

extracted_links = extract_final_internal_links(pdf_file)

if extracted_links:
    print(f"\n✅ 提取完成！共找到 {len(extracted_links)} 条【语义】内部链接。")
    print("\n--- 提取结果示例 (前5条) ---")
    for item in extracted_links[:5]:
        print(json.dumps(item, indent=4, ensure_ascii=False))

    output_file = "Non-SmallCellLungCancerinternal_links_final.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_links, f, indent=4, ensure_ascii=False)
    print(f"\n✅ 所有有效链接关系已成功保存到文件: {output_file}")
else:
    print("ℹ️ 未能从文档中提取到任何有效的语义内部链接。")