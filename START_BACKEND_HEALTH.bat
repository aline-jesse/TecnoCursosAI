@echo off
echo ======================================
echo INICIANDO BACKEND COM HEALTH CHECK
echo ======================================

echo.
echo [1] Instalando dependencias...
python -m pip install fastapi uvicorn python-multipart requests

echo.
echo [2] Iniciando servidor backend...
echo.
echo 🚀 TecnoCursos AI Backend
echo 📍 URL: http://localhost:8001
echo ❤️ Health: http://localhost:8001/health
echo 📚 Docs: http://localhost:8001/docs
echo.

python backend_with_health.py

echo.
echo Backend finalizado!
pause
