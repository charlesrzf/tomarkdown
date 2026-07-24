# toMarkdown

Conversor **local** de documentos para Markdown. Converte PDF, Word (`.docx`),
Excel (`.xlsx`), PowerPoint (`.pptx`), imagens e HTML — tudo rodando no seu
equipamento, sem serviço pago e sem enviar os arquivos para a nuvem.

Usa [MarkItDown](https://github.com/microsoft/markitdown) (Microsoft) para a
conversão e um backend [FastAPI](https://fastapi.tiangolo.com/) que também serve
a interface web (que funciona como PWA instalável no celular).

## Como rodar

### 1. Instalar o Python (só na primeira vez)

```powershell
winget install Python.Python.3.12
```

Feche e reabra o terminal depois de instalar.

### 2. Subir a aplicação

```powershell
.\run.ps1
```

Na primeira execução ele cria o ambiente virtual e instala as dependências
(pode levar alguns minutos). Depois é só abrir:

- **No notebook:** http://localhost:8000
- **No celular** (mesma rede Wi-Fi): o endereço `http://192.168.x.x:8000` que o
  script mostra. No navegador do celular dá para "Adicionar à tela inicial" e usar
  como app.

## Arquitetura

```
toMarkdown/
├── backend/
│   ├── app.py            # FastAPI + MarkItDown + serve o frontend
│   └── requirements.txt
├── frontend/             # interface web / PWA (HTML, CSS, JS puro)
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   ├── manifest.webmanifest
│   ├── sw.js             # service worker (casco offline)
│   └── icon.svg
├── run.ps1               # setup + execução (Windows)
└── README.md
```

## Formatos suportados

PDF · DOCX · DOC · XLSX · XLS · CSV · PPTX · PPT · HTML · TXT · JSON · XML ·
PNG · JPG · WEBP · EPUB · ZIP. Limite de 50 MB por arquivo (ajustável em
`backend/app.py`).

## Deploy grátis no Render

O projeto já vem pronto para o Render (arquivo `render.yaml`). O tier gratuito
não exige cartão de crédito.

1. Suba o projeto para um repositório no **GitHub** (o Render faz deploy a partir
   do Git):

   ```bash
   git init
   git add .
   git commit -m "toMarkdown"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/tomarkdown.git
   git push -u origin main
   ```

2. Em https://render.com, crie a conta e escolha **New → Blueprint**. Aponte para
   o repositório: o Render lê o `render.yaml` e cria o serviço `tomarkdown`
   (plano **Free**) automaticamente.
3. Em **Environment**, defina a variável `TOMARKDOWN_PASSWORD` com a senha
   desejada (o `render.yaml` já a declara como obrigatória, sem valor).
4. Aguarde o build. Ao abrir a URL (`https://tomarkdown.onrender.com`), o
   navegador pedirá usuário/senha.

> **Limitações do tier gratuito:** ~512 MB de RAM (PDFs muito grandes ou
> escaneados podem faltar memória) e hibernação após 15 min de inatividade, com
> "cold start" de 30–60s no próximo acesso.

> **Precisa de áudio ou mais memória?** O `render.yaml` usa o Python nativo (sem
> `ffmpeg`). Para transcrição de áudio, troque para deploy via Docker no Render
> (o `Dockerfile` incluído já instala o `ffmpeg`).

## Próximos passos possíveis

- **App desktop** (Windows/Mac/Linux) com [Tauri](https://tauri.app/), embutindo o backend.
- **OCR melhorado** para PDFs escaneados (Docling ou Tesseract).
- **Conversão 100% offline no navegador** (WASM) para os formatos mais simples.
