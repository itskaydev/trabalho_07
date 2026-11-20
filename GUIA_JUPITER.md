# Guia: reproduzir o modelo no Jupiter

## Modelo (`modelo/spn_servidor_web_v2.json`)
| Elemento | Tipo | Configuração |
|---|---|---|
| Vagas | lugar | marcação inicial **K** |
| Fila | lugar | marcação inicial 0 |
| Serv | lugar | marcação inicial **C** |
| Proc | lugar | marcação inicial 0 |
| T_Chegada | temporizada, exponencial, single server | atraso médio `ATRASO_CHEGADA`; Vagas → Fila |
| T_Inicio | imediata, peso 1 | Fila + Serv → Proc |
| T_Serv | temporizada, exponencial, infinite server | atraso médio `ATRASO_SERV`; Proc → Serv + Vagas |

Quando `Vagas` chega a 0, `T_Chegada` fica desabilitada: a chegada é perdida (descarte).

## Parâmetros (todos em segundos)
`C`, `K`, `ATRASO_CHEGADA` (= 1/λ), `ATRASO_SERV` = 0,1. Digite os atrasos como números.
Antes de rodar, confira os 4 valores na lista PARAMETERS.

## Métricas
`DP = P{#Vagas = 0} * 100` · `TP = E{#Proc} / ATRASO_SERV` · `U = ((C - E{#Serv}) / C) * 100` ·
`MQT`, `MPT`, `MRT` em ms (fórmulas no arquivo do modelo) · `TP_ESPERADA = (1 / ATRASO_CHEGADA) * (1 - P{#Vagas = 0})` (checagem: deve ser ≈ TP).

## Execução
Unique Simulation (estacionária) → conferir TP ≈ TP_ESPERADA → CSV e Export Report (.txt).
Referência esperada (λ=15, C=2, K=20): TP ≈ 14,99 · MRT ≈ 225 ms · U ≈ 74,9% · DP ≈ 0,09%.
