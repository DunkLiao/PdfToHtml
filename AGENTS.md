# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python utility that converts PDFs into static HTML pages backed by per-page WebP images.

- `pdf_to_static.py` contains the CLI, PDF rendering, slug generation, and HTML generation logic.
- `requirements.txt` pins runtime dependencies: `pypdfium2` and `Pillow`.
- `test-pdfs/` stores sample input PDFs for local verification.
- `output/` contains generated HTML and WebP assets. Treat it as build output.
- `run_convert.bat` is a Windows convenience wrapper with local path defaults.
- `rfp/` contains planning notes, outside the runtime path.

## Build, Test, and Development Commands

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the converter against bundled samples:

```powershell
python .\pdf_to_static.py --input-dir .\test-pdfs --output-dir .\output --dpi 144 --quality 80
```

Use the Windows wrapper when its paths match your environment:

```powershell
.\run_convert.bat
```

Open `output\index.html` in a browser to inspect the generated site.

## Coding Style & Naming Conventions

Use Python 3.10+ style with 4-space indentation, type hints for public helpers, and `pathlib.Path` for filesystem work. Keep functions focused: argument parsing, validation, rendering, and HTML generation should remain separated. Use `snake_case` for functions and variables, `PascalCase` for dataclasses, and clear CLI names such as `--input-dir`.

Generated filenames should stay stable and URL-safe: document folders use slugified PDF stems, and page images use `page-0001.webp` numbering.

## Testing Guidelines

There is no formal test suite yet. For changes, run the sample conversion command and verify:

- the command exits successfully;
- `output\index.html` links to every converted PDF page;
- each generated document HTML displays all expected `page-*.webp` images;
- invalid inputs still raise clear errors, especially bad directories, `--dpi <= 0`, and `--quality` outside `0-100`.

If adding automated tests, prefer `pytest` under a new `tests/` directory and name files `test_*.py`.

## Commit & Pull Request Guidelines

The Git history only contains `Initial commit`, so no detailed convention exists yet. Use short, imperative commit subjects such as `Add PDF validation tests` or `Improve generated index styling`.

Pull requests should include a summary, the conversion command used for verification, and screenshots or sample output notes when generated HTML changes. Link related issues when available and call out dependency or output-format changes.

## Security & Configuration Tips

Do not commit private PDFs or sensitive generated output. Review `run_convert.bat` before sharing because it may contain machine-specific absolute paths. Keep dependency updates deliberate and test rendered output after changing `pypdfium2` or `Pillow`.
