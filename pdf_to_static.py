from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium


REVEAL_ASSETS = (
    Path("reset.css"),
    Path("reveal.css"),
    Path("reveal.js"),
    Path("theme") / "white.css",
)


@dataclass
class ConvertedPdf:
    title: str
    source_pdf: Path
    slug: str
    page_count: int
    presentation_html: Path
    image_names: list[str]


@dataclass
class SlideNotes:
    fragment_1: str = ""
    fragment_2: str = ""
    speaker_notes: str = ""

    @property
    def fragments(self) -> list[str]:
        return [value for value in (self.fragment_1, self.fragment_2) if value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDFs in a directory into a Reveal.js presentation backed by WebP images."
    )
    parser.add_argument("--input-dir", required=True, help="Input directory containing PDF files.")
    parser.add_argument(
        "--output-dir",
        default="presentation",
        help="Output directory for generated images and the Reveal.js presentation (default: ./presentation).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=144,
        help="Render DPI for each page image (default: 144).",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=80,
        help="WebP quality 0-100 (default: 80).",
    )
    return parser.parse_args()


def slugify(name: str) -> str:
    value = re.sub(r"[^\w\-]+", "-", name.strip().lower())
    value = re.sub(r"-{2,}", "-", value).strip("-_")
    return value or "document"


def unique_slug(base_slug: str, used: set[str]) -> str:
    if base_slug not in used:
        used.add(base_slug)
        return base_slug
    idx = 2
    while f"{base_slug}-{idx}" in used:
        idx += 1
    slug = f"{base_slug}-{idx}"
    used.add(slug)
    return slug


def render_pdf_to_webp(pdf_path: Path, image_dir: Path, dpi: int, quality: int) -> list[str]:
    image_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    image_names: list[str] = []
    scale = dpi / 72.0

    for page_idx in range(len(pdf)):
        page = pdf[page_idx]
        image = page.render(scale=scale).to_pil()
        image_name = f"page-{page_idx + 1:04d}.webp"
        image_path = image_dir / image_name
        image.save(str(image_path), format="WEBP", quality=quality)
        image_names.append(image_name)

    pdf.close()
    return image_names


def ensure_reveal_assets(output_dir: Path) -> None:
    project_dir = Path(__file__).resolve().parent
    source_dir = project_dir / "presentation" / "vendor" / "reveal.js" / "dist"
    destination_dir = output_dir / "vendor" / "reveal.js" / "dist"

    if source_dir == destination_dir:
        return
    if not source_dir.exists():
        raise RuntimeError(f"Reveal.js assets were not found: {source_dir}")

    for asset in REVEAL_ASSETS:
        source = source_dir / asset
        destination = destination_dir / asset
        if not source.exists():
            raise RuntimeError(f"Reveal.js asset was not found: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def split_markdown_table_row(row: str) -> list[str]:
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in row:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def is_markdown_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def load_slide_notes(notes_path: Path) -> dict[tuple[str, int], SlideNotes]:
    if not notes_path.exists():
        return {}

    rows = [
        split_markdown_table_row(line)
        for line in notes_path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|")
    ]
    if len(rows) < 2:
        return {}

    header_index = next((idx for idx, row in enumerate(rows[:-1]) if is_markdown_separator(rows[idx + 1])), None)
    if header_index is None:
        return {}

    headers = rows[header_index]
    records = rows[header_index + 2 :]
    header_map = {name: idx for idx, name in enumerate(headers)}
    required_headers = ("文件", "頁碼")
    missing_headers = [name for name in required_headers if name not in header_map]
    if missing_headers:
        missing = ", ".join(missing_headers)
        raise ValueError(f"{notes_path} is missing required column(s): {missing}")

    def get_cell(row: list[str], name: str) -> str:
        idx = header_map.get(name)
        if idx is None or idx >= len(row):
            return ""
        return row[idx].replace(r"\n", "\n").strip()

    notes: dict[tuple[str, int], SlideNotes] = {}
    for row in records:
        document = get_cell(row, "文件")
        page_value = get_cell(row, "頁碼")
        if not document and not page_value:
            continue
        try:
            page_number = int(page_value)
        except ValueError as exc:
            raise ValueError(f"{notes_path} has an invalid page number: {page_value}") from exc
        notes[(document, page_number)] = SlideNotes(
            fragment_1=get_cell(row, "逐步提示 1"),
            fragment_2=get_cell(row, "逐步提示 2"),
            speaker_notes=get_cell(row, "講者備註"),
        )
    return notes


def build_fragment_markup(fragments: list[str]) -> str:
    if not fragments:
        return ""

    fragment_items = "\n".join(
        f'          <span class="fragment fade-up">{html.escape(fragment)}</span>'
        for fragment in fragments
    )
    return f"""        <div class="slide-fragments" aria-label="逐步提示">
{fragment_items}
        </div>
"""


def build_notes_markup(notes: str) -> str:
    safe_notes = html.escape(notes).replace("\n", "<br />\n")
    return f"""        <aside class="notes">{safe_notes}</aside>"""


def build_presentation_html(item: ConvertedPdf, slide_notes: dict[tuple[str, int], SlideNotes]) -> str:
    sections: list[str] = []
    safe_title = html.escape(item.title)
    safe_slug = html.escape(item.slug)
    for idx, image_name in enumerate(item.image_names):
        safe_image = html.escape(image_name)
        page_number = idx + 1
        configured_notes = slide_notes.get((item.title, page_number))
        fragments = configured_notes.fragments if configured_notes is not None else []
        speaker_notes = configured_notes.speaker_notes if configured_notes is not None else ""
        fragment_markup = build_fragment_markup(fragments)
        notes_markup = build_notes_markup(speaker_notes)
        sections.append(
            f"""      <section data-document="{safe_slug}" data-page="{page_number}">
        <img src="{safe_slug}/{safe_image}" alt="{safe_title} - Page {page_number}" />
{fragment_markup}{notes_markup}
      </section>"""
        )

    section_markup = "\n\n".join(sections)
    return f"""<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{safe_title}</title>
    <link rel="stylesheet" href="vendor/reveal.js/dist/reset.css" />
    <link rel="stylesheet" href="vendor/reveal.js/dist/reveal.css" />
    <link rel="stylesheet" href="vendor/reveal.js/dist/theme/white.css" />
    <style>
      :root {{
        --stage-bg: #eef2f7;
        --slide-bg: #ffffff;
        --ink: #172033;
        --primary: #0b5cab;
        --notes-panel-width: 360px;
      }}

      body {{
        margin: 0;
        background: var(--stage-bg);
      }}

      .reveal {{
        color: var(--ink);
        font-family: Arial, "Microsoft JhengHei", sans-serif;
      }}

      .reveal .slides {{
        text-align: center;
      }}

      .reveal section {{
        align-items: center;
        background: var(--slide-bg);
        box-sizing: border-box;
        display: flex !important;
        justify-content: center;
        padding: 0;
        position: relative;
      }}

      .reveal section img {{
        border: 0;
        box-shadow: none;
        display: block;
        margin: 0;
        max-height: 100%;
        max-width: 100%;
        object-fit: contain;
      }}

      .reveal .slide-fragments {{
        bottom: 28px;
        display: flex;
        gap: 10px;
        justify-content: flex-end;
        left: 32px;
        pointer-events: none;
        position: absolute;
        right: 32px;
        z-index: 2;
      }}

      .reveal .slide-fragments span {{
        background: rgb(23 32 51 / 78%);
        border-radius: 4px;
        color: #ffffff;
        font-size: 18px;
        line-height: 1.35;
        padding: 8px 12px;
      }}

      .reveal .controls,
      .reveal .progress {{
        color: var(--primary);
      }}

      .reveal .slide-number {{
        background: rgb(23 32 51 / 82%);
      }}

      .notes-panel {{
        background: #ffffff;
        border-left: 1px solid #d8e0ea;
        bottom: 0;
        box-shadow: -10px 0 24px rgb(23 32 51 / 10%);
        box-sizing: border-box;
        color: var(--ink);
        display: flex;
        flex-direction: column;
        font-family: Arial, "Microsoft JhengHei", sans-serif;
        padding: 18px 20px;
        position: fixed;
        right: 0;
        top: 0;
        transform: translateX(100%);
        transition: transform 180ms ease;
        width: var(--notes-panel-width);
        z-index: 40;
      }}

      body.show-inline-notes .notes-panel {{
        transform: translateX(0);
      }}

      body.show-inline-notes .reveal {{
        width: calc(100% - var(--notes-panel-width));
      }}

      .notes-panel__header {{
        align-items: center;
        border-bottom: 1px solid #d8e0ea;
        display: flex;
        gap: 12px;
        justify-content: space-between;
        margin-bottom: 16px;
        padding-bottom: 12px;
      }}

      .notes-panel__title {{
        font-size: 16px;
        font-weight: 700;
      }}

      .notes-panel__close {{
        background: #eef2f7;
        border: 0;
        border-radius: 4px;
        color: var(--ink);
        cursor: pointer;
        font-size: 18px;
        height: 32px;
        line-height: 1;
        width: 32px;
      }}

      .notes-panel__timers {{
        border-bottom: 1px solid #d8e0ea;
        display: grid;
        gap: 8px;
        grid-template-columns: repeat(3, 1fr);
        margin-bottom: 16px;
        padding-bottom: 14px;
      }}

      .notes-panel__timer {{
        min-width: 0;
      }}

      .notes-panel__timer-label {{
        color: #5f6b7a;
        font-size: 12px;
        margin-bottom: 4px;
      }}

      .notes-panel__timer-value {{
        color: var(--ink);
        font-size: 18px;
        font-variant-numeric: tabular-nums;
        font-weight: 700;
        line-height: 1.2;
      }}

      .notes-panel__meta {{
        color: #5f6b7a;
        font-size: 13px;
        margin-bottom: 12px;
      }}

      .notes-panel__content {{
        font-size: 20px;
        line-height: 1.55;
        overflow: auto;
        white-space: normal;
      }}

      .notes-panel__empty {{
        color: #7a8594;
        font-style: italic;
      }}

      @media (max-width: 900px) {{
        .notes-panel {{
          border-left: 0;
          border-top: 1px solid #d8e0ea;
          height: 34vh;
          top: auto;
          transform: translateY(100%);
          width: 100%;
        }}

        body.show-inline-notes .notes-panel {{
          transform: translateY(0);
        }}

        body.show-inline-notes .reveal {{
          height: 66vh;
          width: 100%;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="reveal">
      <div class="slides">
{section_markup}
      </div>
    </div>

    <aside class="notes-panel" aria-label="講者備註" aria-hidden="true">
      <div class="notes-panel__header">
        <div class="notes-panel__title">講者備註</div>
        <button class="notes-panel__close" type="button" aria-label="關閉講者備註">×</button>
      </div>
      <div class="notes-panel__timers" aria-label="簡報計時器">
        <div class="notes-panel__timer">
          <div class="notes-panel__timer-label">總時間</div>
          <div class="notes-panel__timer-value" data-timer="total">00:00:00</div>
        </div>
        <div class="notes-panel__timer">
          <div class="notes-panel__timer-label">本頁</div>
          <div class="notes-panel__timer-value" data-timer="slide">00:00:00</div>
        </div>
        <div class="notes-panel__timer">
          <div class="notes-panel__timer-label">現在</div>
          <div class="notes-panel__timer-value" data-timer="clock">--:--</div>
        </div>
      </div>
      <div class="notes-panel__meta"></div>
      <div class="notes-panel__content"></div>
    </aside>

    <script src="vendor/reveal.js/dist/reveal.js"></script>
    <script>
      Reveal.initialize({{
        width: 1280,
        height: 720,
        controls: true,
        progress: true,
        slideNumber: true,
        keyboard: true,
        overview: true,
        transition: "fade",
        transitionSpeed: "default"
      }});

      const notesPanel = document.querySelector(".notes-panel");
      const notesMeta = document.querySelector(".notes-panel__meta");
      const notesContent = document.querySelector(".notes-panel__content");
      const notesClose = document.querySelector(".notes-panel__close");
      const totalTimer = document.querySelector('[data-timer="total"]');
      const slideTimer = document.querySelector('[data-timer="slide"]');
      const clockTimer = document.querySelector('[data-timer="clock"]');
      let presentationStartedAt = Date.now();
      let slideStartedAt = Date.now();

      function formatDuration(ms) {{
        const totalSeconds = Math.max(0, Math.floor(ms / 1000));
        const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
        const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
        const seconds = String(totalSeconds % 60).padStart(2, "0");
        return hours + ":" + minutes + ":" + seconds;
      }}

      function formatClock(date) {{
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        return hours + ":" + minutes;
      }}

      function updateTimers() {{
        const now = Date.now();
        totalTimer.textContent = formatDuration(now - presentationStartedAt);
        slideTimer.textContent = formatDuration(now - slideStartedAt);
        clockTimer.textContent = formatClock(new Date(now));
      }}

      function resetTimers() {{
        presentationStartedAt = Date.now();
        slideStartedAt = presentationStartedAt;
        updateTimers();
      }}

      function syncInlineNotes() {{
        const slide = Reveal.getCurrentSlide();
        const notes = slide ? slide.querySelector("aside.notes") : null;
        const documentName = slide ? slide.getAttribute("data-document") : "";
        const pageNumber = slide ? slide.getAttribute("data-page") : "";
        const content = notes ? notes.innerHTML.trim() : "";

        notesMeta.textContent = documentName && pageNumber
          ? documentName + " / 第 " + pageNumber + " 頁"
          : "";
        notesContent.innerHTML = content || '<span class="notes-panel__empty">此頁尚未設定講者備註。</span>';
      }}

      function setInlineNotes(open) {{
        document.body.classList.toggle("show-inline-notes", open);
        notesPanel.setAttribute("aria-hidden", open ? "false" : "true");
        if (open) {{
          syncInlineNotes();
          Reveal.layout();
        }} else {{
          Reveal.layout();
        }}
      }}

      notesClose.addEventListener("click", function () {{
        setInlineNotes(false);
      }});

      Reveal.on("slidechanged", syncInlineNotes);
      Reveal.on("slidechanged", function () {{
        slideStartedAt = Date.now();
        updateTimers();
      }});
      Reveal.on("fragmentshown", syncInlineNotes);
      Reveal.on("fragmenthidden", syncInlineNotes);
      updateTimers();
      window.setInterval(updateTimers, 1000);

      document.addEventListener("keydown", function (event) {{
        const key = event.key.toLowerCase();

        if (key === "s") {{
          event.preventDefault();
          setInlineNotes(!document.body.classList.contains("show-inline-notes"));
          return;
        }}

        if (key === "r") {{
          event.preventDefault();
          resetTimers();
          return;
        }}

        if (key !== "f") {{
          return;
        }}

        if (!document.fullscreenElement) {{
          document.documentElement.requestFullscreen();
          return;
        }}

        document.exitFullscreen();
      }});
    </script>
  </body>
</html>
"""


def build_index_html(items: list[ConvertedPdf]) -> str:
    links = "\n".join(
        f"""        <li>
          <a href="{html.escape(item.presentation_html.name)}">{html.escape(item.title)}</a>
          <span>{item.page_count} slides</span>
        </li>"""
        for item in items
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PDF Presentations</title>
    <style>
      :root {{
        --bg: #eef2f7;
        --surface: #ffffff;
        --ink: #172033;
        --muted: #5f6b7a;
        --primary: #0b5cab;
        --line: #d8e0ea;
      }}

      body {{
        background: var(--bg);
        color: var(--ink);
        font-family: Arial, "Microsoft JhengHei", sans-serif;
        margin: 0;
      }}

      main {{
        box-sizing: border-box;
        margin: 0 auto;
        max-width: 880px;
        padding: 48px 20px;
      }}

      h1 {{
        font-size: 32px;
        letter-spacing: 0;
        line-height: 1.2;
        margin: 0 0 10px;
      }}

      p {{
        color: var(--muted);
        font-size: 16px;
        line-height: 1.6;
        margin: 0 0 28px;
      }}

      ul {{
        display: grid;
        gap: 12px;
        list-style: none;
        margin: 0;
        padding: 0;
      }}

      li {{
        align-items: center;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        display: flex;
        gap: 16px;
        justify-content: space-between;
        padding: 18px 20px;
      }}

      a {{
        color: var(--primary);
        font-size: 18px;
        font-weight: 700;
        text-decoration: none;
      }}

      a:hover {{
        text-decoration: underline;
      }}

      span {{
        color: var(--muted);
        flex: 0 0 auto;
        font-size: 14px;
      }}

      @media (max-width: 560px) {{
        li {{
          align-items: flex-start;
          flex-direction: column;
          gap: 6px;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>PDF Presentations</h1>
      <p>選擇一份文件開始播放投影片。</p>
      <ul>
{links}
      </ul>
    </main>
  </body>
</html>
"""


def validate_args(input_dir: Path, dpi: int, quality: int) -> None:
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist or is not a directory: {input_dir}")
    if dpi <= 0:
        raise ValueError("--dpi must be a positive integer.")
    if quality < 0 or quality > 100:
        raise ValueError("--quality must be in range 0-100.")


def run() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    validate_args(input_dir, args.dpi, args.quality)

    pdf_files = sorted(input_dir.rglob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDF files found in input directory: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_reveal_assets(output_dir)
    notes_path = output_dir / "notes.md"
    slide_notes = load_slide_notes(notes_path)
    used_slugs: set[str] = set()
    converted: list[ConvertedPdf] = []

    for pdf_path in pdf_files:
        title = pdf_path.stem
        slug = unique_slug(slugify(title), used_slugs)
        image_dir = output_dir / slug
        image_names = render_pdf_to_webp(pdf_path, image_dir, args.dpi, args.quality)
        presentation_html = output_dir / f"{slug}.html"
        converted_pdf = ConvertedPdf(
            title=title,
            source_pdf=pdf_path,
            slug=slug,
            page_count=len(image_names),
            presentation_html=presentation_html,
            image_names=image_names,
        )
        presentation_html.write_text(build_presentation_html(converted_pdf, slide_notes), encoding="utf-8")
        converted.append(
            converted_pdf
        )

    index_html = output_dir / "index.html"
    index_html.write_text(build_index_html(converted), encoding="utf-8")
    total_slides = sum(item.page_count for item in converted)
    print(f"Converted {len(converted)} PDF file(s).")
    print(f"Generated {total_slides} slide(s).")
    if total_slides < 5:
        print("Warning: Phase 1 sample target is at least 5 slides, but the input PDFs produced fewer.")
    print(f"Output: {index_html}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
