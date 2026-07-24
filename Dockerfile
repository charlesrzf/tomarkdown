# toMarkdown — imagem para Hugging Face Spaces (Docker SDK).
# O HF espera que o app escute na porta definida por app_port (README) — aqui 7860.

FROM python:3.12-slim

# Dependências de sistema úteis para alguns parsers do MarkItDown.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# O HF Spaces roda o container como usuário não-root (UID 1000).
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" \
    PORT=7860 \
    HF_HOME=/home/user/.cache/huggingface \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala as dependências primeiro (melhor cache de build).
COPY --chown=user backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt

# Copia o restante do projeto (backend + frontend).
COPY --chown=user backend ./backend
COPY --chown=user frontend ./frontend

EXPOSE 7860

# app.py lê a porta da variável PORT (7860 aqui) e serve API + frontend.
CMD ["python", "backend/app.py"]
