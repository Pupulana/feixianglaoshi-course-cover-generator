import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
API_KEY = os.getenv("VOLC_API_KEY")
API_ENDPOINT = os.getenv("SEEDDREAM_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3/images/generations")
MODEL_ID = os.getenv("VOLC_MODEL", "doubao-seedream-4-5-251128")


def generate_cover(prompt, output_path="generated_cover.png"):
    """
    纯文生图模式生成封面
    
    Args:
        prompt: 生成提示词
        output_path: 输出文件路径
    
    Returns:
        生成的图片路径，失败返回 None
    """
    if not API_KEY:
        print("Error: 未找到 VOLC_API_KEY，请在 .env 文件中配置。")
        return None

    if not prompt:
        print("Error: Prompt 不能为空")
        return None

    print(f"使用的模型: {MODEL_ID}")
    print(f"使用的 Prompt: {prompt[:100]}...")

    # 硬编码的重要限制（强制追加到提示词末尾）
    restrictions = """
【重要限制】
⚠️ 禁止出现"飞象老师"或任何品牌名称和logo
⚠️ 除了大标题之外，不要有任何其他文字
⚠️ 画面以图像和视觉元素为主，不要其他文字装饰
⚠️ 不要英文，纯中文
"""
    
    # 将限制追加到提示词末尾
    final_prompt = prompt.strip() + "\n" + restrictions.strip()
    
    # 构造请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 构造请求体（纯文生图，无参考图）
    # API 使用标准尺寸，下载后再调整到目标尺寸
    payload = {
        "model": MODEL_ID,
        "prompt": final_prompt,  # 使用包含限制的完整提示词
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2560x1440",  # API 支持的标准尺寸，下载后缩放
        "stream": False,
        "watermark": False
    }

    try:
        print("正在发送 API 请求...")
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=120)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0]["url"]
                print(f"图片生成成功! URL: {image_url}")
                
                # 下载图片并调整尺寸
                print("正在下载并调整图片尺寸...")
                img_data = requests.get(image_url).content
                
                # 使用 PIL 调整到目标尺寸 1077x605（保持比例不变形）
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_data))
                
                # 目标尺寸和比例
                target_w, target_h = 1077, 605
                target_ratio = target_w / target_h  # ≈1.78 (16:9)
                
                # 原图尺寸和比例
                orig_w, orig_h = img.size
                orig_ratio = orig_w / orig_h
                
                # 先裁剪到目标比例（中心裁剪）
                if orig_ratio > target_ratio:
                    # 原图太宽，裁剪两边
                    new_w = int(orig_h * target_ratio)
                    left = (orig_w - new_w) // 2
                    img = img.crop((left, 0, left + new_w, orig_h))
                elif orig_ratio < target_ratio:
                    # 原图太高，裁剪上下
                    new_h = int(orig_w / target_ratio)
                    top = (orig_h - new_h) // 2
                    img = img.crop((0, top, orig_w, top + new_h))
                
                # 缩放到目标尺寸
                img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                img_resized.save(output_path, "PNG")
                
                print(f"封面图已保存为: {output_path} (1077x605)")
                return output_path
            else:
                print("生成成功但未找到图片 URL。响应内容:", result)
                return None
        else:
            print(f"API 请求失败: Status {response.status_code}")
            print("Response:", response.text)
            return None

    except Exception as e:
        print(f"发生错误: {e}")
        return None


if __name__ == "__main__":
    test_prompt = "课程封面图，大标题「三角形内角和」，几何图形，网格背景，专业教育风格，16:9横版"
    generate_cover(test_prompt)
