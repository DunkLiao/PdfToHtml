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


def build_presentation_html(item: ConvertedPdf) -> str:
    sections: list[str] = []
    safe_title = html.escape(item.title)
    safe_slug = html.escape(item.slug)
    for idx, image_name in enumerate(item.image_names):
        safe_image = html.escape(image_name)
        page_number = idx + 1
        sections.append(
            f"""      <section data-document="{safe_slug}" data-page="{page_number}">
        <img src="{safe_slug}/{safe_image}" alt="{safe_title} - Page {page_number}" />
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

      .reveal .controls,
      .reveal .progress {{
        color: var(--primary);
      }}

      .reveal .slide-number {{
        background: rgb(23 32 51 / 82%);
      }}
    </style>
  </head>
  <body>
    <div class="reveal">
      <div class="slides">
{section_markup}
      </div>
    </div>

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
        transition: "slide"
      }});

      document.addEventListener("keydown", function (event) {{
        if (event.key.toLowerCase() !== "f") {{
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
        presentation_html.write_text(build_presentation_html(converted_pdf), encoding="utf-8")
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
