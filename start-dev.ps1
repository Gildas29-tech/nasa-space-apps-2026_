#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Démarre l'environnement de développement FieldShift (Frontend + Backend)

.DESCRIPTION
    Ce script lance :
    - Le backend FastAPI sur http://localhost:8000
    - Le frontend Vite sur http://localhost:5173

.NOTES
    Prérequis : Node.js 18+, Python 3.11+
    Première exécution : installe les dépendances automatiquement
#>

param(
    [switch]$InstallDeps,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendDir = Join-Path $ProjectRoot "backend"

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    FieldShift - Dev Startup                   ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Vérification des prérequis
function Check-Prerequisites {
    Write-Host "🔍 Vérification des prérequis..." -ForegroundColor Cyan

    $nodeVersion = node --version 2>$null
    if (-not $nodeVersion) {
        Write-Error "❌ Node.js non trouvé. Installez Node.js 18+ depuis https://nodejs.org"
        exit 1
    }
    Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Gray

    $pythonVersion = python --version 2>$null
    if (-not $pythonVersion) {
        Write-Error "❌ Python non trouvé. Installez Python 3.11+ depuis https://python.org"
        exit 1
    }
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Gray

    Write-Host ""
}

# Installation dépendances Frontend
function Install-FrontendDeps {
    Write-Host "📦 Installation dépendances Frontend..." -ForegroundColor Cyan
    Set-Location $FrontendDir
    if (-not (Test-Path "node_modules")) {
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Échec npm install"
            exit 1
        }
    } else {
        Write-Host "  ✓ node_modules déjà présent" -ForegroundColor Gray
    }
    Set-Location $ProjectRoot
    Write-Host ""
}

# Installation dépendances Backend
function Install-BackendDeps {
    Write-Host "📦 Installation dépendances Backend..." -ForegroundColor Cyan
    Set-Location $BackendDir

    if (-not (Test-Path "venv")) {
        Write-Host "  Création environnement virtuel..." -ForegroundColor Gray
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Échec création venv"
            exit 1
        }
    }

    $venvPython = Join-Path $BackendDir "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        $venvPython = Join-Path $BackendDir "venv/bin/python"
    }

    Write-Host "  Installation requirements.txt..." -ForegroundColor Gray
    & $venvPython -m pip install --upgrade pip -q
    & $venvPython -m pip install -r requirements.txt -q
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Échec pip install"
        exit 1
    }

    if (-not (Test-Path ".env")) {
        Write-Host "  Création .env depuis .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    }

    Set-Location $ProjectRoot
    Write-Host ""
}

# Démarrage Backend
function Start-Backend {
    Write-Host "🚀 Démarrage Backend (FastAPI)..." -ForegroundColor Cyan
    Set-Location $BackendDir

    $venvPython = Join-Path $BackendDir "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        $venvPython = Join-Path $BackendDir "venv/bin/python"
    }

    $process = Start-Process $venvPython -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -PassThru -WindowStyle Hidden
    $global:BackendProcess = $process
    Write-Host "  ✓ Backend démarré (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "  📍 http://localhost:8000" -ForegroundColor Gray
    Write-Host "  📚 Docs: http://localhost:8000/docs" -ForegroundColor Gray
    Set-Location $ProjectRoot
    Write-Host ""
}

# Démarrage Frontend
function Start-Frontend {
    Write-Host "🚀 Démarrage Frontend (Vite)..." -ForegroundColor Cyan
    Set-Location $FrontendDir

    $process = Start-Process "npm" -ArgumentList "run", "dev", "--", "--host" -PassThru -WindowStyle Hidden
    $global:FrontendProcess = $process
    Write-Host "  ✓ Frontend démarré (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "  📍 http://localhost:5173" -ForegroundColor Gray
    Set-Location $ProjectRoot
    Write-Host ""
}

# Nettoyage à la sortie
function Cleanup {
    Write-Host "`n🛑 Arrêt des processus..." -ForegroundColor Yellow
    if ($global:BackendProcess) {
        Stop-Process -Id $global:BackendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Backend arrêté" -ForegroundColor Gray
    }
    if ($global:FrontendProcess) {
        Stop-Process -Id $global:FrontendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Frontend arrêté" -ForegroundColor Gray
    }
    Write-Host "👋 Au revoir !" -ForegroundColor Green
}

# Main
try {
    Check-Prerequisites

    if ($InstallDeps -or -not (Test-Path (Join-Path $FrontendDir "node_modules")) -or -not (Test-Path (Join-Path $BackendDir "venv"))) {
        Install-FrontendDeps
        Install-BackendDeps
    }

    if (-not $FrontendOnly) { Start-Backend }
    if (-not $BackendOnly) { Start-Frontend }

    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✨ FieldShift est prêt !                                     ║" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "║  Frontend:  http://localhost:5173                            ║" -ForegroundColor Green
    Write-Host "║  Backend:   http://localhost:8000                            ║" -ForegroundColor Green
    Write-Host "║  API Docs:  http://localhost:8000/docs                       ║" -ForegroundColor Green
    Write-Host "║                                                               ║" -ForegroundColor Green
    Write-Host "║  Appuyez sur Ctrl+C pour arrêter                             ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green

    # Attendre Ctrl+C
    while ($true) { Start-Sleep -Seconds 1 }
}
finally {
    Cleanup
}