@echo off
rem Lancador da app CCT (Windows) - duplo clique para abrir
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m cct.app
) else (
    python -m cct.app
)
if errorlevel 1 pause
