param(
    [switch]$SkipNpmInstall
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$dashboardDir = Join-Path $projectRoot "dashboard"
$widgetDir = Join-Path $projectRoot "widget"
$venvActivate = Join-Path $backendDir ".venv\Scripts\Activate.ps1"

Write-Host "Project root: $projectRoot" -ForegroundColor Cyan

if (-not (Test-Path $venvActivate)) {
    Write-Host "Backend virtual environment not found at backend/.venv" -ForegroundColor Red
    Write-Host "Run these once, then rerun this script:" -ForegroundColor Yellow
    Write-Host "  cd backend"
    Write-Host "  python -m venv .venv"
    Write-Host "  .\\.venv\\Scripts\\Activate.ps1"
    Write-Host "  pip install -r requirements.txt"
    exit 1
}

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared is not installed." -ForegroundColor Red
    Write-Host "Install it with:" -ForegroundColor Yellow
    Write-Host "  winget install Cloudflare.cloudflared"
    exit 1
}

if (-not $SkipNpmInstall) {
    Write-Host "Installing dashboard dependencies..." -ForegroundColor Cyan
    Push-Location $dashboardDir
    npm install
    Pop-Location

    Write-Host "Installing widget dependencies and building widget bundle..." -ForegroundColor Cyan
    Push-Location $widgetDir
    npm install
    npm run build
    Pop-Location
}

Write-Host "Starting backend server terminal..." -ForegroundColor Green
$backendCmd = "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; cd '$backendDir'; & '$venvActivate'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Write-Host "Starting dashboard dev server terminal..." -ForegroundColor Green
$dashboardCmd = "cd '$dashboardDir'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $dashboardCmd

Start-Sleep -Seconds 4

Write-Host "Starting Cloudflare tunnel for backend (public API + widget loader)..." -ForegroundColor Green
$backendTunnelCmd = "cloudflared tunnel --url http://localhost:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendTunnelCmd

Write-Host "Starting Cloudflare tunnel for dashboard (public admin)..." -ForegroundColor Green
$dashboardTunnelCmd = "cloudflared tunnel --url http://localhost:5173"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $dashboardTunnelCmd

Write-Host "" 
Write-Host "All services launched in separate terminals." -ForegroundColor Cyan
Write-Host "Copy the two https://*.trycloudflare.com URLs from the tunnel terminals." -ForegroundColor Cyan
Write-Host "Use backend tunnel URL for widget embed, for example:" -ForegroundColor Cyan
Write-Host "  https://YOUR_BACKEND_TUNNEL/zenbot.js?site=YOUR_SITE_ID"
Write-Host "" 
Write-Host "Tip: Next time, skip npm install by running:" -ForegroundColor DarkGray
Write-Host "  powershell -ExecutionPolicy Bypass -File .\\scripts\\start-demo-with-tunnels.ps1 -SkipNpmInstall"
