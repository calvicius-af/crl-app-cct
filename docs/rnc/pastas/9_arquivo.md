# `9_arquivo/` — o que foi substituído

## O que vive aqui
Versões superadas de tudo o resto, e os `.mqex` já integrados no master.

Esta pasta existe para que a regra «uma versão ativa por documento» tenha para
onde mandar as outras. Sem ela, as versões antigas ficam na pasta de trabalho e,
mais cedo ou mais tarde, alguém abre a errada.

## O que não vive aqui
O que está em uso. E o que se pode regerar: `2_processamento/` reconstrói-se
correndo o pipeline outra vez sobre os mesmos PDF com o mesmo *commit*, pelo que
não se arquiva — arquiva-se o `manifest.json` da corrida.

## Como se chamam os ficheiros
Espelha-se a árvore de origem e acrescenta-se a data ao nome:

```text
9_arquivo/
├── 0_gestao/vocabularios/temas_20260901.csv
├── 3_analise/mqex/2026_C9-SALARIOS_AF_20270315.mqex
└── 5_redacao/4_07_remuneracoes_20270312.docx
```

A data é a da substituição, não a da criação. Um `.mqex` integrado mantém o nome
que tinha — já tem data, e é a data que interessa.

## Quem escreve e quem lê
Escreve quem substitui alguma coisa, no momento em que a substitui. Não é uma
arrumação que se faz no fim: adiar é o que produz pastas com três versões do
mesmo ficheiro e nenhuma indicação de qual é a boa.

## Quando sai daqui
Não sai. Retira-se dela uma cópia, quando é preciso recuperar alguma coisa —
mas o ficheiro arquivado fica onde está. No fecho do ciclo, `9_arquivo/`
acompanha a pasta-raiz `RNC_Dados_AAAA/` para o arquivo de longo prazo, inteira.

**Limpar antes de arquivar:** `Thumbs.db`, `.DS_Store`, `~$*.docx`, atalhos
`.url`. São ficheiros que o sistema operativo cria e que, ao fim de alguns anos,
são metade das entradas de um arquivo.
