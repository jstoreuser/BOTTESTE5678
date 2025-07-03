@echo off
echo ========================================
echo   SIMPLEMMO BOT v4.0.0 - EXECUTAR
echo ========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute setup.bat primeiro.
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Executando SimpleMMO Bot...
echo.
python src\main.py

echo.
echo Bot finalizado.
pause
