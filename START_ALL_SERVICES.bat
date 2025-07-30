@echo off
echo ========================================
echo   TECNOCURSOS AI - INICIALIZADOR COMPLETO
echo ========================================

echo.
echo 📦 Iniciando Backend...
echo.

cd backend
call venv\Scripts\activate.bat

echo 🚀 Instalando dependencias extras se necessario...
pip install fastapi uvicorn sqlalchemy pydantic python-multipart jinja2 aiofiles pydantic-settings python-dotenv python-jose[cryptography] passlib[bcrypt] email-validator

echo.
echo 🌐 Iniciando servidor backend na porta 8001...
start "TecnoCursos Backend" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"

echo.
echo ⏳ Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

cd ..\frontend

echo.
echo 🎨 Instalando dependencias do frontend...
call npm install

echo.
echo 🚀 Iniciando frontend na porta 3000...
start "TecnoCursos Frontend" cmd /k "npm run dev"

echo.
echo =========================================
echo    TECNOCURSOS AI INICIADO COM SUCESSO!
echo =========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
