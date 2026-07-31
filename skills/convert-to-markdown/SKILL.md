---
name: convert-to-markdown
description: >-
  Generate Markdown (.md) FILES from documents — PDF, Word, Excel, PowerPoint,
  images, HTML, CSV, EPUB and more — using Microsoft's MarkItDown, running
  locally so the documents' contents never enter context (minimal tokens). Use
  whenever the goal is to PRODUCE markdown files from documents: converting one
  file to .md, batch-converting a whole folder or many files at once, or building
  a .md corpus for a repo, docs site, or RAG pipeline. Trigger even without the
  words "MarkItDown" or "convert" — e.g. "get these PDFs as markdown files",
  "turn our Word docs into .md for Docusaurus", "I need .md versions of
  everything in this folder". Do NOT use it to read, summarize, extract data
  from, translate, or answer questions ABOUT a document (that needs the content
  in context — read it directly or use the built-in pdf/docx/xlsx skills), nor
  for the reverse direction (markdown → PDF/DOCX), merging PDFs, or extracting
  images.
---

# Convert to Markdown

Generate Markdown (`.md`) files from documents using
[MarkItDown](https://github.com/microsoft/markitdown). This skill exists for one
job: **producing `.md` files as deliverables**, cheaply. The conversion runs as
a local script, so the documents' contents never enter the model context — you
get back only the paths of the files created. This is what makes it far cheaper
than reading each document in when the user just wants Markdown out.

Use it for single files or whole folders. If instead the user wants you to
*understand, summarize, or answer questions about* a document, this skill is the
wrong tool — that inherently requires the content in context, so read the file
directly or use the built-in `pdf`/`docx`/`xlsx` skills.

## Setup (once per environment)

The script needs MarkItDown. Check and install if missing:

```bash
python -c "import markitdown" 2>/dev/null || pip install "markitdown[all]"
```

`markitdown[all]` pulls the parsers for every supported format. If `pip` is
restricted, `pip install --user "markitdown[all]"` usually works.

## Usage

Run the bundled script — it does the conversion and prints the path of each
`.md` it writes (nothing else, so the content stays out of context):

```bash
python scripts/convert.py INPUT [INPUT ...] [-o OUTPUT_DIR] [--stdout]
```

- **One file** → writes `report.md` next to `report.pdf`:
  ```bash
  python scripts/convert.py report.pdf
  ```
- **Many files / a folder** → collect them into one output directory:
  ```bash
  python scripts/convert.py docs/*.docx invoices/*.xlsx -o markdown_out/
  ```
- **Preview the Markdown** without writing a file (this DOES put content in
  context — only use it when the user explicitly wants to see the result):
  ```bash
  python scripts/convert.py summary.pptx --stdout
  ```

The path to `scripts/convert.py` is relative to this skill's directory; use the
absolute path when running from elsewhere.

## Behavior notes

- **Batch is the sweet spot.** Passing many files in one call converts them all
  in a single process — one command, N `.md` files, zero content loaded. Prefer
  this over converting one at a time.
- **Errors don't abort the batch.** A file that fails to parse is reported on
  stderr and the script moves on to the rest, exiting non-zero if any failed.
- **Output location.** Default is a `.md` beside each input; `-o` puts them all
  in one folder. The output filename is the input's stem + `.md`.
- **Report back concisely.** After running, tell the user how many files were
  created and where — don't paste the Markdown unless they asked to see it
  (pasting it defeats the token savings).

## Supported formats

PDF · DOCX · DOC · XLSX · XLS · CSV · PPTX · PPT · HTML · HTM · TXT · JSON ·
XML · EPUB · ZIP · PNG · JPG · JPEG · GIF · BMP · WEBP.

Scanned/image-only PDFs have no embedded text, so they convert to little or
nothing — those need OCR, which this skill does not perform. If a PDF comes back
nearly empty, tell the user it's likely scanned and would need OCR.
