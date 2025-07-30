@echo off
echo 🚀 Iniciando TecnoCursos AI Backend...
echo ===============================================

echo 📦 Verificando dependências...
pip install fastapi uvicorn python-multipart pyjwt pydantic[email] email-validator --quiet

echo 🌐 Iniciando servidor na porta 8000...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo.
echo Credenciais de teste:
echo Email: admin@tecnocursos.com
echo Senha: admin123
echo.
echo ===============================================

python simple_backend.py

echo.
echo Servidor parado.
pause
