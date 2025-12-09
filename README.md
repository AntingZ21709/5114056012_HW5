# PPT AI 設計師 (PPT AI Designer)

一份利用大型語言模型（LLM）能力，自動化重新設計 PowerPoint 簡報的 Python 專案。使用者僅需上傳 PPTX 檔案、輸入風格描述，AI 便能為您生成全新的配色方案，並可選擇套用不同的版面配置，一鍵完成簡報美化。

![應用程式介面](https://i.imgur.com/your-image-url.png) <!-- 請替換為您的應用程式截圖 -->

---

## 專案介紹

本專案旨在探索生成式 AI 在文件處理與設計領域的應用潛力。我們打造了一個基於 Streamlit 的 Web 應用程式，它串接了 Google Gemini 模型，並利用 `python-pptx` 函式庫對 PowerPoint 檔案進行深度操作。

使用者可以上傳既有的簡報，透過自然語言（例如：“請幫我設計一個賽博龐克風格的簡報”）來指導 AI 生成一組包含背景、標題、內文和強調色的 JSON 格式配色方案。接著，程式會將此配色應用於整個簡報。

此外，我們還實現了更進階的版面配置重塑功能，能夠讀取簡報中的內容，並將其填充到使用者選定的一套全新版面中，實現結構與風格的雙重革新。

### 主要功能

- **AI 驅動配色**：根據使用者輸入的風格描述，動態生成和諧的色彩組合。
- **版面一鍵重塑**：提取原始投影片內容，並將其應用於全新的投影片版面配置。
- **網頁操作介面**：使用 Streamlit 搭建，提供直覺的檔案上傳、文字輸入與下載功能。
- **完整的檔案處理**：支援 PPTX 檔案的讀取、修改與存儲。

---

## 如何本地端執行 (Installation & Run)

請依照以下步驟在您的本地環境中設置並執行此專案。

### 1. 複製專案

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2. 安裝依賴套件

本專案使用 `pip` 管理套件。請執行以下指令安裝所有必要的函式庫：

```bash
pip install -r requirements.txt
```

### 3. 設定 API 金鑰

您需要一個 Google Gemini API 金鑰才能讓 AI 功能正常運作。

- 在專案根目錄下，建立一個名為 `.streamlit` 的資料夾。
- 在 `.streamlit` 資料夾中，建立一個名為 `secrets.toml` 的檔案。
- 在 `secrets.toml` 檔案中，貼上以下內容，並將 `YOUR_API_KEY` 替換成您自己的金鑰：

```toml
# .streamlit/secrets.toml

GEMINI_API_KEY = "YOUR_API_KEY"
```

### 4. 執行應用程式

一切準備就緒後，執行以下指令即可啟動 Streamlit 應用程式：

```bash
streamlit run app.py
```

應用程式將在您的預設瀏覽器中開啟。

---

## 技術實現細節

### 1. 如何解決 Hex 色碼轉 RGB 的問題

- **問題**：Gemini 模型根據我們的 Prompt 設計，回傳的是通用的 Hex 格式色碼（例如 `#FFFFFF`）。然而，`python-pptx` 函式庫在設定顏色時，需要的是 RGB 元組（例如 `(255, 255, 255)`）。
- **解決方案**：我們在 `utils.py` 中編寫了一個名為 `hex_to_rgb` 的輔助函式。此函式負責將 Hex 色碼字串解析並轉換為 `python-pptx` 可接受的 RGB 格式。

    ```python
    # utils.py
    def hex_to_rgb(hex_color):
        """將 Hex 顏色字串轉換為 RGB 元組。"""
        hex_color = hex_color.lstrip('#')
        # ... 轉換邏輯 ...
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    ```

### 2. 如何設計 Prompt 讓 Gemini 回傳 JSON

- **挑戰**：要讓大型語言模型穩定地回傳結構化資料（而不是一段自然語言文字），需要精心設計 Prompt。
- **解決方案**：我們在 `ai_utils.py` 中採用了 "Few-shot Prompting" 的技巧，並給予模型非常明確的指令。

    1.  **角色扮演**：我們讓模型扮演一位「簡報設計專家」。
    2.  **明確指令**：我們直接命令模型「你必須只回傳一個 JSON 物件」，杜絕任何額外的文字描述。
    3.  **提供 Schema**：我們定義了 JSON 的結構，包含 `background_color`, `title_color`, `body_color`, 和 `accent_color` 這四個鍵。
    4.  **提供範例**：我們在 Prompt 中提供了一對「使用者輸入」與「理想 JSON 輸出」的範例，讓模型能從中學習。

    透過這種方式，我們確保了 API 回傳的資料可以直接被 Python 的 `json` 模組解析，增強了系統的穩定性。

---

## 遇到的困難與解決方案

在開發過程中，我們主要解決了以下幾個核心挑戰：

### 挑戰 1：僅有顏色變化，版面配置無變化

- **問題**：初版功能完成後，我們發現雖然顏色可以成功替換，但選擇新的版面配置後，生成的簡報看起來沒有任何結構上的改變。
- **原因**：經過追蹤，發現 `_get_slide_content` 函式的內容提取邏輯過於嚴格。它只尋找那些被 `python-pptx` 明確標記為 `PP_PLACEHOLDER.BODY` 或 `PP_PLACEHOLDER.OBJECT` 的標準預留位置。如果使用者上傳的簡報內文是放在普通的文字方塊 (Text Box) 中，程式便無法提取到任何內容，導致後續的版面重建步驟被跳過。
- **解決方案**：我們重構了 `_get_slide_content` 函式，使其更加穩健。新的邏輯是：
    1.  優先尋找標準的內容預留位置。
    2.  如果找不到，則啟動**後備策略**：遍歷該投影片上的所有圖案 (shapes)，並將**文字量最多的那個圖案**的內容認定為是主要內文。
    
    這個改進使得內容提取功能更具彈性，能夠適應更多不規範的簡報格式。

### 挑戰 2：處理 `python-pptx` 的 API 錯誤

- **問題**：在開發過程中，我們頻繁遇到來自 `python-pptx` 函式庫的 `ValueError: shape is not a placeholder` 錯誤。
- **原因**：此錯誤發生在我們的程式碼試圖存取一個普通圖案（非預留位置）的 `placeholder_format` 屬性時。我們最初使用了 `try...except AttributeError` 來捕捉這個錯誤，但後來發現函式庫實際拋出的是 `ValueError`，導致錯誤處理失效。
- **解決方案**：我們放棄了不穩定的 `try...except` 寫法，改為在存取任何預留位置相關屬性前，先使用 `if shape.is_placeholder:` 進行明確和安全的檢查。這個修正應用到了 `change_text_style` 和 `_get_slide_content` 等多個函式中，從根本上解決了這個問題，提高了程式碼的穩定性。

```python
# 修正前的錯誤寫法
try:
    is_title = shape.placeholder_format.type == PP_PLACEHOLDER.TITLE
except AttributeError:
    is_title = False

# 修正後的安全寫法
is_title = False
if shape.is_placeholder:
    if shape.placeholder_format.type == PP_PLACEHOLDER.TITLE:
        is_title = True
```
