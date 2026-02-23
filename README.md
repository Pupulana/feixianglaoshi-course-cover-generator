# 🐘 飞象课程封面生成器

从教学动画一键生成精美课程封面。

## 功能介绍

### 📸 单个生成
1. 输入教学动画的 URL 链接
2. 系统自动截取动画画面
3. AI 分析内容并生成封面设计提示词
4. 一键生成 1077×605 精美封面
5. 下载保存

### 📋 批量生成
1. 准备 Excel 文件，包含 URL 列
2. 上传 Excel 文件
3. 点击「开始批量生成」
4. 实时查看每个链接的处理进度
5. 批量导出所有生成的封面

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env`，填入你的 API Key：
```
VOLC_API_KEY=你的火山引擎API密钥
```

### 3. 启动应用
```bash
./.venv/bin/streamlit run app.py
```

### 4. 打开浏览器
访问 http://localhost:8501

## Excel 格式要求

批量生成时，Excel 文件需包含 `URL` 列，每行一个链接：

| URL |
|-----|
| https://xxx.html |
| https://yyy.html |
| https://zzz.html |

## 输出规格

- 尺寸：1077 × 605 像素
- 格式：PNG
- 比例：16:9 横版
