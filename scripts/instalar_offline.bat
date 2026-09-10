@echo off
rem Instalacao offline da AppCCT (Windows) - duplo clique para instalar
cd /d "%~dp0.."
python scripts\instalar_offline.py
if errorlevel 1 (
    echo.
    echo A instalacao nao terminou. Ver a mensagem acima.
)
pause
