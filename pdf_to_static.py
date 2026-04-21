from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium


@dataclass
class ConvertedPdf:
    title: str
    source_pdf: Path
    slug: str
    page_count: int
    page_html: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDFs in a directory into per-page WebP images and static HTML pages."
    )
    parser.add_argument("--input-dir", required=True, help="Input directory containing PDF files.")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for generated images and HTML (default: ./output).",
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


def build_pdf_page_html(title: str, image_dir_name: str, image_names: list[str]) -> str:
    safe_title = html.escape(title)
    image_tags = "\n".join(
        f'      <img loading="lazy" src="{html.escape(image_dir_name)}/{html.escape(name)}" alt="{safe_title} - Page {idx + 1}" />'
        for idx, name in enumerate(image_names)
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{safe_title}</title>
    <style>
      body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #f4f6f8;
        color: #1f2937;
      }}
      main {{
        max-width: 1100px;
        margin: 0 auto;
        padding: 24px 16px 36px;
      }}
      h1 {{
        font-size: 24px;
        margin: 0 0 16px;
      }}
      .pages {{
        display: flex;
        flex-direction: column;
        gap: 16px;
      }}
      img {{
        width: 100%;
        height: auto;
        background: #fff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
      }}
      .top-nav {{
        margin: 0 0 12px;
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="top-nav"><a href="index.html">← Back to index</a></div>
      <h1>{safe_title}</h1>
      <section class="pages">
{image_tags}
      </section>
    </main>
  </body>
</html>
"""


def build_index_html(items: list[ConvertedPdf]) -> str:
    rows = "\n".join(
        f'      <li><a href="{html.escape(item.page_html.name)}">{html.escape(item.title)}</a> <span>({item.page_count} pages)</span></li>'
        for item in items
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PDF Static Pages</title>
    <style>
      body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #f7f7f7;
        color: #1f2937;
      }}
      main {{
        max-width: 780px;
        margin: 32px auto;
        padding: 0 16px;
      }}
      h1 {{
        margin: 0 0 12px;
      }}
      ul {{
        padding-left: 20px;
      }}
      li {{
        margin: 8px 0;
      }}
      span {{
        color: #6b7280;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>PDF Static Pages</h1>
      <p>Generated documents:</p>
      <ul>
{rows}
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
    used_slugs: set[str] = set()
    converted: list[ConvertedPdf] = []

    for pdf_path in pdf_files:
        title = pdf_path.stem
        slug = unique_slug(slugify(title), used_slugs)
        image_dir = output_dir / slug
        image_names = render_pdf_to_webp(pdf_path, image_dir, args.dpi, args.quality)
        doc_html_path = output_dir / f"{slug}.html"
        doc_html_path.write_text(
            build_pdf_page_html(title=title, image_dir_name=slug, image_names=image_names),
            encoding="utf-8",
        )
        converted.append(
            ConvertedPdf(
                title=title,
                source_pdf=pdf_path,
                slug=slug,
                page_count=len(image_names),
                page_html=doc_html_path,
            )
        )

    index_html = output_dir / "index.html"
    index_html.write_text(build_index_html(converted), encoding="utf-8")
    print(f"Converted {len(converted)} PDF file(s).")
    print(f"Output: {index_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
