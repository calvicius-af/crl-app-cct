@echo off
rem Instalacao offline da AppCCT (Windows) - duplo clique para instalar
cd /d "%~dp0.."
rem PYTHONUTF8: a consola do Windows em regiao portuguesa e cp1252 e
rem nao tem os simbolos v, x e -> usados nas mensagens (ISSUE #37)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
python scripts\instalar_offline.py
if errorlevel 1 (
    echo.
    echo A instalacao nao terminou. Ver a mensagem acima.
)
pause
