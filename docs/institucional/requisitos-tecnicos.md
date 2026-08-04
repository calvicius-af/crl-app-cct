# Requisitos técnicos — Aplicação "Pipeline CCT → MaxQDA"
### Documento para o Instituto de Informática · plano de teste e implementação

## 1. Descrição
Aplicação local de apoio à análise qualitativa de convenções coletivas de
trabalho (CRL). Converte PDFs do Boletim do Trabalho e Emprego em projetos
MaxQDA (formato aberto REFI-QDA/QDPX) e ficheiros Excel, com pré-codificação
temática e comparação de versões. **Totalmente offline**: não envia dados
para o exterior, não requer serviços cloud, não abre portas de rede
(exceção opcional descrita em §5).

## 2. Plataformas-alvo
| Componente | Requisito |
|---|---|
| Sistema operativo | Windows 10/11 (principal); macOS 13+ (secundário) |
| Python | 3.11 ou superior, 64 bits, com tcl/tk (opção por omissão do instalador oficial) |
| Privilégios | utilizador normal — sem administração após instalação do Python |
| Disco | ~200 MB (Python + bibliotecas) + espaço para PDFs/resultados |
| Rede | não necessária em operação |

## 3. Bibliotecas Python (todas open-source, via pip)
| Pacote | Versão mín. | Licença | Função |
|---|---|---|---|
| pdfplumber | 0.11 | MIT | extração de texto e tabelas de PDF |
| pdfminer.six* | — | MIT | (dependência do pdfplumber) |
| Pillow* | — | MIT-CMU | (dependência do pdfplumber) |
| pypdfium2* | — | Apache-2.0/BSD | (dependência do pdfplumber) |
| openpyxl | 3.1 | MIT | leitura/escrita de Excel |
| PyYAML | 6.0 | MIT | ficheiros de configuração dos temas |
| jsonschema | 4.0 | MIT | validação dos formatos internos |
| pytest (só testes) | 8.0 | MIT | suite de testes automática |
\* instaladas automaticamente como dependências.

Interface gráfica: **tkinter** (biblioteca padrão do Python — sem instalação
adicional). Sem compiladores, sem binários externos, sem drivers.

Instalação (com acesso pip/proxy autorizado, uma única vez):
```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```
Em redes fechadas: o pip suporta instalação a partir de uma pasta local de
wheels (`pip download -r requirements.txt -d wheels/` numa máquina com
acesso; `pip install --no-index --find-links wheels/ -r requirements.txt`
na estação).

## 4. Dados e segurança
- Entradas: PDFs públicos do BTE, exports Excel/QDC do MaxQDA (dados já
  tratados pela equipa). Sem dados pessoais além dos constantes nos
  documentos públicos.
- Saídas: ficheiros locais (.qdpx, .xlsx, .txt) na pasta escolhida.
- Sem telemetria, sem atualizações automáticas, sem escrita fora das pastas
  do projeto.
- Código-fonte auditável: ~15 módulos Python (~3 000 linhas), suite com
  99 testes automáticos (`python -m pytest`).

## 5. Componente opcional — camada semântica local
Se ativada, a aplicação comunica com um servidor LLM **local**
(LM Studio, `http://127.0.0.1:1234`) na própria estação. É uma opção
desligada por omissão; a aplicação funciona integralmente sem ela.
Se o Instituto preferir, pode ser excluída do plano de implementação.

## 6. Plano de teste sugerido (estação padrão Windows)
1. Instalar Python 3.11+ 64 bits (instalador oficial, opção tcl/tk).
2. Copiar a pasta do projeto e criar o ambiente (ver §3).
3. `python -m cct.doctor` → deve terminar com "Tudo pronto".
4. `python -m pytest -q` → 99 testes, 0 falhas (≈10 s).
5. Duplo clique em `AppCCT.bat` → a janela abre; botão "Verificar
   instalação" repete o passo 3 dentro da app.
6. Corrida de fumo: pasta com 2 PDFs de teste + tema 4.08 → gera
   `projeto.qdpx` e `sugestoes_peritas.xlsx` em <1 minuto.
7. Importar o `projeto.qdpx` no MaxQDA 2022+ e confirmar a árvore de códigos.

## 7. Manutenção
- Atualizações = substituir a pasta do projeto, ou `git pull` (sem instaladores).
- Configuração dos temas = ficheiros YAML editáveis pela equipa de análise
  (sem intervenção informática).
- Logs de cada corrida em `results/<corrida>/relatorio.txt`.
