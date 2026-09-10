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
| Disco | ~200 MB na instalação base + espaço para PDFs/resultados; Docling opcional requer vários GB |
| Rede | não necessária em operação (exceção opcional em §5-A) |

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

O extrator Docling é opcional e não integra a instalação base. Inclui PyTorch e modelos
de layout/tabelas; deve ser instalado e pré-provisionado à parte quando a instituição o
aprovar. A primeira execução pode descarregar modelos, pelo que numa rede fechada estes
têm de ser preparados numa máquina autorizada e transferidos segundo a política interna.

Instalação (com acesso pip/proxy autorizado, uma única vez):
```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```
Em redes fechadas (instalação sem qualquer pedido ao proxy): o projeto traz
os dois passos automatizados — `scripts/preparar_pacote_offline.py` numa
máquina com acesso, que guarda as wheels e os respetivos SHA-256 em
`vendor/wheels/`, e `scripts/instalar_offline.bat` na estação, que instala a
partir dessa pasta com `--no-index`. Procedimento, conferência de integridade
e resolução de problemas em
[instalacao-offline.md](instalacao-offline.md).

## 4. Dados e segurança
- Entradas: PDFs públicos do BTE, exports Excel/QDC do MaxQDA (dados já
  tratados pela equipa). Sem dados pessoais além dos constantes nos
  documentos públicos.
- Saídas: ficheiros locais (.qdpx, .xlsx, .txt) na pasta escolhida.
- Sem telemetria, sem atualizações automáticas, sem escrita fora das pastas
  do projeto.
- Código-fonte auditável e suite automática (`python -m pytest`), executada no CI em
  Linux/macOS e Python 3.11/3.12.

## 5. Componente opcional — camada semântica local
Se ativada, a aplicação comunica com um servidor LLM **local** (por exemplo,
LM Studio, `http://127.0.0.1:1234`) na própria estação. É uma opção desligada por
omissão; a aplicação funciona integralmente sem ela. O código aceita apenas endereços de
loopback (`localhost`, `127.0.0.1` ou `::1`) e não contém backend para serviços externos.
Uma eventual integração interna do Instituto de Informática requer uma decisão de arquitetura
e implementação próprias. Se o Instituto preferir, a camada pode ser excluída do plano de
implementação.

## 5-A. Componente opcional — recolha automática do BTE
Se autorizada, a aplicação descarrega documentos públicos do Boletim do
Trabalho e Emprego, a partir das ligações que constam dos ficheiros-índice
fornecidos pela DGERT. Características relevantes para segurança de rede:

| Aspeto | Comportamento |
|---|---|
| Ativação | desligada por omissão; exige `--confirmar-rede` em cada corrida (na app gráfica, uma pergunta de confirmação) |
| Destinos | lista fechada: `bte.dgcp.mtsss.gov.pt`, `bte.gep.msess.gov.pt`, `bte.gep.mtsss.gov.pt`. Revalidada a cada redirecionamento |
| Protocolo | HTTPS apenas; pedidos `GET`; sem cookies, sem autenticação, sem envio de dados do CRL |
| Descoberta | nenhuma — a aplicação não navega nem infere endereços; só descarrega os URL que constam dos índices |
| Proxy | usa o proxy do sistema (`HTTPS_PROXY`) |
| Bibliotecas | `urllib` da biblioteca padrão do Python — sem dependências novas |
| Volume | ~1 MB por documento; ~14 documentos por número do boletim; pausa de 1 s entre pedidos |
| Se bloqueado | a equipa coloca os PDFs à mão numa pasta local e corre apenas a fase de nomeação, que é offline |

Decisão de arquitetura e alternativas ponderadas:
[ADR-0015](../adr/0015-recolha-em-rede-desligada-por-omissao.md).
Se o Instituto preferir, esta componente pode ser excluída do plano de
implementação sem qualquer efeito no resto da aplicação.

## 6. Plano de teste sugerido (estação padrão Windows)
1. Instalar Python 3.11+ 64 bits (instalador oficial, opção tcl/tk).
2. Copiar a pasta do projeto e criar o ambiente (ver §3).
3. `python -m cct.doctor` → deve terminar com "Tudo pronto".
4. `python -m pytest -q` → todos os testes aplicáveis passam; os que exigem corpus local
   ou Docling real identificam claramente a dependência.
5. Duplo clique em `AppCCT.bat` → a janela abre; botão "Verificar
   instalação" repete o passo 3 dentro da app.
6. Corrida de fumo: pasta com 2 PDFs de teste + tema 4.08 → gera
   `projeto.qdpx` e `sugestoes_peritas.xlsx` em <1 minuto.
7. Importar o `projeto.qdpx` no MaxQDA 2022+ e confirmar a árvore de códigos.

## 7. Manutenção
- Atualizações = substituir a pasta do projeto, ou `git pull` (sem instaladores).
- Configuração dos temas = ficheiros YAML editáveis pela equipa de análise
  (sem intervenção informática).
- Logs de cada corrida em `results/<corrida>/relatorio.txt` e proveniência verificável em
  `results/<corrida>/manifest.json`; os da recolha do BTE em `results/aquisicao/`.
