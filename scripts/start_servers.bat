@echo off
echo Iniciando TecnoCursos AI...
echo.

echo Iniciando servidor backend na porta 8000...
start "Backend Server" python simple_server.py

echo Aguardando 5 segundos...
timeout /t 5 /nobreak > nul

echo Iniciando servidor frontend na porta 3000...
start "Frontend Server" cmd /k "set PORT=3000 && npm start"

echo.
echo Servidores iniciados!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause 