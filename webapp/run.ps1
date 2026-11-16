# Windows PowerShell: build frontend nếu cần rồi chạy FastAPI ở http://localhost:8000
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path frontend/node_modules)) { Push-Location frontend; npm install --no-audit --no-fund; Pop-Location }
if (-not (Test-Path frontend/dist)) { Push-Location frontend; npm run build; Pop-Location }
Set-Location backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
