# Mostrar información del sistema operativo
$osInfo = Get-WmiObject Win32_OperatingSystem
Write-Host "===== Información del Sistema Operativo =====" -ForegroundColor Cyan
Write-Host "Versión: $($osInfo.Caption)"
Write-Host "Arquitectura: $($osInfo.OSArchitecture)"

# Mostrar drivers ODBC de 64 bits
Write-Host "`n===== ODBC Drivers de 64 bits =====" -ForegroundColor Cyan
$drivers64 = Get-ItemProperty -Path "HKLM:\SOFTWARE\ODBC\ODBCINST.INI\ODBC Drivers"
$drivers64.PSObject.Properties | ForEach-Object {
    Write-Host "$($_.Name) - 64 bits"
}

# Mostrar drivers ODBC de 32 bits
Write-Host "`n===== ODBC Drivers de 32 bits =====" -ForegroundColor Cyan
$drivers32 = Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\ODBC\ODBCINST.INI\ODBC Drivers"
$drivers32.PSObject.Properties | ForEach-Object {
    Write-Host "$($_.Name) - 32 bits"
}
