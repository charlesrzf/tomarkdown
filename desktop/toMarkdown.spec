# PyInstaller spec — toMarkdown Desktop (janela nativa via pywebview).
# Build (onedir):  pyinstaller desktop/toMarkdown.spec
import os
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = []
binaries = []
hiddenimports = []

# Coleta código, dados e submódulos das bibliotecas com imports "preguiçosos"
# ou arquivos de dados (o MarkItDown carrega conversores dinamicamente).
for pkg in [
    "markitdown", "pdfminer", "openpyxl", "pptx", "mammoth",
    "markdownify", "bs4", "charset_normalizer", "olefile", "defusedxml",
    "puremagic", "et_xmlfile",
]:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# O frontend (HTML/CSS/JS) precisa ir junto e ser resolvido em runtime.
datas += [(os.path.join(ROOT, "frontend"), "frontend")]

a = Analysis(
    [os.path.join(SPECPATH, "desktop_app.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + ["backend", "backend.app"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="toMarkdown",
    debug=False,
    strip=False,
    upx=False,
    console=False,             # janela nativa, sem console
    icon=os.path.join(ROOT, "frontend", "icon.ico") if os.path.exists(os.path.join(ROOT, "frontend", "icon.ico")) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="toMarkdown",
)
