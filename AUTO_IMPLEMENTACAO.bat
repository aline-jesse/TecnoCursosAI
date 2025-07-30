@echo off
title TecnoCursos AI - Auto Implementacao

cls
echo.
echo ████████╗███████╗ ██████╗███╗   ██╗ ██████╗  ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ███████╗
echo ╚══██╔══╝██╔════╝██╔════╝████╗  ██║██╔═══██╗██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔════╝
echo    ██║   █████╗  ██║     ██╔██╗ ██║██║   ██║██║     ██║   ██║██████╔╝███████╗██║   ██║███████╗
echo    ██║   ██╔══╝  ██║     ██║╚██╗██║██║   ██║██║     ██║   ██║██╔══██╗╚════██║██║   ██║╚════██║
echo    ██║   ███████╗╚██████╗██║ ╚████║╚██████╔╝╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝███████║
echo    ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝
echo.
echo                            🚀 AUTO IMPLEMENTACAO COMPLETA 🚀
echo ==================================================================================
echo.

echo [ETAPA 1/5] Verificando Python...
python --version 2>nul
if errorlevel 1 (
    echo ❌ ERRO: Python nao encontrado! Instale Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python verificado

echo.
echo [ETAPA 2/5] Instalando dependencias criticas...
python -m pip install --upgrade pip --quiet
python -m pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 --quiet --user
python -m pip install python-multipart pyjwt pydantic[email] --quiet --user
echo ✅ Dependencias instaladas

echo.
echo [ETAPA 3/5] Liberando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%a 2>nul
echo ✅ Porta liberada

echo.
echo [ETAPA 4/5] Iniciando auto implementador...
echo 📍 URL Backend: http://localhost:8000
echo 📚 Documentacao: http://localhost:8000/docs
echo ❤️ Health Check: http://localhost:8000/health
echo 🔑 Login: admin@tecnocursos.com / admin123
echo.

echo [ETAPA 5/5] Executando servidor...
echo ==================================================================================
echo ⚠️  MANTENHA ESTA JANELA ABERTA PARA O SERVIDOR FUNCIONAR
echo ⚠️  Para parar o servidor: Ctrl+C
echo ==================================================================================
echo.

timeout /t 3 /nobreak >nul
start "" "http://localhost:8000" 2>nul
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/docs" 2>nul

python AUTO_IMPLEMENTAR.py

echo.
echo 🛑 Servidor parado.
echo 💡 Para reiniciar: execute AUTO_IMPLEMENTACAO.bat novamente
pause
