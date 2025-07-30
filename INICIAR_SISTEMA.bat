@echo off
echo 🚀 INICIANDO TecnoCursos AI - Sistema Completo
echo ================================================

echo 📦 Instalando dependencias...
pip install fastapi uvicorn pyjwt python-multipart email-validator requests python-dotenv

echo 🚀 Iniciando servidor na porta 8000...
echo ⭐ Acesse: http://127.0.0.1:8000
echo 📚 Docs: http://127.0.0.1:8000/docs
echo 🔑 Login: admin@tecnocursos.com / admin123

python server_completo.py

pause
