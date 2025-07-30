@echo off
title TecnoCursos AI - Servidor Backend
echo 🚀 Iniciando TecnoCursos AI Backend...
echo ===============================================

echo 📦 Instalando dependências...
pip install fastapi uvicorn python-multipart pyjwt pydantic[email] email-validator --quiet

echo 🌐 Iniciando servidor na porta 8000...
echo ✅ Backend estará disponível em: http://localhost:8000
echo 📚 Documentação da API: http://localhost:8000/docs
echo ❤️ Health Check: http://localhost:8000/health
echo.
echo 🔑 Credenciais de teste:
echo Email: admin@tecnocursos.com
echo Senha: admin123
echo.
echo ⚠️ Para parar o servidor, pressione Ctrl+C
echo ===============================================

python simple_backend.py

pause
