@echo off
rem Lancador da app CCT (Windows) - duplo clique para abrir
cd /d "%~dp0.."
rem PYTHONUTF8: a consola do Windows em regiao portuguesa e cp1252 e
rem nao tem os simbolos v, x e -> usados nas mensagens (ISSUE #37)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m cct.app
) else (
    python -m cct.app
)
if errorlevel 1 pause
