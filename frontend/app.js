// toMarkdown — lógica da interface. Envia cada arquivo para /api/convert e
// mostra o Markdown resultante com botões de copiar e baixar.

const drop = document.getElementById("drop");
const input = document.getElementById("fileInput");
const results = document.getElementById("results");
const cardTpl = document.getElementById("cardTpl");

// --- Seleção de arquivos ---------------------------------------------------
drop.addEventListener("click", () => input.click());
drop.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }
});
input.addEventListener("change", () => handleFiles(input.files));

["dragenter", "dragover"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("dragover"); })
);
["dragleave", "drop"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("dragover"); })
);
drop.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));

// --- Conversão -------------------------------------------------------------
function handleFiles(fileList) {
  const files = Array.from(fileList || []);
  if (!files.length) return;
  results.hidden = false;
  files.forEach(convertFile);
  input.value = "";
}

async function convertFile(file) {
  const card = cardTpl.content.firstElementChild.cloneNode(true);
  card.querySelector(".card-name").textContent = file.name;
  const status = card.querySelector(".card-status");
  status.innerHTML = '<span class="spinner"></span> convertendo…';
  results.prepend(card);

  try {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/api/convert", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Erro ${res.status}`);

    status.textContent = `${data.chars.toLocaleString("pt-BR")} caracteres`;
    status.classList.add("ok");

    const preview = card.querySelector(".card-preview");
    preview.textContent = data.markdown || "(vazio)";
    preview.hidden = false;

    const actions = card.querySelector(".card-actions");
    actions.hidden = false;
    actions.querySelector(".copy").onclick = () => {
      navigator.clipboard.writeText(data.markdown);
    };
    actions.querySelector(".download").onclick = () =>
      downloadMd(data.markdown, data.markdown_filename);
  } catch (err) {
    status.textContent = "✕ " + err.message;
    status.classList.add("err");
  }
}

function downloadMd(text, name) {
  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name || "arquivo.md";
  a.click();
  URL.revokeObjectURL(url);
}

// --- PWA: registra o service worker ---------------------------------------
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () =>
    navigator.serviceWorker.register("sw.js").catch(() => {})
  );
}
