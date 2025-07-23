@echo off
echo 🚀 TecnoCursos AI - Abrindo Sistema no Navegador
echo ================================================
echo.
echo ✅ O sistema está funcionando na porta 8001
echo 🌐 Abrindo URLs principais...
echo.

REM Abrir documentação da API
start "" http://localhost:8001/docs

REM Aguardar 2 segundos
timeout /t 2 /nobreak >nul

REM Abrir health check
start "" http://localhost:8001/api/health

echo ✅ Navegador aberto com as URLs funcionais!
echo.
echo 📋 URLs Principais:
echo    🏠 Home: http://localhost:8001/
echo    📚 Docs: http://localhost:8001/docs
echo    ❤️ Health: http://localhost:8001/api/health
echo    🎬 Export: http://localhost:8001/api/video/export/formats
echo    🎤 TTS: http://localhost:8001/api/tts/voices
echo    🎭 Avatar: http://localhost:8001/api/avatar/styles
echo.
echo 💡 Dica: Use a porta 8001 em vez de 8000!
echo.
pause 