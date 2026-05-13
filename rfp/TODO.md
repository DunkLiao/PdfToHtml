# TODO.md

## 專案定位

- [ ] 現有 PDF 轉靜態 HTML 工具改為做 Reveal.js 簡報網頁。
- [ ] 建議新增目錄為 `presentation/`，簡報入口放在 `presentation/index.html`。
- [ ] `output/` 資料夾不再使用
- [ ] 保留現有 `pdf_to_static.py`、`test-pdfs/`資料夾
- [ ] `pdf_to_static.py`可視情況改寫
- [ ] 採用純 HTML、CSS、JavaScript 與本機端 Reveal.js ，不新增 Node.js、npm 或打包流程。

## Phase 1：建立基本簡報架構

- [ ] 原先 PDF 轉檔輸出目錄，改為'presentation/index.html'
- [ ] 轉檔圖片依照原先pdf格式對應網頁名稱
- [ ] 透過本機端 Reveal.js CSS 與 JavaScript。
- [ ] 建立 Reveal.js 必要 DOM 結構：`.reveal`、`.slides`、`section`。
- [ ] 建立至少 5 張商務展示風格的範例投影片，每頁即是一頁PDF轉圖片的結果，圖片格式為webp。
- [ ] 設定投影片比例為 16:9。
- [ ] 啟用鍵盤翻頁，確認左右方向鍵與空白鍵可切換頁面。
- [ ] 啟用頁碼顯示。
- [ ] 啟用進度條顯示。
- [ ] 啟用 `F` 全螢幕快捷鍵。
- [ ] 確認 `Esc` 可進入投影片總覽模式。

## Phase 2：加入互動與講者功能

- [ ] 在範例投影片中加入 Reveal.js `fragment` 逐步出現效果。
- [ ] 設定正式、穩定的頁面切換動畫。
- [ ] 加入至少 1 張含條列重點逐步出現的投影片。
- [ ] 加入至少 1 張含講者備註的投影片。
- [ ] 啟用 Reveal.js notes plugin。
- [ ] 測試 `S` 可開啟講者模式。
- [ ] 測試 `B` 可切換黑畫面暫停。

## Phase 3：建立品牌樣式

- [ ] 建立 `presentation/assets/css/custom.css`。
- [ ] 將自訂版面與品牌樣式集中到 `custom.css`。
- [ ] 建立 CSS 變數控制主色、輔色、背景色、文字色與字體。
- [ ] 設計乾淨、正式、適合商務簡報的預設樣式。
- [ ] 定義標題頁、章節頁、重點條列頁、圖文頁的基礎樣式。
- [ ] 確認非工程背景使用者只需修改 HTML `section` 內容即可新增投影片。

## Phase 4：支援正式展示素材

- [ ] 建立 `presentation/assets/images/` 放置圖片素材。
- [ ] 在範例中加入一般圖片插入方式。
- [ ] 在範例中加入背景圖片投影片寫法。
- [ ] 在範例中加入影片嵌入區塊。
- [ ] 在範例中加入 iframe 嵌入區塊。
- [ ] 建立簡易圖表或 KPI 區塊樣式。
- [ ] 在 README 或簡報註解中說明圖片放置與引用規則。

## Phase 5：文件與部署準備

- [ ] 更新根目錄 `README.md`，補充 `presentation/` 簡報專案用途與開啟方式。
- [ ] 在 `presentation/README.md` 或根目錄 README 中說明如何新增投影片。
- [ ] 說明 Reveal.js CDN 依賴需要網路連線；若要完全離線使用，需改成本地 vendored 檔案。
- [ ] 規劃 GitHub Pages 部署方式，優先使用 `presentation/` 作為靜態頁面來源。
- [ ] 確認桌機瀏覽器顯示正常。
- [ ] 確認手機瀏覽器可閱讀與操作。

## 驗收清單

- [ ] `presentation/index.html` 可直接用 Chrome 開啟。
- [ ] 不需要安裝 Node.js。
- [ ] 投影片可正常左右切換。
- [ ] 空白鍵可前進。
- [ ] `F` 可進入全螢幕。
- [ ] `Esc` 可進入總覽模式。
- [ ] `S` 可開啟講者模式。
- [ ] `B` 可切換黑畫面。
- [ ] 投影片比例為 16:9。
- [ ] 頁碼正常顯示。
- [ ] 進度條正常顯示。
- [ ] 至少包含 5 張範例投影片。
- [ ] 樣式正式、清楚、適合商務展示。
- [ ] 新增投影片不需要理解複雜 JavaScript。
- [ ] 現有 `pdf_to_static.py` PDF 轉 HTML 功能不受影響。

## 暫不處理項目

- [ ] Markdown 投影片先列為後續加分功能，不納入第一版必要範圍。
- [ ] 匯出 PDF 先列為後續加分功能，不納入第一版必要範圍。
- [ ] 主題切換與深色模式先列為後續加分功能。
- [ ] QR Code 分享與自動產生目錄頁先列為後續加分功能。
