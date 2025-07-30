@echo off
title TecnoCursos AI - Executor Final
cls

echo.
echo 🚀 TECNOCURSOS AI - EXECUTOR FINAL
echo ================================
echo.

echo [1] Verificando Python...
python --version
if errorlevel 1 goto :error

echo.
echo [2] Instalando dependencias...
python -m pip install fastapi uvicorn --quiet --user

echo.
echo [3] Liberando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul

echo.
echo [4] Iniciando servidor...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo.
echo Credenciais: admin@tecnocursos.com / admin123
echo ================================
echo.

timeout /t 2 /nobreak >nul
start "" "http://localhost:8000"
timeout /t 1 /nobreak >nul
start "" "http://localhost:8000/docs"

python simple_backend.py
goto :end

:error
echo ERRO: Python nao encontrado!
pause

:end
echo Servidor parado.
pause
