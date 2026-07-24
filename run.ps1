# toMarkdown — setup e execução (Windows / PowerShell)
# Uso:  .\run.ps1
# Cria o ambiente virtual na primeira vez, instala as dependências e sobe o servidor.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$venv = Join-Path $root ".venv"
$py   = Join-Path $venv "Scripts\python.exe"

# Descobre um Python real (ignora o atalho da Microsoft Store).
function Get-RealPython {
  foreach ($cmd in @("py", "python")) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c -and $c.Source -notlike "*WindowsApps*") { return $c.Source }
  }
  return $null
}

if (-not (Test-Path $py)) {
  $sys = Get-RealPython
  if (-not $sys) {
    Write-Host "Python nao encontrado. Instale com:  winget install Python.Python.3.12" -ForegroundColor Yellow
    exit 1
  }
  Write-Host "Criando ambiente virtual..." -ForegroundColor Cyan
  & $sys -m venv $venv
  & $py -m pip install --upgrade pip
  & $py -m pip install -r (Join-Path $root "backend\requirements.txt")
}

Write-Host ""
Write-Host "Servidor rodando em:" -ForegroundColor Green
Write-Host "  Notebook:  http://localhost:8000"
$ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
       Where-Object { $_.PrefixOrigin -eq "Dhcp" -or $_.IPAddress -like "192.168.*" } |
       Select-Object -First 1 -ExpandProperty IPAddress)
if ($ip) { Write-Host "  Celular:   http://${ip}:8000   (mesma rede Wi-Fi)" }
Write-Host ""

& $py (Join-Path $root "backend\app.py")
