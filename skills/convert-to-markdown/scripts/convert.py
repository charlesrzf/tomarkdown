#!/usr/bin/env python3
"""
Converte documentos para Markdown usando o MarkItDown (Microsoft).

Uso:
    python convert.py ARQUIVO [ARQUIVO ...] [-o PASTA_SAIDA] [--stdout]

Exemplos:
    python convert.py relatorio.pdf
    python convert.py *.docx -o convertidos/
    python convert.py planilha.xlsx --stdout

Formatos: PDF, DOCX, XLSX, PPTX, HTML, CSV, TXT, JSON, XML, EPUB, ZIP e
imagens (PNG/JPG/...). Sem argumento --stdout, grava um arquivo .md ao lado
de cada entrada (ou na pasta de saída) e imprime o caminho gerado.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Converte documentos para Markdown via MarkItDown.")
    ap.add_argument("inputs", nargs="+", help="Arquivo(s) de entrada a converter.")
    ap.add_argument("-o", "--output-dir", help="Pasta de saída dos .md (padrão: ao lado de cada entrada).")
    ap.add_argument("--stdout", action="store_true", help="Imprime o Markdown na saída padrão em vez de gravar arquivos.")
    args = ap.parse_args()

    try:
        from markitdown import MarkItDown
    except ImportError:
        print("MarkItDown não instalado. Rode:  pip install 'markitdown[all]'", file=sys.stderr)
        return 2

    converter = MarkItDown()
    out_dir = Path(args.output_dir) if args.output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    had_error = False
    for raw in args.inputs:
        path = Path(raw)
        if not path.exists():
            print(f"[pulado] não encontrado: {path}", file=sys.stderr)
            had_error = True
            continue
        try:
            text = (converter.convert(str(path)).text_content or "").strip()
        except Exception as exc:  # noqa: BLE001 — reporta e segue para os demais
            print(f"[erro] {path}: {exc}", file=sys.stderr)
            had_error = True
            continue

        if args.stdout:
            if len(args.inputs) > 1:
                print(f"\n<!-- {path.name} -->")
            print(text)
        else:
            dest = (out_dir or path.parent) / f"{path.stem}.md"
            dest.write_text(text, encoding="utf-8")
            print(str(dest))

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
