@echo off
echo ============================
echo TECNOCURSOS AI - INICIALIZACAO
echo ============================

echo.
echo [1/3] Verificando diretórios...
if not exist "backend" (
    echo ERRO: Diretório backend não encontrado!
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERRO: Diretório frontend não encontrado!
    pause
    exit /b 1
)

echo Diretórios OK!

echo.
echo [2/3] Iniciando Backend...
cd backend
echo Executando: python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
start "TecnoCursos Backend" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

echo Aguardando backend inicializar...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] Iniciando Frontend...
cd ..\frontend
echo Executando: npm run dev
start "TecnoCursos Frontend" cmd /k "npm run dev"

echo.
echo ============================
echo SISTEMA INICIADO!
echo ============================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo ============================
echo.
echo Pressione qualquer tecla para fechar este script
echo (Os serviços continuarao rodando nas outras janelas)
pause > nul
