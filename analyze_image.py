import os
import base64
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VOLC_API_KEY")
VISION_ENDPOINT = os.getenv("VOLC_VISION_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3/responses")
VISION_MODEL = os.getenv("VOLC_VISION_MODEL", "doubao-seed-1-6-251015")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_image(image_path):
    """
    分析动画截图并生成高质量封面提示词
    
    Args:
        image_path: 动画截图路径
    
    Returns:
        dict: {"thinking": 思考过程, "prompt": 文生图提示词}
    """
    if not API_KEY:
        return {"thinking": "", "prompt": "Error: API Key not found."}

    base64_image = encode_image(image_path)
    
    instruction = """你是一位顶级的 AI 绘画提示词专家，专门为在线教育课程设计封面。

【任务】
仔细分析这张教学动画截图，然后生成一段详细、专业、高质量的图像生成提示词。

【第一步：内容分析】
1. 识别课程主题（数学/物理/化学/语文/英语/信息科技等）
2. 提取核心知识点
3. 确定目标学生群体（小学/初中/高中）
4. 思考适合的视觉风格

【第二步：设计大标题】
- 必须准确概括课程核心内容
- 4-8个中文字，简洁有力

【第三步：生成详细提示词】
提示词必须包含以下维度：

1. **画面主体**（30%）- 具体描述视觉元素的形状、大小、位置
2. **背景与环境**（20%）- 背景类型、空间感
3. **风格与质感**（25%）- 艺术风格、材质、光影效果
4. **配色方案**（15%）- 主色调+辅助色+点缀色
5. **构图与布局**（10%）- 标题位置、元素排列

【重要限制】
⚠️ 禁止出现"飞象老师"或任何品牌名称和logo
⚠️ 除了大标题之外，不要有任何其他文字
⚠️ 画面以图像和视觉元素为主，不要其他文字装饰
⚠️ 不要英文，纯中文

【输出格式】
请严格按以下格式输出：
（在这里写完整的文生图提示词，不少于150字，写成自然流畅的描述段落）
"""

    content = [
        {
            "type": "input_image",
            "image_url": f"data:image/png;base64,{base64_image}"
        },
        {
            "type": "input_text",
            "text": instruction
        }
    ]

    payload = {
        "model": VISION_MODEL,
        "input": [
            {
                "role": "user",
                "content": content
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(VISION_ENDPOINT, headers=headers, json=payload, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            
            # 解析 doubao-seed-1-6 的响应格式
            # output 数组包含：[{type: "reasoning", summary: [...]}, {type: "message", content: [...]}]
            thinking = ""
            prompt = ""
            
            if "output" in result:
                for item in result["output"]:
                    # 提取思考过程
                    if item.get("type") == "reasoning" and "summary" in item:
                        for s in item["summary"]:
                            if s.get("type") == "summary_text":
                                thinking = s.get("text", "").strip()
                    
                    # 提取实际提示词
                    if item.get("type") == "message" and "content" in item:
                        for c in item["content"]:
                            if c.get("type") == "output_text":
                                prompt = c.get("text", "").strip()
                
                return {"thinking": thinking, "prompt": prompt}
            
            # 兼容其他可能的格式
            elif "data" in result and "message" in result["data"]:
                return {"thinking": "", "prompt": result["data"]["message"]["content"].strip()}
            elif "choices" in result:
                return {"thinking": "", "prompt": result["choices"][0]["message"]["content"].strip()}
            else:
                return {"thinking": "", "prompt": f"Response format unclear: {json.dumps(result, ensure_ascii=False)}"}
        else:
            return {"thinking": "", "prompt": f"Error: API Request failed with status {response.status_code}. Info: {response.text}"}

    except Exception as e:
        return {"thinking": "", "prompt": f"Error analyzing image: {e}"}


def parse_response(raw_content: str) -> dict:
    """解析模型返回的内容，提取 thinking 和 prompt"""
    import re
    
    thinking = ""
    prompt = ""
    
    # 提取 <thinking>...</thinking>
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', raw_content, re.DOTALL)
    if thinking_match:
        thinking = thinking_match.group(1).strip()
    
    # 提取 <prompt>...</prompt>
    prompt_match = re.search(r'<prompt>(.*?)</prompt>', raw_content, re.DOTALL)
    if prompt_match:
        prompt = prompt_match.group(1).strip()
    else:
        # 如果没有标签，整个内容作为 prompt
        prompt = raw_content
    
    return {"thinking": thinking, "prompt": prompt}


if __name__ == "__main__":
    if os.path.exists("input_screenshot.png"):
        result = analyze_image("input_screenshot.png")
        print("=== 思考过程 ===")
        print(result["thinking"])
        print("\n=== 文生图提示词 ===")
        print(result["prompt"])
    else:
        print("请先运行 capture_screenshot.py 生成测试图片。")
