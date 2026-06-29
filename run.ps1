# run.ps1 — Local development runner for DocuMind
# Requires: Python 3.11+, Ollama installed and running
#
# Usage:
#   .\run.ps1
#   .\run.ps1 -Model llama3
#   .\run.ps1 -OllamaHost http://192.168.1.10:11434

param(
    [string]$Model      = "mistral",
    [string]$OllamaHost = "http://localhost:11434",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$VenvPath    = Join-Path $ProjectRoot "venv"
$PythonExe   = Join-Path $VenvPath "Scripts\python.exe"
$PipExe      = Join-Path $VenvPath "Scripts\pip.exe"
$StreamlitExe = Join-Path $VenvPath "Scripts\streamlit.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$AppEntry    = Join-Path $ProjectRoot "app\main.py"

Write-Host ""
Write-Host "  ██████╗  ██████╗  ██████╗██╗   ██╗███╗   ███╗██╗███╗   ██╗██████╗ " -ForegroundColor Cyan
Write-Host "  ██╔══██╗██╔═══██╗██╔════╝██║   ██║████╗ ████║██║████╗  ██║██╔══██╗" -ForegroundColor Cyan
Write-Host "  ██║  ██║██║   ██║██║     ██║   ██║██╔████╔██║██║██╔██╗ ██║██║  ██║" -ForegroundColor Cyan
Write-Host "  ██║  ██║██║   ██║██║     ██║   ██║██║╚██╔╝██║██║██║╚██╗██║██║  ██║" -ForegroundColor Cyan
Write-Host "  ██████╔╝╚██████╔╝╚██████╗╚██████╔╝██║ ╚═╝ ██║██║██║ ╚████║██████╔╝" -ForegroundColor Cyan
Write-Host "  ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ " -ForegroundColor Cyan
Write-Host "  Intelligent Document Q&A System" -ForegroundColor DarkCyan
Write-Host ""

# ── 1. Check Python ────────────────────────────────────────────────────────
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "       Download from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
$pyVersion = & python --version 2>&1
Write-Host "      Found: $pyVersion" -ForegroundColor Green

# ── 2. Create / activate venv ─────────────────────────────────────────────
Write-Host "[2/4] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path $VenvPath)) {
    Write-Host "      Creating venv at $VenvPath..." -ForegroundColor DarkGray
    & python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "      Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "      Virtual environment already exists." -ForegroundColor Green
}

# ── 3. Install / update requirements ──────────────────────────────────────
if (-not $SkipInstall) {
    Write-Host "[3/4] Installing requirements (this may take a few minutes on first run)..." -ForegroundColor Yellow
    & $PipExe install --quiet --upgrade pip
    & $PipExe install --quiet -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pip install failed. Check requirements.txt and your internet connection." -ForegroundColor Red
        exit 1
    }
    Write-Host "      Dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[3/4] Skipping installation (-SkipInstall flag set)." -ForegroundColor DarkGray
}

# ── 4. Check Ollama ────────────────────────────────────────────────────────
Write-Host "[4/4] Checking Ollama status at $OllamaHost..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$OllamaHost/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "      Ollama is running." -ForegroundColor Green
} catch {
    Write-Host "WARNING: Ollama does not appear to be running at $OllamaHost." -ForegroundColor DarkYellow
    Write-Host "         Start it with: ollama serve" -ForegroundColor DarkYellow
    Write-Host "         Pull the model: ollama pull $Model" -ForegroundColor DarkYellow
    Write-Host "         (DocuMind will start but LLM queries will fail until Ollama is available.)" -ForegroundColor DarkYellow
}

# ── Launch Streamlit ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "Starting DocuMind..." -ForegroundColor Cyan
Write-Host "  URL:   http://localhost:8501" -ForegroundColor White
Write-Host "  Model: $Model" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

$env:OLLAMA_HOST  = $OllamaHost
$env:OLLAMA_MODEL = $Model

& $StreamlitExe run $AppEntry `
    --server.port 8501 `
    --server.address localhost `
    --browser.gatherUsageStats false
