# Mostrar información del sistema operativo
$osInfo = Get-WmiObject Win32_OperatingSystem
Write-Host "===== Información del Sistema Operativo =====" -ForegroundColor Cyan
Write-Host "Versión: $($osInfo.Caption)"
Write-Host "Arquitectura: $($osInfo.OSArchitecture)"

# Función para obtener detalles del driver (versión, compañía, fecha de creación)
function Get-DriverDetails {
    param (
        [string]$driverPath
    )

    if (Test-Path $driverPath) {
        $file = Get-Item $driverPath
        $version = (Get-Command $driverPath).FileVersionInfo.FileVersion
        $company = (Get-Command $driverPath).FileVersionInfo.CompanyName
        $date = $file.CreationTime
        return [PSCustomObject]@{
            Driver = $file.Name
            Version = $version
            Company = $company
            Date = $date
        }
    }
}

# Mostrar drivers ODBC de 64 bits
Write-Host "`n===== ODBC Drivers de 64 bits =====" -ForegroundColor Cyan
$drivers64 = Get-ItemProperty -Path "HKLM:\SOFTWARE\ODBC\ODBCINST.INI\ODBC Drivers"
$drivers64.PSObject.Properties | ForEach-Object {
    $driverName = $_.Name
    $driverKeyPath = "HKLM:\SOFTWARE\ODBC\ODBCINST.INI\$driverName"

    # Comprobamos si la clave existe y tiene la propiedad 'Driver'
    if (Test-Path $driverKeyPath) {
        $driverPath = (Get-ItemProperty $driverKeyPath).Driver
        if ($driverPath) {
            Write-Host "`nDriver: $driverName"
            $driverDetails = Get-DriverDetails -driverPath $driverPath
            Write-Host "Version: $($driverDetails.Version)"
            Write-Host "Company: $($driverDetails.Company)"
            Write-Host "Date Created: $($driverDetails.Date)"
        }
    }
}

# Mostrar drivers ODBC de 32 bits
Write-Host "`n===== ODBC Drivers de 32 bits =====" -ForegroundColor Cyan
$drivers32 = Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\ODBC\ODBCINST.INI\ODBC Drivers"
$drivers32.PSObject.Properties | ForEach-Object {
    $driverName = $_.Name
    $driverKeyPath = "HKLM:\SOFTWARE\WOW6432Node\ODBC\ODBCINST.INI\$driverName"

    # Comprobamos si la clave existe y tiene la propiedad 'Driver'
    if (Test-Path $driverKeyPath) {
        $driverPath = (Get-ItemProperty $driverKeyPath).Driver
        if ($driverPath) {
            Write-Host "`nDriver: $driverName"
            $driverDetails = Get-DriverDetails -driverPath $driverPath
            Write-Host "Version: $($driverDetails.Version)"
            Write-Host "Company: $($driverDetails.Company)"
            Write-Host "Date Created: $($driverDetails.Date)"
        }
    }
}
