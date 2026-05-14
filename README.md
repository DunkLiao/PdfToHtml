# PDF to Reveal.js Presentation

將資料夾中的 PDF 批次轉成「每頁一張 WebP 圖片」，並自動產生可直接開啟的 Reveal.js 靜態簡報頁。

## 專案用途

這個工具適合把 PDF 內容轉成純前端簡報網頁，例如放到靜態網站、內部文件站或檔案伺服器。不需要後端服務、Node.js、npm 或打包流程。

## 功能特色

- 遞迴掃描輸入資料夾內所有 `*.pdf`
- 每個 PDF 頁面轉為一張 WebP 圖片（`page-0001.webp`...）
- 產生文件清單入口 `presentation/index.html`
- 每份 PDF 產生一個 Reveal.js 簡報頁
- 使用本機端 Reveal.js CSS 與 JavaScript
- 支援鍵盤翻頁、頁碼、進度條、總覽模式與 `F` 全螢幕快捷鍵
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
python .\pdf_to_static.py --input-dir .\test-pdfs --output-dir .\presentation --dpi 144 --quality 80
```

也可以省略 `--output-dir`，預設會輸出到 `presentation`：

```powershell
python .\pdf_to_static.py --input-dir .\test-pdfs --dpi 144 --quality 80
```

執行完成後，開啟：

```text
.\presentation\index.html
```

首頁會列出每份 PDF，例如 `金融市場晨訊-20260420` 與 `金融市場晨訊-20260421`。點進文件連結後才會進入對應的投影片頁。

`S` 會在同一個簡報頁右側切換講者備註面板，不會另開講者視窗。

## 參數說明

| 參數 | 必填 | 預設值 | 說明 |
| --- | --- | --- | --- |
| `--input-dir` | 是 | - | 輸入 PDF 的根資料夾（會遞迴掃描） |
| `--output-dir` | 否 | `presentation` | 輸出簡報、WebP 圖片與 Reveal.js 資源的目錄 |
| `--dpi` | 否 | `144` | PDF 頁面渲染解析度，越高越清楚但檔案越大 |
| `--quality` | 否 | `80` | WebP 品質，範圍 `0-100` |

## 執行流程

1. 解析命令列參數並檢查合法性（目錄存在、`dpi > 0`、`quality` 在 0-100）
2. 遞迴搜尋輸入目錄下所有 PDF
3. 對每個 PDF：
   - 以 PDF 名稱產生 slug（並保證唯一）
   - 逐頁渲染為 WebP 圖片
   - 每張圖片成為該 PDF 簡報頁的一張投影片
   - 產生 `<pdf-slug>.html`
4. 最後產生清單入口 `presentation/index.html`

## 輸出結構

```text
presentation\
  index.html
  <pdf-slug>.html
  vendor\
    reveal.js\
      dist\
        reset.css
        reveal.css
        reveal.js
        theme\
          white.css
  <pdf-slug>\
    page-0001.webp
    page-0002.webp
    ...
```

## 操作方式

在 `presentation/index.html` 點選文件連結後，進入該文件的投影片頁：

- 左右方向鍵：切換投影片
- 空白鍵：前進
- `F`：切換瀏覽器全螢幕
- `Esc`：進入或離開投影片總覽模式
- `S`：在同頁切換講者備註面板
- `R`：重置總時間與本頁時間
- `B`：切換黑畫面暫停

## 講者備註與逐步提示

可在 `presentation/notes.md` 用 Markdown 表格設定每頁的逐步提示與講者備註。根目錄的 `notes_sample.md` 是範本；第一次使用時，可依範本內容建立或更新 `presentation/notes.md`：

```markdown
| 文件 | 頁碼 | 逐步提示 1 | 逐步提示 2 | 講者備註 |
| --- | ---: | --- | --- | --- |
| AI在日常辦公與工作中的多元應用 | 1 | 封面 | 說明應用場景 | 開場介紹這份簡報的目的。 |
```

- `文件`：PDF 檔名，不含 `.pdf`
- `頁碼`：PDF 頁碼，從 `1` 開始
- `逐步提示 1`、`逐步提示 2`：顯示在投影片上的 Reveal.js fragment
- `講者備註`：顯示在 `S` 同頁講者備註面板

未列在 `presentation/notes.md` 的頁面不會顯示投影片逐步提示，講者備註保持空白。若表格內容需要換行，請輸入 `\n`；若文字中需要直線符號，請寫成 `\|`。

修改 `presentation/notes.md` 後，請重新執行轉檔命令，新的講者備註才會寫入產生的簡報 HTML。`presentation/notes.md` 屬於簡報設定檔，請不要和產生的 HTML 或圖片一起刪除；若誤刪，可用根目錄 `notes_sample.md` 重新建立。

## 使用批次檔（Windows）

專案提供 `run_convert.bat` 可一鍵執行。若你的環境路徑不同，請先修改批次檔內的輸入與輸出路徑。

## 錯誤與注意事項

- 若 `--input-dir` 不存在或不是資料夾，程式會中止並回報錯誤
- 若找不到任何 PDF，程式會中止並回報錯誤
- `--quality` 超出 `0-100` 或 `--dpi <= 0` 會中止
- 圖片與 HTML 可能很多，請預留足夠磁碟空間
- `presentation/vendor/` 內的 Reveal.js 檔案需保留，簡報才能離線開啟
