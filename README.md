# PDF 轉網頁簡報使用手冊

這個工具可以把資料夾中的 PDF 檔案轉成可在瀏覽器開啟的網頁簡報。轉換後，每一頁 PDF 會變成一張 WebP 圖片，並自動產生簡報首頁與播放頁面。

轉換完成的簡報不需要安裝伺服器，也不需要 Node.js 或 npm。只要用瀏覽器開啟產生的 `index.html`，就可以瀏覽與播放。

## 適用情境

- 將多份 PDF 批次轉成可播放的簡報網頁
- 在內部網站、檔案伺服器或本機資料夾中分享簡報
- 離線播放 PDF 內容，並支援鍵盤翻頁、全螢幕、頁碼與講者備註
- 為每頁加入簡短逐步提示或講者備註

## 使用前準備

請先確認電腦已安裝：

- Windows、macOS 或 Linux
- Python 3.10 或更新版本
- 可執行 PowerShell、命令提示字元或終端機

第一次使用前，請在此專案資料夾中安裝必要套件：

```powershell
pip install -r requirements.txt
```

若你的電腦同時安裝多個 Python 版本，也可以使用：

```powershell
python -m pip install -r requirements.txt
```

## 資料夾說明

常用檔案與資料夾如下：

| 名稱 | 用途 |
| --- | --- |
| `pdf_to_static.py` | 主要轉檔程式 |
| `run_convert.bat` | Windows 一鍵轉檔批次檔 |
| `test-pdfs/` | 範例 PDF 放置處 |
| `presentation/` | 預設輸出資料夾，轉換後的網頁簡報會放在這裡 |
| `notes_sample.md` | 講者備註與逐步提示範本 |

## 快速轉檔

如果要使用專案內的範例 PDF，請執行：

```powershell
python .\pdf_to_static.py --input-dir .\test-pdfs --output-dir .\presentation --dpi 144 --quality 80
```

執行成功後，畫面會顯示已轉換的 PDF 數量、投影片總頁數，以及輸出首頁的位置。

接著用瀏覽器開啟：

```text
.\presentation\index.html
```

首頁會列出所有轉換完成的 PDF。點選文件名稱後，即可進入該文件的簡報播放頁。

## 使用自己的 PDF

1. 建立一個資料夾，例如 `my-pdfs`。
2. 將要轉換的 PDF 放入該資料夾。
3. 執行轉檔命令：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs --output-dir .\presentation
```

程式會自動掃描 `my-pdfs` 以及其子資料夾中的所有 `.pdf` 檔案。

如果沒有指定 `--output-dir`，預設會輸出到 `presentation`：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs
```

## 使用 Windows 批次檔

Windows 使用者可以直接執行：

```powershell
.\run_convert.bat
```

批次檔預設會讀取：

```text
.\test-pdfs
```

並輸出到：

```text
.\presentation
```

若要轉換其他資料夾，可以把輸入資料夾路徑放在批次檔後面：

```powershell
.\run_convert.bat .\my-pdfs
```

如果你的 Python 安裝位置比較特殊，請先開啟 `run_convert.bat`，依照自己的環境調整設定。

## 轉檔參數

| 參數 | 是否必填 | 預設值 | 說明 |
| --- | --- | --- | --- |
| `--input-dir` | 是 | 無 | PDF 來源資料夾。程式會遞迴掃描其中所有 PDF |
| `--output-dir` | 否 | `presentation` | 轉換後的網頁、圖片與簡報資源輸出位置 |
| `--dpi` | 否 | `144` | 圖片解析度。數字越高越清楚，但檔案也越大 |
| `--quality` | 否 | `80` | WebP 圖片品質，範圍為 `0` 到 `100` |

一般使用建議保留預設值：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs
```

如果 PDF 中有很多細字，可以提高 DPI：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs --dpi 180
```

如果希望檔案較小，可以降低圖片品質：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs --quality 70
```

## 輸出結果

轉換完成後，輸出資料夾大致會像這樣：

```text
presentation\
  index.html
  文件名稱.html
  文件名稱\
    page-0001.webp
    page-0002.webp
    page-0003.webp
  vendor\
    reveal.js\
      dist\
        ...
```

請保留整個 `presentation` 資料夾。若只複製單一 HTML 檔，圖片與簡報功能可能無法正常顯示。

## 播放簡報

開啟 `presentation\index.html` 後，點選任一文件即可播放。

常用操作如下：

| 操作 | 功能 |
| --- | --- |
| 左右方向鍵 | 上一頁 / 下一頁 |
| 空白鍵 | 下一頁 |
| `F` | 切換瀏覽器全螢幕 |
| `Esc` | 進入或離開投影片總覽 |
| `S` | 顯示或隱藏同頁講者備註面板 |
| `R` | 重置總時間與本頁時間 |
| `B` | 切換黑畫面暫停 |
| 左上角月亮 / 太陽按鈕 | 切換日間或夜晚模式 |

## 加入講者備註與逐步提示

你可以在輸出資料夾中建立或編輯：

```text
presentation\notes.md
```

根目錄的 `notes_sample.md` 可作為範本。內容格式如下：

```markdown
| 文件 | 頁碼 | 逐步提示 1 | 逐步提示 2 | 講者備註 |
| --- | ---: | --- | --- | --- |
| AI在日常辦公與工作中的多元應用 | 1 | 封面 | 說明應用場景 | 開場介紹這份簡報的目的。 |
```

欄位說明：

| 欄位 | 說明 |
| --- | --- |
| `文件` | PDF 檔名，不含 `.pdf` |
| `頁碼` | PDF 頁碼，從 `1` 開始 |
| `逐步提示 1` | 第一個顯示在投影片上的提示 |
| `逐步提示 2` | 第二個顯示在投影片上的提示 |
| `講者備註` | 按 `S` 後在右側面板顯示的備註 |

注意事項：

- 修改 `presentation\notes.md` 後，需要重新執行轉檔，備註才會寫入簡報頁。
- 如果備註需要換行，請在文字中輸入 `\n`。
- 如果文字中需要直線符號，請寫成 `\|`。
- 沒有設定備註的頁面仍可正常播放，只是不會顯示備註內容。

## 常見問題

### 找不到 PDF

請確認 `--input-dir` 指向的資料夾存在，而且資料夾內至少有一個副檔名為 `.pdf` 的檔案。

### 顯示 `--dpi must be a positive integer`

`--dpi` 必須是大於 `0` 的整數，例如：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs --dpi 144
```

### 顯示 `--quality must be in range 0-100`

`--quality` 必須介於 `0` 到 `100` 之間。一般建議使用 `70` 到 `90`。

### 開啟 HTML 後沒有圖片

請確認沒有只複製單一 HTML 檔。簡報頁需要同資料夾中的圖片資料夾與 `vendor` 資源，建議完整保留或搬移整個 `presentation` 資料夾。

### 簡報檔案太大

可以降低圖片品質或 DPI，例如：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs --dpi 120 --quality 70
```

### 細字不夠清楚

可以提高 DPI，例如：

```powershell
python .\pdf_to_static.py --input-dir .\my-pdfs --dpi 180 --quality 85
```

## 使用提醒

- 不要把含有機密資料的 PDF 或轉換後的簡報資料夾提交到公開版本庫。
- 轉檔會產生許多圖片，請先確認磁碟空間足夠。
- 若重新轉換同一批 PDF，舊的同名圖片與 HTML 可能會被更新。
- `presentation\vendor` 內的 Reveal.js 檔案是離線播放所需資源，請不要刪除。
