"""
toMarkdown — backend FastAPI que converte PDF, DOCX, XLSX, PPTX, imagens e HTML
para Markdown usando a biblioteca MarkItDown (Microsoft).

Serve também a interface web estática (../frontend), então um único processo
cobre notebook (localhost) e mobile/web (acesso pela rede local ou deploy).
"""
from __future__ import annotations

import os
import secrets
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from markitdown import MarkItDown

# Extensões suportadas (MarkItDown cobre todas com o extra [all]).
SUPPORTED = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv",
    ".pptx", ".ppt", ".html", ".htm", ".txt", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",
    ".epub", ".zip",
}
MAX_BYTES = 50 * 1024 * 1024  # 50 MB

# Pasta do frontend: por padrão ../frontend, mas pode ser sobrescrita via
# TOMARKDOWN_FRONTEND (usado pelo app desktop empacotado, onde o caminho muda).
_env_frontend = os.environ.get("TOMARKDOWN_FRONTEND")
FRONTEND_DIR = Path(_env_frontend) if _env_frontend else (Path(__file__).resolve().parent.parent / "frontend")

app = FastAPI(title="toMarkdown", version="1.0.0")

# Libera o acesso a partir de outros dispositivos (celular na mesma rede) e de PWAs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uma instância é reutilizada entre requisições (é thread-safe para leitura).
_converter = MarkItDown()

# --- Proteção de acesso (opcional) -----------------------------------------
# Defina a variável de ambiente TOMARKDOWN_PASSWORD para exigir login.
# Usuário padrão: "admin" (ajustável via TOMARKDOWN_USER).
# Sem a variável, o app fica aberto (útil para rodar só no localhost).
AUTH_USER = os.environ.get("TOMARKDOWN_USER", "admin")
AUTH_PASSWORD = os.environ.get("TOMARKDOWN_PASSWORD", "")


@app.middleware("http")
async def basic_auth(request: Request, call_next):
    if not AUTH_PASSWORD:  # proteção desativada
        return await call_next(request)

    header = request.headers.get("authorization", "")
    if header.startswith("Basic "):
        import base64

        try:
            user, _, pwd = base64.b64decode(header[6:]).decode("utf-8").partition(":")
        except Exception:  # noqa: BLE001
            user = pwd = ""
        # compare_digest evita vazar o tempo de comparação.
        if secrets.compare_digest(user, AUTH_USER) and secrets.compare_digest(pwd, AUTH_PASSWORD):
            return await call_next(request)

    return Response(
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="toMarkdown"'},
        content="Autenticação necessária.",
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "supported": sorted(SUPPORTED)}


@app.post("/api/convert")
async def convert(file: UploadFile = File(...)) -> dict:
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in SUPPORTED:
        raise HTTPException(
            status_code=415,
            detail=f"Formato '{ext}' não suportado. Suportados: {', '.join(sorted(SUPPORTED))}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo maior que 50 MB.")

    # MarkItDown funciona melhor a partir de um caminho real (usa a extensão como
    # dica do parser). Gravamos num arquivo temporário e removemos ao final.
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".bin") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        result = _converter.convert(tmp_path)
    except Exception as exc:  # noqa: BLE001 — devolve a causa para a UI
        raise HTTPException(status_code=422, detail=f"Falha ao converter: {exc}") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    markdown = (result.text_content or "").strip()
    out_name = f"{Path(file.filename or 'arquivo').stem}.md"
    return {
        "filename": file.filename,
        "markdown_filename": out_name,
        "chars": len(markdown),
        "markdown": markdown,
    }


# Interface web estática (montada por último para não capturar as rotas /api).
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    # host 0.0.0.0 -> acessível pelo celular na rede local e por hosts na nuvem.
    # A porta vem da variável PORT quando hospedado (Render, Cloud Run, HF); 8000 no local.
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
