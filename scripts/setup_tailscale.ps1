# Tailscale Setup Script for Windows
# This script helps you install and configure Tailscale

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Tailscale Setup for Item AI Assistant" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Tailscale is installed
Write-Host "Checking if Tailscale is installed..." -ForegroundColor Yellow
$tailscalePath = "C:\Program Files\Tailscale\tailscale.exe"

if (Test-Path $tailscalePath) {
    Write-Host "✓ Tailscale is already installed" -ForegroundColor Green
} else {
    Write-Host "✗ Tailscale not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Tailscale first:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://tailscale.com/download" -ForegroundColor White
    Write-Host "2. Download Windows version" -ForegroundColor White
    Write-Host "3. Run installer" -ForegroundColor White
    Write-Host "4. Run this script again" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Checking Tailscale status..." -ForegroundColor Yellow

# Get Tailscale status
try {
    $status = & $tailscalePath status
    Write-Host "✓ Tailscale is running" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Tailscale IP:" -ForegroundColor Cyan
    $ip = & $tailscalePath ip -4
    Write-Host $ip -ForegroundColor Green
} catch {
    Write-Host "✗ Tailscale is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Starting Tailscale..." -ForegroundColor Yellow
    & $tailscalePath up
}

Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Install Tailscale on your phone:" -ForegroundColor White
Write-Host "   - Android: Google Play Store → Search 'Tailscale'" -ForegroundColor Gray
Write-Host "   - iPhone: App Store → Search 'Tailscale'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Sign in on phone with SAME account as laptop" -ForegroundColor White
Write-Host ""
Write-Host "3. In Item Assistant app settings, enter:" -ForegroundColor White
Write-Host "   - Laptop IP: $ip" -ForegroundColor Green
Write-Host "   - Port: 8765" -ForegroundColor Green
Write-Host "   - Auth Token: ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ" -ForegroundColor Green
Write-Host ""
Write-Host "4. Test connection from mobile data (not Wi-Fi)" -ForegroundColor White
Write-Host ""
Write-Host "For more help, see: docs/TAILSCALE_SETUP.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
