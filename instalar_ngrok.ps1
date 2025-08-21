# Script PowerShell para instalar ngrok automáticamente
# Ejecutar como: PowerShell -ExecutionPolicy Bypass -File instalar_ngrok.ps1

Write-Host "🔧 INSTALADOR AUTOMÁTICO DE NGROK" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$downloadPath = "$env:TEMP\ngrok.zip"
$extractPath = "$env:USERPROFILE\ngrok"

Write-Host "📥 Descargando ngrok..." -ForegroundColor Yellow

try {
    Invoke-WebRequest -Uri $ngrokUrl -OutFile $downloadPath
    Write-Host "✅ Descarga completa" -ForegroundColor Green
} catch {
    Write-Host "❌ Error descargando: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Descomprimiendo..." -ForegroundColor Yellow

try {
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $extractPath | Out-Null
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath
    Write-Host "✅ Descompresión completa" -ForegroundColor Green
} catch {
    Write-Host "❌ Error descomprimiendo: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Agregando al PATH..." -ForegroundColor Yellow

# Agregar ngrok al PATH del usuario
$userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($userPath -notlike "*$extractPath*") {
    $newPath = "$userPath;$extractPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
    Write-Host "✅ ngrok agregado al PATH" -ForegroundColor Green
} else {
    Write-Host "✅ ngrok ya está en el PATH" -ForegroundColor Green
}

# Limpiar archivo temporal
Remove-Item $downloadPath -Force

Write-Host ""
Write-Host "🎉 INSTALACIÓN COMPLETA!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. Reinicia PowerShell/cmd"
Write-Host "2. Ve a https://dashboard.ngrok.com/get-started/your-authtoken"
Write-Host "3. Ejecuta: ngrok authtoken TU_TOKEN"
Write-Host "4. Ejecuta: ngrok http 8080"
Write-Host "5. En otra terminal: python bot_webhook.py"
Write-Host ""
Write-Host "🔥 ALTERNATIVA MÁS RÁPIDA: USA HOTSPOT MÓVIL" -ForegroundColor Yellow
