# Wake-on-LAN Setup Script for Windows
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup_wol.ps1

Write-Host "=" * 80
Write-Host "Wake-on-LAN Setup for Item AI Assistant"
Write-Host "=" * 80

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`n✗ This script must be run as Administrator"
    Write-Host "  Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

# Get network adapters
Write-Host "`nDiscovering network adapters..."
$adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.MediaType -eq "802.3" }

if ($adapters.Count -eq 0) {
    Write-Host "✗ No active Ethernet adapters found"
    exit 1
}

Write-Host "`nActive network adapters:"
$i = 1
foreach ($adapter in $adapters) {
    Write-Host "  $i. $($adapter.Name) - $($adapter.InterfaceDescription)"
    Write-Host "     MAC: $($adapter.MacAddress)"
    $i++
}

# Select adapter
if ($adapters.Count -eq 1) {
    $selectedAdapter = $adapters[0]
    Write-Host "`nUsing adapter: $($selectedAdapter.Name)"
}
else {
    $selection = Read-Host "`nSelect adapter number (1-$($adapters.Count))"
    $selectedAdapter = $adapters[$selection - 1]
}

# Display MAC address
Write-Host "`nMAC Address: $($selectedAdapter.MacAddress)"
Write-Host "  (Save this for Wake-on-LAN configuration)"

# Enable Wake-on-LAN in network adapter properties
Write-Host "`nEnabling Wake-on-LAN in adapter settings..."

try {
    # Enable Magic Packet
    $adapterName = $selectedAdapter.Name
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
    
    # Find the adapter's registry key
    Get-ChildItem $regPath | ForEach-Object {
        $driverDesc = Get-ItemProperty -Path $_.PSPath -Name "DriverDesc" -ErrorAction SilentlyContinue
        if ($driverDesc.DriverDesc -eq $selectedAdapter.InterfaceDescription) {
            # Enable Wake on Magic Packet
            Set-ItemProperty -Path $_.PSPath -Name "*WakeOnMagicPacket" -Value "1" -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $_.PSPath -Name "WakeOnMagicPacket" -Value "1" -ErrorAction SilentlyContinue
        }
    }
    
    # Enable in Power Management
    $adapterPnP = Get-PnpDevice | Where-Object { $_.FriendlyName -eq $selectedAdapter.InterfaceDescription }
    if ($adapterPnP) {
        $powerMgmt = Get-CimInstance -ClassName MSPower_DeviceWakeEnable -Namespace root\wmi | Where-Object { $_.InstanceName -like "*$($adapterPnP.InstanceId)*" }
        if ($powerMgmt) {
            $powerMgmt.Enable = $true
            Set-CimInstance -InputObject $powerMgmt
        }
    }
    
    Write-Host "✓ Wake-on-LAN enabled in adapter settings"
}
catch {
    Write-Host "⚠ Partial configuration - please check adapter properties manually"
}

# Instructions
Write-Host "`n" + "=" * 80
Write-Host "NEXT STEPS:"
Write-Host "=" * 80
Write-Host "1. BIOS/UEFI Setup:"
Write-Host "   - Restart your laptop and enter BIOS/UEFI (usually Del, F2, or F12)"
Write-Host "   - Find 'Power Management' or 'Advanced' settings"
Write-Host "   - Enable 'Wake on LAN' or 'PME Event Wake Up'"
Write-Host "   - Save and exit"
Write-Host "`n2. Network Adapter Settings (verify):"
Write-Host "   - Open Device Manager"
Write-Host "   - Find your network adapter under 'Network adapters'"
Write-Host "   - Right-click → Properties → Power Management"
Write-Host "   - Check: 'Allow this device to wake the computer'"
Write-Host "   - Check: 'Only allow a magic packet to wake the computer'"
Write-Host "`n3. Router Configuration (for remote WoL):"
Write-Host "   - Forward UDP port 9 to broadcast address (e.g., 192.168.1.255)"
Write-Host "   - Or use Tailscale VPN for easier setup"
Write-Host "`n4. Add MAC address to config.yaml:"
Write-Host "   MAC Address: $($selectedAdapter.MacAddress)"
Write-Host "=" * 80
