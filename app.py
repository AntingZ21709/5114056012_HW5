import streamlit as st
import io
from pptx import Presentation

# 匯入我們自訂的模組，包含新的 apply_layout_to_slides 函式
from ai_utils import get_ai_design_scheme
from pptx_utils import change_slide_background, change_text_style, apply_layout_to_slides

st.set_page_config(page_title="PPT AI 設計師", layout="wide")

st.title("PPT AI 設計師 🎨")
st.write("上傳您的 PowerPoint 檔案，AI 將根據您的風格描述重新設計顏色，並可選擇套用全新的版面配置！")

# --- UI 元件 ---
uploaded_file = st.file_uploader("上傳您的 PPTX 檔案", type=["pptx"])

# 如果使用者上傳了檔案，則讀取其可用的版面配置
layout_options = {}
if uploaded_file is not None:
    try:
        # 使用 BytesIO 在記憶體中讀取檔案，以供分析版面
        file_bytes_for_layout = io.BytesIO(uploaded_file.getvalue())
        prs_for_layout = Presentation(file_bytes_for_layout)
        # 建立一個包含索引和名稱的字典，方便後續使用
        layout_options = {i: layout.name for i, layout in enumerate(prs_for_layout.slide_layouts)}
    except Exception as e:
        st.warning(f"無法讀取簡報的版面配置：{e}")

# 如果成功讀取到版面選項，則顯示下拉選單
selected_layout_index = None
if layout_options:
    st.subheader("📐 選擇新的版面配置 (可選)")
    st.write("選擇一個版面來重新產生您的投影片。新投影片將附加到簡報末尾，以便比較。")
    selected_layout_index = st.selectbox(
        "選擇要套用的版面:",
        options=list(layout_options.keys()),
        # 讓選項顯示得更清楚，例如 "版面 0: Title Slide"
        format_func=lambda x: f"版面 {x}: {layout_options[x]}"
    )

user_style_prompt = st.text_input(
    "請輸入您想要的設計風格描述 (例如: 賽博龐克風, 極簡主義, 復古)",
    value="Minimalist Blue"
)

# --- 主流程 ---
if st.button("✨ 開始設計"):
    if uploaded_file is not None:
        with st.spinner('AI 正在揮灑創意中，請稍候...'):
            try:
                # 步驟 1: 呼叫 Gemini 取得設計配色
                st.write("Step 1: 正在從 AI 獲取設計靈感...")
                design_scheme = get_ai_design_scheme(user_style_prompt)

                if not design_scheme:
                    st.error("無法從 AI 獲取設計方案，請檢查 API 金鑰或稍後再試。")
                else:
                    st.write("Step 2: AI 建議的配色方案如下...")
                    # 步驟 2: 顯示建議的配色
                    cols = st.columns(4)
                    # ... (顏色選擇器的程式碼不變)
                    with cols[0]:
                        st.color_picker("背景顏色", value=design_scheme["background_color"], disabled=True)
                    with cols[1]:
                        st.color_picker("標題顏色", value=design_scheme["title_color"], disabled=True)
                    with cols[2]:
                        st.color_picker("內文顏色", value=design_scheme["body_color"], disabled=True)
                    with cols[3]:
                        st.color_picker("強調顏色", value=design_scheme["accent_color"], disabled=True)

                    st.write("Step 3: 正在讀取並修改簡報...")
                    # 讀取上傳的檔案以進行修改
                    file_bytes = io.BytesIO(uploaded_file.getvalue())
                    prs = Presentation(file_bytes)

                    # 步驟 3.1: 變更顏色
                    change_slide_background(prs, design_scheme["background_color"])
                    change_text_style(prs, design_scheme["title_color"], design_scheme["body_color"])
                    
                    # 步驟 3.2: 如果使用者選擇了新的版面，就套用它
                    if selected_layout_index is not None:
                        st.write(f"Step 3.5: 正在套用新的版面配置 '{layout_options[selected_layout_index]}'...")
                        apply_layout_to_slides(prs, selected_layout_index)

                    st.write("Step 4: 產生預覽與下載連結...")
                    # 將修改後的 PPT 存入記憶體
                    output_buffer = io.BytesIO()
                    prs.save(output_buffer)
                    output_buffer.seek(0)

                    # 將結果存入 session state 供下載按鈕使用
                    st.session_state['processed_ppt'] = output_buffer
                    st.session_state['file_name'] = f"designed_{uploaded_file.name}"

                st.success("設計完成！您可以下載新的簡報。")

            except Exception as e:
                st.error(f"處理過程中發生錯誤：{e}")
    else:
        st.warning("請先上傳一個 PPTX 檔案！")

# --- 下載按鈕 ---
if 'processed_ppt' in st.session_state and st.session_state['processed_ppt'] is not None:
    st.download_button(
        label="📥 下載設計好的 PPTX",
        data=st.session_state['processed_ppt'],
        file_name=st.session_state.get('file_name', 'designed_presentation.pptx'),
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
