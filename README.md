# PDF to Static HTML

將資料夾中的 PDF 批次轉成「每頁一張 WebP 圖片」，並自動產生可直接部署的靜態 HTML 瀏覽頁。

## 專案用途

這個工具適合把 PDF 內容轉成純前端可瀏覽的頁面（例如放到靜態網站、內部文件站或檔案伺服器），不需要後端服務就能開啟閱讀。

## 功能特色

- 遞迴掃描輸入資料夾內所有 `*.pdf`
- 每個 PDF 轉為一組 WebP 圖片（`page-0001.webp`...）
- 每個 PDF 產生一個長頁面 HTML（由上到下瀏覽）
- 自動產生總入口 `index.html`
- 內建檔名 slug 去重邏輯（避免同名檔案衝突）

## 需求

- Python 3.10+
- 依賴套件：
  - `pypdfium2==4.30.0`
  - `Pillow==11.2.1`

## 安裝

```powershell
pip install -r requirements.txt
```

## 快速開始

```powershell
python .\pdf_to_static.py --input-dir .\test-pdfs --output-dir .\output --dpi 144 --quality 80
```

執行完成後，開啟：

```text
.\output\index.html
```

## 參數說明

| 參數 | 必填 | 預設值 | 說明 |
| --- | --- | --- | --- |
| `--input-dir` | 是 | - | 輸入 PDF 的根資料夾（會遞迴掃描） |
| `--output-dir` | 否 | `output` | 輸出目錄 |
| `--dpi` | 否 | `144` | PDF 頁面渲染解析度，越高越清楚但檔案越大 |
| `--quality` | 否 | `80` | WebP 品質，範圍 `0-100` |

## 執行流程

1. 解析命令列參數並檢查合法性（目錄存在、`dpi > 0`、`quality` 在 0-100）
2. 遞迴搜尋輸入目錄下所有 PDF
3. 對每個 PDF：
   - 以 PDF 名稱產生 slug（並保證唯一）
   - 逐頁渲染為影像，輸出為 WebP
   - 產生該 PDF 專屬 HTML（含所有頁面 `<img>`）
4. 最後彙整產生 `index.html`

## 輸出結構

```text
output\
  index.html
  clean_2026_financial_risk_masterclass\
    page-0001.webp
    page-0002.webp
    ...
  clean_2026_financial_risk_masterclass.html
  clean_2026_insight_finance_masterclass\
    page-0001.webp
    ...
  clean_2026_insight_finance_masterclass.html
```

## 使用批次檔（Windows）

專案提供 `run_convert.bat` 可一鍵執行。檔案內含以下設定：

- `PYTHON_EXE`：優先使用 `D:\ProgramData\anaconda3\python.exe`，不存在時退回 `python`
- `INPUT_DIR`：`D:\SourceCode\VibeCoding\PdfToHtml\test-pdfs`
- `OUTPUT_DIR`：`D:\SourceCode\VibeCoding\PdfToHtml\output`
- `DPI=144`、`QUALITY=80`

若你的環境路徑不同，請先修改 `run_convert.bat` 再執行。

## 錯誤與注意事項

- 若 `--input-dir` 不存在或不是資料夾，程式會中止並回報錯誤
- 若找不到任何 PDF，程式會中止並回報錯誤
- `--quality` 超出 `0-100` 或 `--dpi <= 0` 會中止
- 圖片與 HTML 可能很多，請預留足夠磁碟空間
