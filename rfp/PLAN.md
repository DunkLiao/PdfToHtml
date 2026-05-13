# PLAN.md

## 專案目標

建立一套「HTML 翻頁式簡報」系統，效果接近 PowerPoint，可在瀏覽器中展示、翻頁、全螢幕播放，並支援後續快速新增投影片內容。

優先完成可用版本，再逐步優化版型、動畫與部署流程。

---

## 技術選型

- 前端：HTML、CSS、JavaScript
- 簡報框架：Reveal.js
- 執行方式：瀏覽器直接開啟 `index.html`
- 全部都能在本地端執行
- 可選部署：
  - GitHub Pages
  - Cloudflare Pages
  - Netlify
  - Vercel
---

## 開發階段

## Phase 1：建立基本簡報架構

目標：完成可翻頁、可全螢幕展示的 HTML 簡報。

任務：

- 建立 `index.html`
- 引入 Reveal.js CDN
- 建立基本投影片結構
- 啟用方向鍵翻頁
- 啟用頁碼
- 啟用進度條
- 啟用全螢幕展示

完成標準：

- 可以用 Chrome 開啟簡報內容頁
- 可以用左右方向鍵切換頁面
- 可以按 `F` 進入全螢幕
- 可以按 `Esc` 進入總覽模式

---

## Phase 2：加入簡報互動效果

目標：讓簡報更像 PowerPoint 展示。

任務：

- 加入逐步出現效果
- 使用 Reveal.js `fragment`
- 設定頁面切換動畫
- 加入簡報頁碼
- 加入進度條
- 加入講者備註
- 測試講者模式

範例：

```html
<p class="fragment">第一個重點</p>
<p class="fragment">第二個重點</p>
<p class="fragment">第三個重點</p>
```
---

## Phase 3：加入品牌樣式

目標：可依不同單位或企業修改品牌風格。

任務：

- 將樣式集中到 `assets/css/custom.css`
- 建立 CSS 變數
- 使用變數控制主色、輔色、背景色、字體

範例：

```css
:root {
  --primary-color: #005BAC;
  --secondary-color: #D9A441;
  --background-color: #FFFFFF;
  --text-color: #222222;
}
```

---

## Phase 4：支援圖片、圖表與影片

目標：讓簡報支援正式展示所需素材。

任務：

- 支援圖片插入
- 支援背景圖片
- 支援影片嵌入
- 支援 iframe
- 支援圖表區塊
- 建立圖片放置規則

圖片目錄：

```text
assets/images/
```

---

## Phase 5：部署成線上簡報

目標：讓簡報可以透過網址分享。

任務：

- 上傳所有檔案
- 啟用 GitHub Pages
- 測試線上網址
- 確認手機與桌機都可以觀看

可選部署平台：

- GitHub Pages
- Cloudflare Pages
- Netlify
- Vercel

---

## 功能需求

## 必要功能

- 可翻頁
- 可全螢幕
- 可顯示頁碼
- 可顯示進度條
- 可用鍵盤操作
- 可支援 16:9 投影片
- 可自訂樣式
- 可加入動畫
- 可加入圖片

## 加分功能

- 講者模式
- Markdown 投影片
- 匯出 PDF
- 主題切換
- 深色模式
- QR Code 分享
- 自動產生目錄頁

---

## 使用者操作方式

| 操作 | 功能 |
|---|---|
| 右方向鍵 | 下一頁 |
| 左方向鍵 | 上一頁 |
| 空白鍵 | 下一頁 |
| Esc | 投影片總覽 |
| F | 全螢幕 |
| S | 講者模式 |
| B | 黑畫面暫停 |

---

## 驗收標準

完成後必須符合：

- `index.html` 可直接用瀏覽器開啟
- 投影片可正常左右切換
- 全螢幕功能可使用
- 投影片比例為 16:9
- 頁碼與進度條正常顯示
- 至少包含 5 張範例投影片
- 樣式乾淨、正式、適合商務展示
- 程式碼容易修改
- 新增投影片不需要理解複雜 JavaScript

---

## AI Coding Agent 指令

請依照本 `PLAN.md` 建立一個 Reveal.js HTML 翻頁式簡報專案。

優先完成：

1. `index.html`
2. `assets/css/custom.css`
3. `README.md`

請確保專案可以直接用瀏覽器開啟，不需要安裝 Node.js。

除非必要，不要使用複雜框架。

程式碼需保持簡潔、可維護、容易讓非工程背景使用者修改。
