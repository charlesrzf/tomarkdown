"""
toMarkdown Desktop — abre a aplicação numa janela nativa (pywebview).

Sobe o servidor FastAPI numa porta local livre, em uma thread de fundo, e
mostra a interface numa janela do sistema (WebView2 no Windows). Quando
empacotado com PyInstaller, os arquivos ficam em sys._MEIPASS.
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path

# --- Localiza os recursos (frontend/backend), com ou sem PyInstaller --------
if getattr(sys, "frozen", False):
    # Executável empacotado: os dados vão para a pasta temporária _MEIPASS.
    BASE = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    BASE = Path(__file__).resolve().parent.parent

# Aponta o app.py para o frontend correto e garante que o backend é importável.
os.environ.setdefault("TOMARKDOWN_FRONTEND", str(BASE / "frontend"))
sys.path.insert(0, str(BASE))

import uvicorn  # noqa: E402
import webview  # noqa: E402

from backend.app import app  # noqa: E402


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run_server(port: int) -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    # Desliga os handlers de sinal (só funcionam na thread principal).
    server.install_signal_handlers = lambda: None  # type: ignore[assignment]
    server.run()


def _wait_ready(port: int, timeout: float = 30.0) -> bool:
    url = f"http://127.0.0.1:{port}/api/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def main() -> None:
    # Porta fixa opcional (usada em testes); caso contrário, escolhe uma livre.
    env_port = os.environ.get("TOMARKDOWN_DESKTOP_PORT")
    port = int(env_port) if env_port else _free_port()
    threading.Thread(target=_run_server, args=(port,), daemon=True).start()
    _wait_ready(port)
    webview.create_window(
        "toMarkdown",
        f"http://127.0.0.1:{port}",
        width=1024,
        height=740,
        min_size=(640, 480),
    )
    webview.start()


if __name__ == "__main__":
    main()
