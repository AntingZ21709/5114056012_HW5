import streamlit as st
import google.generativeai as genai
import json
import re

# 預設的設計方案，以防 API 呼叫失敗
DEFAULT_SCHEME = {
    "background_color": "#0D1B2A",
    "title_color": "#E0E1DD",
    "body_color": "#FFFFFF",
    "accent_color": "#778DA9"
}

def get_ai_design_scheme(user_prompt: str) -> dict:
    """
    使用 Google Gemini API 根據使用者描述產生設計配色方案。

    Args:
        user_prompt: 使用者提供的風格描述，例如 "賽博龐克風" 或 "極簡商業風格"。

    Returns:
        一個包含 Hex 色碼的字典，格式如下：
        {
            "background_color": "#...",
            "title_color": "#...",
            "body_color": "#...",
            "accent_color": "#..."
        }
    """
    try:
        # 從 Streamlit secrets 讀取 API 金鑰
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("錯誤：找不到 GOOGLE_API_KEY。請在 .streamlit/secrets.toml 中設定。")
            return DEFAULT_SCHEME

        genai.configure(api_key=api_key)

        # 使用最新穩定的 Gemini 模型
        model = genai.GenerativeModel('models/gemini-2.5-flash')

        # 建立一個精確的 Prompt，要求 Gemini 回傳純 JSON
        prompt = f"""
        你是一位專業的 UI/UX 設計師。根據以下的使用者風格描述，請提供一組專業的配色方案。
        使用者描述："{user_prompt}"

        請嚴格按照以下 JSON 格式回傳，不要包含任何額外的文字、註解或程式碼區塊標記 (```json ... ```)。
        只需回傳純粹的 JSON 物件。

        {{
            "background_color": "<Hex 色碼>",
            "title_color": "<Hex 色碼>",
            "body_color": "<Hex 色碼>",
            "accent_color": "<Hex 色碼>"
        }}
        """

        # 呼叫 API
        response = model.generate_content(prompt)
        
        # 從回應中提取純文字並解析 JSON
        text_content = response.text.strip()
        
        # 移除 ```json ``` 等包裝
        text_content = re.sub(r"^```(?:json)?", "", text_content, flags=re.IGNORECASE).strip()
        text_content = re.sub(r"```$", "", text_content).strip()
        
        # 嘗試直接擷取 JSON 物件
        json_match = re.search(r'\{[\s\S]*\}', text_content)
        
        if not json_match:
            st.error("AI 回傳的格式不符合預期的 JSON 結構。請檢查 AI 的回應。")
            return DEFAULT_SCHEME
            
        json_str = json_match.group(0)
        design_scheme = json.loads(json_str)

        # 驗證所有鍵是否存在
        required_keys = ["background_color", "title_color", "body_color", "accent_color"]
        if not all(key in design_scheme for key in required_keys):
            st.error("AI 回傳的 JSON 缺少必要的顏色欄位。請檢查 AI 的回應。")
            return DEFAULT_SCHEME

        return design_scheme

    except Exception as e:
        st.error(f"與 AI API 互動時發生錯誤：{e}")
        return DEFAULT_SCHEME


if __name__ == '__main__':
    # 這個區塊主要用於直接測試，在 Streamlit 環境中不會執行
    # 需要手動設定 secrets 來進行本地測試
    
    # 模擬 Streamlit secrets
    class StreamlitSecrets(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    st.secrets = StreamlitSecrets()
    # 執行前請將 "YOUR_API_KEY" 換成你的真實金鑰
    # st.secrets['GOOGLE_API_KEY'] = "YOUR_API_KEY"

    if st.secrets.get("GOOGLE_API_KEY") and st.secrets.get("GOOGLE_API_KEY") != "YOUR_API_KEY":
        print("正在測試 get_ai_design_scheme 函式...")
        test_prompt = "賽博龐克城市霓虹燈風格"
        scheme = get_ai_design_scheme(test_prompt)
        print(f"使用者提示：'{test_prompt}'")
        print("取得的設計方案：")
        print(json.dumps(scheme, indent=2))
    else:
        print("請在程式碼中設定 GOOGLE_API_KEY 以進行測試。")

    print("\n測試 API 失敗時的情況...")
    st.secrets['GOOGLE_API_KEY'] = None # 模擬 API Key 不存在
    scheme = get_ai_design_scheme("任何提示")
    print("取得的設計方案 (預期為預設值):")
    print(json.dumps(scheme, indent=2))