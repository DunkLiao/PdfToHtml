# TODO.md

## 專案定位

- [x] 現有 PDF 轉靜態 HTML 工具改為做 Reveal.js 簡報網頁。
- [x] 建議新增目錄為 `presentation/`，簡報入口放在 `presentation/index.html`。
- [x] `output/` 資料夾不再使用
- [x] 保留現有 `pdf_to_static.py`、`test-pdfs/`資料夾
- [x] `pdf_to_static.py`可視情況改寫
- [x] 採用純 HTML、CSS、JavaScript 與本機端 Reveal.js ，不新增 Node.js、npm 或打包流程。

## Phase 1：建立基本簡報架構

- [x] 原先 PDF 轉檔輸出目錄，改為'presentation/index.html'
- [x] 轉檔圖片依照原先pdf格式對應網頁名稱
- [x] 透過本機端 Reveal.js CSS 與 JavaScript。
- [x] 建立 Reveal.js 必要 DOM 結構：`.reveal`、`.slides`、`section`。
- [x] 建立至少 5 張商務展示風格的範例投影片，每頁即是一頁PDF轉圖片的結果，圖片格式為webp。
- [x] 設定投影片比例為 16:9。
- [x] 啟用鍵盤翻頁，確認左右方向鍵與空白鍵可切換頁面。
- [x] 啟用頁碼顯示。
- [x] 啟用進度條顯示。
- [x] 啟用 `F` 全螢幕快捷鍵。
- [x] 確認 `Esc` 可進入投影片總覽模式。

## Phase 2：加入互動與講者功能

- [x] 在範例投影片中加入 Reveal.js `fragment` 逐步出現效果。
- [x] 設定正式、穩定的頁面切換動畫。
- [x] 建立同頁講者備註面板。
- [x] 測試 `S` 可切換同頁講者備註面板。
- [x] 測試 `B` 可切換黑畫面暫停。
- [x] Phase 2 功能驗證成功。


## Phase 3：文件與部署準備

- [ ] 更新根目錄 `README.md`，補充 `presentation/` 簡報專案用途與開啟方式。
- [ ] 在 `presentation/README.md` 或根目錄 README 中說明如何新增投影片。
- [ ] 說明 Reveal.js 使用本地檔案。
- [ ] 規劃 GitHub Pages 部署方式，優先使用 `presentation/` 作為靜態頁面來源。
- [ ] 確認桌機瀏覽器顯示正常。
- [ ] 確認手機瀏覽器可閱讀與操作。

## 驗收清單

- [x] `presentation/index.html` 可直接用 Chrome 開啟。
- [x] 不需要安裝 Node.js。
- [x] 投影片可正常左右切換。
- [x] 空白鍵可前進。
- [x] `F` 可進入全螢幕。
- [x] `Esc` 可進入總覽模式。
- [x] `S` 可切換同頁講者備註面板。
- [x] `B` 可切換黑畫面。
- [x] 投影片比例為 16:9。
- [x] 頁碼正常顯示。
- [x] 進度條正常顯示。
- [x] 至少包含 5 張範例投影片。
- [x] 樣式正式、清楚、適合商務展示。
- [x] 新增投影片不需要理解複雜 JavaScript。

## 暫不處理項目

- [ ] Markdown 投影片先列為後續加分功能，不納入第一版必要範圍。
- [ ] 主題切換與深色模式先列為後續加分功能。
- [ ] QR Code 分享列為後續加分功能。
