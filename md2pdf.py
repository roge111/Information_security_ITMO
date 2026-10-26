# -*- coding: utf-8 -*-
"""Конвертация Markdown -> PDF через HTML + Chrome headless."""
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from urllib.request import pathname2url

import markdown

BASE_DIR = Path(__file__).resolve().parent
MD_PATH = BASE_DIR / "README.md"
HTML_PATH = BASE_DIR / "README.html"
PDF_PATH = BASE_DIR / "README.pdf"

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 11pt;
    line-height: 1.45;
    color: #1a1a1a;
    margin: 0;
}
h1, h2, h3, h4 { font-family: "Segoe UI", "Arial", sans-serif; color: #0b3d91; page-break-after: avoid; }
h1 { font-size: 20pt; border-bottom: 2px solid #0b3d91; padding-bottom: 6px; }
h2 { font-size: 16pt; border-bottom: 1px solid #c0c4cc; padding-bottom: 4px; margin-top: 22px; }
h3 { font-size: 13pt; margin-top: 18px; }
h4 { font-size: 11.5pt; }
p { margin: 8px 0; }
ul, ol { margin: 6px 0 10px 0; }
li { margin: 3px 0; }
code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9.5pt;
    background: #f0f2f5;
    padding: 1px 4px;
    border-radius: 3px;
    color: #a31515;
}
pre {
    background: #f6f8fa;
    border: 1px solid #d8dee4;
    border-radius: 5px;
    padding: 10px 12px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9pt;
    line-height: 1.35;
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid;
}
pre code { background: none; padding: 0; color: inherit; font-size: inherit; }
blockquote {
    border-left: 4px solid #0b3d91;
    margin: 10px 0;
    padding: 6px 14px;
    background: #f2f6ff;
    color: #333;
}
table { border-collapse: collapse; margin: 10px 0; width: 100%; }
th, td { border: 1px solid #b6bcc4; padding: 5px 9px; font-size: 10pt; }
th { background: #e8edf5; }
hr { border: none; border-top: 1px solid #c0c4cc; margin: 16px 0; }
strong { color: #000; }
"""


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    sys.exit("Chrome/Edge не найден")


def main():
    md_text = MD_PATH.read_text(encoding="utf-8")

    html_body = markdown.markdown(
        md_text,
        extensions=[
            "fenced_code",
            "tables",
            "sane_lists",
            "attr_list",
            "md_in_html",
        ],
        output_format="html5",
    )

    html_full = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>README</title>
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    HTML_PATH.write_text(html_full, encoding="utf-8")
    print(f"HTML сохранён: {HTML_PATH}")

    chrome = find_chrome()
    file_url = urllib.parse.urljoin("file:///", pathname2url(str(HTML_PATH)))

    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--print-to-pdf=" + str(PDF_PATH),
        "--virtual-time-budget=10000",
        file_url,
    ]
    print("Запуск:", " ".join(cmd))
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
    )
    if result.stdout:
        print("STDOUT:", result.stdout[:500])
    if result.stderr:
        print("STDERR:", result.stderr[:500])

    if PDF_PATH.exists() and PDF_PATH.stat().st_size > 0:
        print(f"PDF создан: {PDF_PATH} ({PDF_PATH.stat().st_size} байт)")
    else:
        sys.exit("Ошибка: PDF не был создан")


if __name__ == "__main__":
    main()