@echo off
REM Despliegue de Dulas Properties a Cloudflare Pages
REM Doble clic en este archivo para publicar los cambios de la web
REM NOTA: este script despliega al MISMO proyecto Pages de siempre.
REM No toca el dominio ni borra nada del proyecto existente.

cd /d "%~dp0"

echo ============================================
echo   Publicando Dulas Properties en Cloudflare
echo ============================================
echo.

wrangler pages deploy . --project-name=dulas-properties --branch=production

echo.
echo ============================================
echo   Despliegue finalizado. Comprobando la web...
echo ============================================

node verificar-sitio.js

pause
