# Windows Startup Setup Script
# Creates a scheduled task to auto-start Item on Windows login

Write-Host "=" * 80
Write-Host "Item AI Assistant - Startup Configuration"
Write-Host "=" * 80

# Get current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
$pythonExe = Join-Path $projectDir "venv\Scripts\python.exe"
$mainScript = Join-Path $projectDir "item_assistant\main.py"

# Check if virtual environment exists
if (!(Test-Path $pythonExe)) {
    Write-Host "`n✗ Virtual environment not found"
    Write-Host "  Please run install.ps1 first"
    exit 1
}

Write-Host "`nCreating startup task..."

# Create scheduled task
$taskName = "Item AI Assistant"
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "-m item_assistant.main" -WorkingDirectory $projectDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Register task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

Write-Host "✓ Startup task created: '$taskName'"
Write-Host "`nItem will now start automatically when you log in to Windows"
Write-Host "`nTo disable auto-start, run:"
Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
Write-Host "=" * 80
