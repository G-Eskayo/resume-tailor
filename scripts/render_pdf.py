#!/usr/bin/env python3
"""
render_pdf.py — convert a Markdown resume/cover letter to PDF via WeasyPrint.
Usage: python render_pdf.py <input.md> <output.pdf> [--cover-letter]
Exits non-zero on error.
"""
import os
import sys
import re
from pathlib import Path

# WeasyPrint needs GLib/Pango from Homebrew on macOS.
# Re-exec with the lib path set if not already present.
if sys.platform == "darwin" and "DYLD_LIBRARY_PATH" not in os.environ:
    os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
    os.execv(sys.executable, [sys.executable] + sys.argv)

SKILL_DIR = Path(__file__).parent.parent
CSS_PATH = SKILL_DIR / "template" / "resume.css"


def md_to_html(md_text: str, cover_letter: bool = False) -> str:
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        print("ERROR: missing dependency. Run: ~/.agents/venv/bin/pip install markdown-it-py", file=sys.stderr)
        sys.exit(2)

    md = MarkdownIt()
    body_html = md.render(md_text)

    # Post-process: wrap the first <p> after the h1 as summary, mark h2 sections
    body_html = _annotate_sections(body_html)

    body_class = ' class="cover-letter"' if cover_letter else ""
    css_uri = CSS_PATH.as_uri()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="{css_uri}">
</head>
<body{body_class}>
{body_html}
</body>
</html>"""


def _annotate_sections(html: str) -> str:
    """Wrap structural elements in CSS-hookable classes."""
    # h1 → name
    html = re.sub(r"<h1>(.*?)</h1>", r'<p class="name">\1</p>', html, flags=re.DOTALL)
    # The title line is the first <p> class="em" or first <p> right after name — handled by CSS cascade
    return html


def render(input_md: str, output_pdf: str, cover_letter: bool = False) -> None:
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        print(
            "ERROR: WeasyPrint not installed.\n"
            "Run: ~/.agents/venv/bin/pip install weasyprint",
            file=sys.stderr,
        )
        sys.exit(2)

    src = Path(input_md).expanduser().resolve()
    dst = Path(output_pdf).expanduser().resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    md_text = src.read_text(encoding="utf-8")
    html_str = md_to_html(md_text, cover_letter=cover_letter)

    font_config = FontConfiguration()
    html_obj = HTML(string=html_str, base_url=str(SKILL_DIR))
    css_obj = CSS(filename=str(CSS_PATH), font_config=font_config)

    html_obj.write_pdf(str(dst), stylesheets=[css_obj], font_config=font_config)
    print(f"PDF written: {dst}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: render_pdf.py <input.md> <output.pdf> [--cover-letter]", file=sys.stderr)
        sys.exit(2)
    input_md, output_pdf = args[0], args[1]
    is_cover = "--cover-letter" in args
    render(input_md, output_pdf, cover_letter=is_cover)
