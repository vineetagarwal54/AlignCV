# Quick start script for AlignCV (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AlignCV - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "myenv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first: python -m venv myenv"
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "myenv\Scripts\Activate.ps1"

# Check for API key
if (-not $env:GOOGLE_API_KEY) {
    Write-Host ""
    Write-Host "ERROR: GOOGLE_API_KEY not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it with:" -ForegroundColor Yellow
    Write-Host '  $env:GOOGLE_API_KEY="your-api-key-here"' -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "API Key: $($env:GOOGLE_API_KEY.Substring(0,10))..." -ForegroundColor Green
Write-Host ""

# Run setup test
Write-Host "Running setup test..." -ForegroundColor Yellow
python test_setup.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  1. Backend:   uvicorn main:app --reload" -ForegroundColor Cyan
Write-Host "  2. Streamlit: streamlit run streamlit_app.py" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"
