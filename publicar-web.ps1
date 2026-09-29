# ============================================================
#  Dulas Properties - Publicar la web (sustituye a deploy.bat)
#  Ejecutar:  powershell -ExecutionPolicy Bypass -File "C:\Users\PC\Desktop\EMPRESA\WEB DULAS ACTUAL\publicar-web.ps1"
#  1) Comprueba la sesion de Cloudflare (y la abre si hace falta)
#  2) Publica la web   3) Guarda los cambios en GitHub   4) Comprueba que la zona privada sigue protegida
# ============================================================
$ErrorActionPreference = 'Continue'
$Proyecto = 'dulas-properties'
$Web = Split-Path -Parent $MyInvocation.MyCommand.Path
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
function Titulo($t) { Write-Host ''; Write-Host "=== $t ===" -ForegroundColor Cyan }
function Ok($t)     { Write-Host "  OK  $t" -ForegroundColor Green }
function Aviso($t)  { Write-Host "  !!  $t" -ForegroundColor Yellow }
function Salir($msg) { Write-Host ''; Write-Host "ERROR: $msg" -ForegroundColor Red; Read-Host 'Pulsa Enter para cerrar'; exit 1 }
Set-Location $Web
if (-not (Test-Path (Join-Path $Web 'functions\_lib\auth.js'))) { Salir 'Este script tiene que estar en la carpeta WEB DULAS ACTUAL.' }

Titulo '1. Sesion de Cloudflare'
wrangler whoami 2>&1 | Out-String | Set-Variable quien
if ($quien -notmatch 'dulasproperties') {
    Aviso 'No hay sesion abierta. Se abre el navegador: baja hasta el final de los permisos y pulsa Autorizar.'
    wrangler login
    wrangler whoami 2>&1 | Out-String | Set-Variable quien
    if ($quien -notmatch 'dulasproperties') { Salir 'No se pudo iniciar sesion en Cloudflare.' }
}
Ok 'Sesion de Cloudflare abierta'

Titulo '2. Publicando la web'
wrangler pages deploy . --project-name=$Proyecto --branch=master
if ($LASTEXITCODE -ne 0) { Salir 'La publicacion ha fallado' }
Ok 'Web publicada'

Titulo '3. Guardando en GitHub'
git add -A
git reset -q -- colaboradores/activos.json 2>$null
$pend = git status --porcelain
if ($pend) {
    git -c user.name="Dulas Properties" -c user.email="info@dulasproperties.com" commit -q -m ("Actualizacion web " + (Get-Date -Format 'yyyy-MM-dd HH:mm'))
    git pull --rebase -q origin master
    git push -q origin master
    if ($LASTEXITCODE -ne 0) { Aviso 'No se pudo subir a GitHub; la web SI esta publicada.' } else { Ok 'Guardado en GitHub' }
} else { Ok 'No habia cambios que guardar en GitHub' }

Titulo '4. Comprobacion'
Start-Sleep -Seconds 5
try { $r = Invoke-WebRequest -Uri 'https://dulasproperties.com/colaboradores/activos.json' -MaximumRedirection 0 -UseBasicParsing -ErrorAction SilentlyContinue; $code = $r.StatusCode } catch { $code = $_.Exception.Response.StatusCode.value__ }
if ($code -eq 302) { Ok 'La zona privada sigue protegida' } else { Aviso "Respuesta inesperada ($code). Avisa a Claude." }
Write-Host ''; Write-Host 'Listo. Si no ves los cambios, pulsa Ctrl + F5 en el navegador.' -ForegroundColor Green
Read-Host 'Pulsa Enter para cerrar'
