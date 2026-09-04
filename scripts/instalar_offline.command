#!/bin/bash
# Instalação offline da AppCCT (macOS) — duplo clique para instalar
cd "$(dirname "$0")/.."
python3 scripts/instalar_offline.py
echo
read -n 1 -s -r -p "Carregar em qualquer tecla para fechar."
