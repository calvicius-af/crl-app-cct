#!/bin/bash
# Lançador da app CCT (macOS) — duplo clique para abrir
#
# Se a app não abrir, esta janela fica aberta com a razão: antes fechava-se e
# levava o erro com ela (corrida de 2025 em macOS). O mesmo texto fica em
# results/app_erro.log, para enviar.
cd "$(dirname "$0")/.." || exit 1
if [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"; else PY="python3"; fi
echo "Python: $("$PY" -c 'import sys; print(sys.version.split()[0], sys.executable)' 2>&1)"

mkdir -p results
set -o pipefail
"$PY" -m cct.app 2>&1 | tee results/app_erro.log
codigo=$?
if [ "$codigo" -eq 0 ]; then
    rm -f results/app_erro.log
    exit 0
fi
echo
if [ "$codigo" -ge 128 ]; then
    # 134 (abort) e 139 (segmentation fault) vêm do Tk, não da app
    echo "O Python terminou de repente (código $codigo): o Tk deste Python pode não"
    echo "funcionar nesta versão do macOS. Instalar o Python de python.org e refazer"
    echo "o .venv com scripts/instalar_offline.command."
fi
echo "A app terminou com o código $codigo. O pipeline continua a funcionar no"
echo "terminal. Para diagnosticar: $PY -m cct.doctor"
echo "Registo: results/app_erro.log"
echo
read -r -p "Carregar em Enter para fechar esta janela. " _
exit "$codigo"
