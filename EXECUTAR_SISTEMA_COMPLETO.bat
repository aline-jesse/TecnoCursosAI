@echo off
cls
echo.
echo ===============================================
echo    TECNOCURSOS AI - INICIALIZACAO COMPLETA
echo ===============================================
echo.

echo [PASSO 1] Verificando estrutura...
if not exist "backend\main.py" (
    echo ERRO: backend\main.py nao encontrado!
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ERRO: frontend\package.json nao encontrado!
    pause
    exit /b 1
)

echo ✅ Estrutura verificada com sucesso!
echo.

echo [PASSO 2] Instalando dependencias do backend...
python -m pip install fastapi uvicorn python-multipart jinja2 aiofiles requests psutil
echo ✅ Dependencias do backend instaladas!
echo.

echo [PASSO 3] Instalando dependencias do frontend...
cd frontend
npm install
cd ..
echo ✅ Dependencias do frontend instaladas!
echo.

echo [PASSO 4] Iniciando Backend na porta 8001...
cd backend
start "Backend - TecnoCursos AI" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload && pause"
cd ..
echo ✅ Backend iniciado em nova janela!
echo.

echo [PASSO 5] Aguardando backend inicializar...
timeout /t 5 /nobreak > nul
echo.

echo [PASSO 6] Iniciando Frontend na porta 3000...
cd frontend
start "Frontend - TecnoCursos AI" cmd /c "npm run start && pause"
cd ..
echo ✅ Frontend iniciado em nova janela!
echo.

echo ===============================================
echo           🎉 SISTEMA INICIADO! 🎉
echo ===============================================
echo.
echo 🌐 Acessos:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8001
echo    API Docs: http://localhost:8001/docs
echo.
echo 💡 Dica: O sistema esta rodando em janelas separadas
echo    Para parar, feche as janelas do Backend e Frontend
echo.
echo ===============================================
echo.
echo Pressione qualquer tecla para fechar...
pause > nul
