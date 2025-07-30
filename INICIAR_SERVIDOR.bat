@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   TECNOCURSOS AI - SERVIDOR BACKEND
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/4] Instalando dependencias...
python -m pip install fastapi uvicorn python-multipart pyjwt --quiet --user
echo Dependencias instaladas.

echo.
echo [3/4] Verificando arquivo servidor...
if not exist "simple_backend.py" (
    echo ERRO: Arquivo simple_backend.py nao encontrado!
    pause
    exit /b 1
)

echo.
echo [4/4] Iniciando servidor...
echo.
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo.
echo Credenciais de teste:
echo Email: admin@tecnocursos.com
echo Senha: admin123
echo.
echo ========================================
echo Pressione Ctrl+C para parar o servidor
echo ========================================
echo.

python simple_backend.py

echo.
echo Servidor parado.
pause
