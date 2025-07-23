@echo off
title TecnoCursosAI - Frontend React
echo ===============================================
echo    TecnoCursosAI - Iniciando Frontend
echo ===============================================
echo.

REM Navega para a pasta frontend
cd /d "%~dp0frontend"

REM Verifica se o Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js não está instalado!
    echo Por favor, instale Node.js em https://nodejs.org/
    pause
    exit /b 1
)

REM Verifica se as dependências estão instaladas
if not exist "node_modules" (
    echo [INFO] Instalando dependências do frontend...
    npm install
)

echo.
echo [INFO] Iniciando servidor de desenvolvimento React...
echo.
echo ===============================================
echo    Frontend será iniciado em:
echo    http://localhost:3000
echo ===============================================
echo.

REM Inicia o React
npm start