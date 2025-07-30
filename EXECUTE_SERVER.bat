@echo off
cd /d "%~dp0"
title TecnoCursos AI Backend

echo.
echo 🚀 TECNOCURSOS AI - SERVIDOR BACKEND
echo ====================================================
echo.

echo 📍 Diretorio: %CD%
echo 📅 Data/Hora: %DATE% %TIME%
echo.

echo 📦 Instalando dependencias...
python -m pip install fastapi uvicorn python-multipart pyjwt --quiet

echo.
echo 🌐 Iniciando servidor na porta 8000...
echo URL Principal: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo 🔑 Credenciais de teste:
echo    Email: admin@tecnocursos.com
echo    Senha: admin123
echo.
echo ⚠️  Para parar o servidor: Ctrl+C
echo ====================================================
echo.

python simple_backend.py

echo.
echo 🛑 Servidor parado.
pause
