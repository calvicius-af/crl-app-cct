# ISSUE-0014: quatro documentos CARRISTUR produzem zero cláusulas

- **Estado:** Aberta
- **Data:** 2026-09-17
- **GitHub:** #64 (sub-issue de #24)
- **Onde dói:** extração e validação (`cct/extractor*.py`, deteção da nota de depósito)

## O que acontece

Na corrida de 2026-09-17, sobre 14 convenções do BTE 31 de 2026, quatro documentos deram
zero cláusulas:

```
[11/14] 26_PR_011_BTE_31_CARRISTUR_ASPTC: 0 cláusulas, 1 anotações
[12/14] 26_PR_012_BTE_31_CARRISTUR_FECTRANS: 0 cláusulas, 1 anotações
[13/14] 26_PR_013_BTE_31_CARRISTUR_SITRA: 0 cláusulas, 1 anotações
[14/14] 26_PR_014_BTE_31_CARRISTUR_Motoristas: 0 cláusulas, 1 anotações
```

Os mesmos quatro, e só esses, sinalizam no relatório:

```
sem nota de depósito (art. 494.º CT) — documento truncado?
```

São ficheiros de tamanho normal, entre 846 421 e 846 501 bytes, e com hashes distintos,
pelo que não são cópias um do outro. Os quatro têm a CARRISTUR como parte patronal e
diferem no sindicato.

## Hipóteses, por ordem de probabilidade

Nenhuma verificada. É preciso abrir os PDFs, que não estão disponíveis neste ambiente.

1. **São acordos de adesão ou revisões curtas**, sem articulado próprio, que remetem para
   uma convenção anterior. Nesse caso zero cláusulas é o resultado *correto*, e o defeito
   está em o relatarmos como problema e em sugerir truncagem.
2. **A estrutura destes documentos não é reconhecida** pelo extrator, por os cabeçalhos
   não seguirem o padrão esperado.
3. **Os PDFs estão mesmo truncados** na origem, e o sinal da nota de depósito está certo.

A coincidência dos quatro terem o mesmo tamanho aproximado e a mesma parte patronal aponta
para a hipótese 1: documentos do mesmo tipo, publicados juntos.

## O que devia acontecer

Depende da hipótese que se confirmar. Se for a 1, o sistema deve reconhecer esta família
documental e dizer *documento sem articulado próprio (adesão ou revisão)* em vez de
*truncado?*, que envia quem lê para a pista errada.

Uma extração que devolve zero cláusulas nunca deve ficar ambígua entre "não há nada para
extrair" e "não consegui extrair".

## Como reproduzir

```bash
python -m cct.pipeline_tema \
  --pdfs data/raw/bte/bte_2026 \
  --codebook codebooks/4_08_protecao_dados.yaml \
  --out results/corrida
```

## Notas

Dois outros documentos da mesma corrida sinalizaram `Artigo 1.º: corpo sem frase terminada
em ponto` (26_PR_008 e 26_PR_009). É outro sintoma e provavelmente outra causa; fica aqui
registado para não se perder, e deve sair para issue próprio se se confirmar que não tem
relação com este.

Sem relação com a instalação. Registado a partir do mesmo gate apenas porque foi aí que
apareceu — ver [o registo do gate](../docs/validacao/instalacao-estacao-crl-2026-09-17.md).
