@echo off
echo ===============================
echo   INSTALADOR JARVIS WINDOWS
echo ===============================

echo.
echo Verificar Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado.
    echo Instala Python primeiro: https://python.org
    pause
    exit
)

echo.
echo Criar ambiente virtual...

python -m venv venv

echo.
echo Ativar ambiente virtual...

call venv\Scripts\activate

echo.
echo Instalar dependencias...

pip install --upgrade pip

pip install -r requirements.txt

echo.
echo ===============================
echo INSTALACAO CONCLUIDA
echo ===============================

echo.
echo Para iniciar o Jarvis:
echo python main.py

pause