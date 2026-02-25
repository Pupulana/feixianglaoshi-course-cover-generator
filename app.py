import streamlit as st
import os
import pandas as pd
import zipfile
import io
import shutil
from capture_screenshot import capture_from_url
from analyze_image import analyze_image
from generate_cover import generate_cover
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide", page_title="飞象课程封面生成器")

st.title("飞象老师封面生成器")

# Sidebar
with st.sidebar:
    st.header("⚙️ 配置")
    api_key_status = "✅ 已配置" if os.getenv("VOLC_API_KEY") else "❌ 未配置"
    st.info(f"API Key: {api_key_status}")
    st.info(f"Vision 模型: {os.getenv('VOLC_VISION_MODEL', 'doubao-seed-1-6')}")
    st.info(f"生成模型: {os.getenv('VOLC_MODEL', 'doubao-seedream-4-5')}")

tab1, tab2 = st.tabs(["📸 单个生成", "📋 批量生成"])

# ========== Tab 1 ==========
with tab1:
    st.markdown("输入动画 URL → 智能分析 → 一键生成精美封面")
    col1, col2 = st.columns(2)

    with col1:
        st.header("1️⃣ 输入")
        url = st.text_input("教学动画 URL", "https://musk-online.fbcontent.cn/pub-musk-ai-studio/workflow/file/document/VcXtodDJ7Zeep4GcJ8vMxT.html")
        
        if st.button("📸 截图并分析", type="primary"):
            with st.spinner("正在截取动画画面..."):
                screenshot_path = capture_from_url(url)
            if screenshot_path and os.path.exists(screenshot_path):
                st.session_state['screenshot'] = screenshot_path
                st.image(screenshot_path, caption="动画截图", use_container_width=True)
                with st.spinner("正在分析内容并生成提示词..."):
                    result = analyze_image(screenshot_path)
                    st.session_state['thinking'] = result.get("thinking", "")
                    st.session_state['prompt'] = result.get("prompt", "")
            else:
                st.error("截图失败，请检查 URL 是否可访问。")

        if 'thinking' in st.session_state and st.session_state['thinking']:
            with st.expander("💭 思考过程", expanded=False):
                st.markdown(st.session_state['thinking'])
        
        if 'prompt' in st.session_state:
            st.subheader("🎯 文生图提示词")
            prompt = st.text_area("可编辑提示词", st.session_state['prompt'], height=200)
            st.session_state['prompt'] = prompt

    with col2:
        st.header("2️⃣ 输出")
        if 'prompt' in st.session_state and st.session_state['prompt']:
            if st.button("🎨 生成封面", type="primary"):
                with st.spinner("正在生成封面..."):
                    output_path = generate_cover(st.session_state['prompt'])
                    if output_path and os.path.exists(output_path):
                        st.success("✅ 封面生成成功！")
                        st.image(output_path, caption="生成的封面", use_container_width=True)
                        with open(output_path, "rb") as f:
                            st.download_button("📥 下载封面", f, "course_cover.png", "image/png")
                    else:
                        st.error("封面生成失败。")
        else:
            st.info("👈 请先完成第一步")

# ========== Tab 2 ==========
with tab2:
    st.markdown("上传 Excel 文件，批量生成课程封面")
    
    uploaded_file = st.file_uploader("上传 Excel 文件（需包含 URL 列）", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            url_col = None
            for col in df.columns:
                if 'url' in col.lower():
                    url_col = col
                    break
            if url_col is None:
                url_col = df.columns[0]
            
            urls = df[url_col].dropna().tolist()
            st.success(f"✅ 成功读取 {len(urls)} 个 URL")
            
            output_dir = "batch_output"
            screenshot_dir = os.path.join(output_dir, "screenshots")
            covers_dir = os.path.join(output_dir, "covers")
            os.makedirs(screenshot_dir, exist_ok=True)
            os.makedirs(covers_dir, exist_ok=True)
            
            # 初始化数据（增加 prompt 字段）
            if 'batch_data' not in st.session_state or st.session_state.get('batch_file_name') != uploaded_file.name:
                st.session_state['batch_data'] = [
                    {"序号": i+1, "URL": url, "状态": "⏳ 待处理", "截图路径": None, "封面路径": None, "prompt": ""}
                    for i, url in enumerate(urls)
                ]
                st.session_state['batch_file_name'] = uploaded_file.name
            
            # 按钮区域
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
            with btn_col1:
                start_btn = st.button("🚀 开始批量生成", type="primary")
            with btn_col2:
                # 批量导出
                success_rows = [r for r in st.session_state['batch_data'] if r.get('状态') == "✅ 成功"]
                if len(success_rows) > 0:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for r in success_rows:
                            if r.get('封面路径') and os.path.exists(r['封面路径']):
                                zf.write(r['封面路径'], os.path.basename(r['封面路径']))
                    zip_buffer.seek(0)
                    st.download_button(f"📦 批量导出 ({len(success_rows)})", zip_buffer, "batch_covers.zip", "application/zip", key="export_all")
                else:
                    st.button("📦 批量导出", disabled=True, key="export_disabled_empty")
            
            # 当点击开始按钮时，启动批量处理
            if start_btn:
                st.session_state['batch_processing_index'] = 0
                # 重置所有行状态
                for i in range(len(st.session_state['batch_data'])):
                    st.session_state['batch_data'][i]['状态'] = "⏳ 待处理"
                    st.session_state['batch_data'][i]['截图路径'] = None
                    st.session_state['batch_data'][i]['封面路径'] = None
                    st.session_state['batch_data'][i]['prompt'] = ""
                st.rerun()
            
            # 检查是否正在批量处理
            processing_idx = st.session_state.get('batch_processing_index', -1)
            total = len(st.session_state['batch_data'])
            is_processing = 0 <= processing_idx < total
            
            # 进度条
            if is_processing:
                st.progress(processing_idx / total, text=f"⏳ 正在处理 {processing_idx + 1}/{total}")
            elif processing_idx >= total:
                st.progress(1.0, text="✅ 全部完成！请检查各项结果，编辑提示词并确认后批量导出。")
            
            st.markdown("---")
            st.subheader("📊 处理结果")
            
            # ===== 渲染所有卡片（始终带完整交互控件） =====
            for idx, row in enumerate(st.session_state['batch_data']):
                with st.container():
                    # 头部信息行
                    hcols = st.columns([0.5, 3, 1, 1.5])
                    with hcols[0]:
                        st.markdown(f"### #{row['序号']}")
                    with hcols[1]:
                        # 使用 markdown 链接，截断显示但链接指向完整 URL
                        display_url = row['URL'][:55] + "..." if len(row['URL']) > 55 else row['URL']
                        st.markdown(f"🔗 [{display_url}]({row['URL']})")
                    with hcols[2]:
                        st.markdown(f"**{row['状态']}**")
                    with hcols[3]:
                        if row.get('封面路径') and os.path.exists(row['封面路径']):
                            with open(row['封面路径'], "rb") as f:
                                st.download_button("📥 下载", f.read(), f"cover_{row['序号']:03d}.png", "image/png", key=f"dl_{row['序号']}")
                        else:
                            st.markdown("*待生成*")
                    
                    # 截图 + 封面预览
                    icols = st.columns(2)
                    with icols[0]:
                        st.markdown("**📸 截图**")
                        if row['截图路径'] and os.path.exists(row['截图路径']):
                            st.image(row['截图路径'], use_container_width=True)
                        else:
                            st.info("待截图")
                    with icols[1]:
                        st.markdown("**🎨 生成封面**")
                        if row['封面路径'] and os.path.exists(row['封面路径']):
                            st.image(row['封面路径'], use_container_width=True)
                        else:
                            st.info("待生成")
                    
                    # 提示词编辑 + 重新生成
                    if row.get('prompt'):
                        st.markdown("**📝 提示词**")
                        new_prompt = st.text_area(
                            f"编辑提示词 #{row['序号']}",
                            value=row['prompt'],
                            height=150,
                            key=f"prompt_{row['序号']}",
                            label_visibility="collapsed",
                            disabled=is_processing
                        )
                        st.session_state['batch_data'][idx]['prompt'] = new_prompt
                        
                        regen_btn = st.button(
                            "🔄 重新生成", key=f"regen_{row['序号']}",
                            type="secondary", disabled=is_processing
                        )
                        if regen_btn and not is_processing:
                            current_prompt = st.session_state['batch_data'][idx]['prompt']
                            if current_prompt:
                                cover_save_path = os.path.join(covers_dir, f"cover_{idx+1:03d}.png")
                                with st.spinner(f"正在重新生成 #{row['序号']} 的封面..."):
                                    cover_path = generate_cover(current_prompt, output_path=cover_save_path)
                                    if cover_path and os.path.exists(cover_path):
                                        st.session_state['batch_data'][idx]['封面路径'] = cover_save_path
                                        st.session_state['batch_data'][idx]['状态'] = "✅ 成功"
                                        st.success(f"✅ #{row['序号']} 封面已重新生成！")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ #{row['序号']} 重新生成失败")
                            else:
                                st.warning("提示词不能为空")
                    
                    st.markdown("---")
            
            # ===== 批量处理：每次处理一个，然后 rerun =====
            if is_processing:
                i = processing_idx
                row_data = st.session_state['batch_data'][i]
                url = row_data['URL']
                
                screenshot_save_path = os.path.join(screenshot_dir, f"screenshot_{i+1:03d}.png")
                cover_save_path = os.path.join(covers_dir, f"cover_{i+1:03d}.png")
                
                st.session_state['batch_data'][i]['状态'] = "🔄 处理中..."
                
                try:
                    screenshot_path = capture_from_url(url)
                    if screenshot_path and os.path.exists(screenshot_path):
                        shutil.copy(screenshot_path, screenshot_save_path)
                        st.session_state['batch_data'][i]['截图路径'] = screenshot_save_path
                        
                        result = analyze_image(screenshot_path)
                        prompt = result.get("prompt", "")
                        st.session_state['batch_data'][i]['prompt'] = prompt
                        
                        if prompt and not prompt.startswith("Error"):
                            cover_path = generate_cover(prompt, output_path=cover_save_path)
                            if cover_path and os.path.exists(cover_path):
                                st.session_state['batch_data'][i]['封面路径'] = cover_save_path
                                st.session_state['batch_data'][i]['状态'] = "✅ 成功"
                            else:
                                st.session_state['batch_data'][i]['状态'] = "❌ 生成失败"
                        else:
                            st.session_state['batch_data'][i]['状态'] = "❌ 分析失败"
                    else:
                        st.session_state['batch_data'][i]['状态'] = "❌ 截图失败"
                except Exception as e:
                    st.session_state['batch_data'][i]['状态'] = "❌ 错误"
                
                # 处理完当前项，推进到下一个并 rerun
                st.session_state['batch_processing_index'] = i + 1
                if i + 1 >= total:
                    st.balloons()
                st.rerun()
        
        except Exception as e:
            st.error(f"读取 Excel 文件失败: {e}")

