@echo off
echo 🚀 Iniciando TecnoCursos AI - Editor de Vídeo
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale o Python primeiro.
    pause
    exit /b 1
)

REM Inicia o servidor
echo ✅ Iniciando servidor na porta 8000...
echo 🔗 Acesse: http://localhost:8000
echo.
python server.py

pause 