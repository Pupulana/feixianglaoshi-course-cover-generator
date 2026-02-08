# 飞象课程封面生成器 (Feixiang Course Cover Generator)

这是一个自动化工具，用于将在线教学动画（HTML URL）转换为精美的 16:9 课程封面。

它包含三个主要步骤：
1.  **截图**: 自动截取网页内容。
2.  **分析**: 使用视觉大模型 (Doubao Vision) 理解画面，生成绘画提示词 (Prompt)。
3.  **生成**: 使用文生图模型 (SeedDream 4.5) 生成最终封面。

## 🚀 快速开始

### 1. 环境准备

确保您已安装 Python 3.8+。

安装必要的依赖库：
```bash
pip install -r requirements.txt
playwright install chromium
```
*(如果没有 `requirements.txt`，请运行: `pip install streamlit playwright requests python-dotenv`)*

### 2. 配置 API Key

在项目根目录下创建一个名为 `.env` 的文件（可以复制 `.env.example`）。
填入您的火山引擎 (Volcengine) API Key 和相关模型 ID：

```ini
# .env 文件内容示例
VOLC_API_KEY=您的API_KEY

# 视觉模型 (用于分析截图)
VOLC_VISION_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3/responses
VOLC_VISION_MODEL=doubao-seed-1-6-251015

# 绘画模型 (用于生成封面)
SEEDDREAM_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3/images/generations
VOLC_MODEL=doubao-seedream-4-5-251128
```

### 3. 启动应用

在终端中运行：
```bash
streamlit run app.py
```

浏览器会自动打开操作界面（通常是 `http://localhost:8501`）。

---

## 📖 使用指南

1.  **输入 URL**: 在左侧输入框填入教学动画的链接。
2.  **Step 1: Capture & Analyze**: 点击按钮。
    - 系统会自动截图。
    - 视觉模型会分析截图并生成一段英文 Prompt。
3.  **编辑 Prompt**: 在左下角的文本框中，您可以查看并修改生成的 Prompt。
4.  **Step 2: Generate Cover**: 点击右侧的按钮。
    - AI 将根据 Prompt 生成最终的 16:9 封面图。
    - 生成结果会显示在右侧，并自动保存为 `generated_cover.png`。

## 📂 文件说明
- `app.py`: 前端界面主程序。
- `capture_screenshot.py`: 网页截图模块 (Playwright)。
- `analyze_image.py`: 视觉分析模块 (Volcengine Vision)。
- `generate_cover.py`: 封面生成模块 (SeedDream 4.5)。
