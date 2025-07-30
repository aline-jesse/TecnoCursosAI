@echo off
echo ===========================================
echo INICIANDO TECNOCURSOS AI - FRONTEND E BACKEND
echo ===========================================

echo.
echo [1] Verificando se Node.js esta instalado...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Node.js nao encontrado! Instale o Node.js primeiro.
    pause
    exit /b 1
)
echo ✅ Node.js encontrado!

echo.
echo [2] Verificando se Python esta instalado...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)
echo ✅ Python encontrado!

echo.
echo [3] Instalando dependencias do backend...
cd backend
pip install fastapi uvicorn python-multipart jinja2 aiofiles requests psutil sqlalchemy pydantic pydantic-settings python-dotenv
echo ✅ Dependencias do backend instaladas!

echo.
echo [4] Instalando dependencias do frontend...
cd ..\frontend
call npm install
echo ✅ Dependencias do frontend instaladas!

echo.
echo [5] Iniciando Backend em nova janela...
cd ..\backend
start "TecnoCursos Backend" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
echo ✅ Backend iniciado na porta 8001

echo.
echo [6] Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

echo.
echo [7] Iniciando Frontend em nova janela...
cd ..\frontend
start "TecnoCursos Frontend" cmd /c "npm start"
echo ✅ Frontend iniciado na porta 3000

echo.
echo ===========================================
echo 🎉 SISTEMA INICIADO COM SUCESSO! 🎉
echo ===========================================
echo.
echo 🌐 Acesse:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8001
echo    API Docs: http://localhost:8001/docs
echo.
echo 💡 Os serviços estao rodando em janelas separadas
echo    Para parar, feche as janelas do Backend e Frontend
echo.
echo ===========================================

echo.
echo Pressione qualquer tecla para abrir o navegador...
pause >nul

echo.
echo Abrindo navegador...
start http://localhost:3000
start http://localhost:8001/docs

echo.
echo Tudo pronto! ✅
pause
