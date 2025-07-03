@echo off
echo ========================================
echo   SIMPLEMMO BOT v4.0.0 - SETUP
echo ========================================
echo.

echo 1. Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ❌ Erro ao criar ambiente virtual
    pause
    exit /b 1
)

echo ✅ Ambiente virtual criado com sucesso!
echo.

echo 2. Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo 3. Atualizando pip...
python -m pip install --upgrade pip

echo 4. Instalando dependências...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo ✅ Dependências instaladas com sucesso!
echo.

echo 5. Verificando instalação...
python -c "import selenium; print('✅ Selenium OK')"
python -c "import tkinter; print('✅ Tkinter OK')"
python -c "import requests; print('✅ Requests OK')"

echo.
echo ========================================
echo   SETUP CONCLUÍDO COM SUCESSO! 🎉
echo ========================================
echo.
echo Para executar o bot:
echo   1. call venv\Scripts\activate.bat
echo   2. python src\main.py
echo.
echo Ou use o VS Code:
echo   Ctrl+Shift+P → Tasks: Run Task → 🚀 Run SimpleMMO Bot
echo.
pause
