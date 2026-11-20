# Trabalho 07 – Modelagem e Avaliação de Desempenho de um Servidor Web com SPN

Modelo SPN (Jupiter) de um servidor web M/M/c/K: `c` servidores em paralelo, fila compartilhada e capacidade total `K`.
Quem chega com o sistema cheio é descartado.

## Conteúdo
| Caminho | Descrição |
|---|---|
| `modelo/spn_servidor_web_v2.json` | Modelo SPN para importação no Jupiter (configurações de lugares, transições e parâmetros) |
| `jupiter_execucoes/execucaoN/` | CSVs de métricas e relatórios (.txt) exportados pelo Jupiter em cada uma das 13 execuções |
| `resultados_jupiter.csv` | Consolidado das execuções do Jupiter (valor e IC 95% de cada métrica) |
| `resultados_analitico.csv` | Solução analítica da CTMC M/M/c/K, utilizada para validação dos resultados |
| `comparacao_jupiter_analitico.csv` | Comparativo quantitativo entre o Jupiter e o modelo analítico |
| `gerar_resultados.py` | Script Python que processa os resultados brutos do Jupiter e gera os consolidados e gráficos |
| `spn_web.py` | Script com a modelagem e solução analítica CTMC M/M/c/K |
| `GUIA_JUPITER.md` | Guia com instruções detalhadas para importar e executar o modelo no Jupiter |

## Parâmetros
Serviço: `ATRASO_SERV = 0,1 s` (μ = 10 req/s por servidor). Referência: λ = 15 req/s (`ATRASO_CHEGADA = 0,0666666667 s`), `C = 2`, `K = 20`.
Os atrasos são informados como números (o Jupiter não avaliou a expressão `1/LAMBDA`).

| Execução | Experimento | λ (req/s) | C | K |
|---|---|---|---|---|
| 1 | Referência | 15 | 2 | 20 |
| 2, 3, 4, 5 | E1 | 5, 10, 20, 30 | 2 | 20 |
| 6, 7 | E2 | 15 | 1, 4 | 20 |
| 8, 9, 10 | E3 | 15 | 2 | 5, 10, 40 |
| 11, 12 (e 4) | E4 | (10,1,10), (40,4,40) e (20,2,20) | | |
| 13 | Extra | 30 | 4 | 20 |

## Como reproduzir
1. Importe `modelo/spn_servidor_web_v2.json` no Jupiter.
2. Para cada linha da tabela, ajuste `ATRASO_CHEGADA` (= 1/λ), `C` e `K`, rode **Unique Simulation** (simulação estacionária) e exporte o CSV e o relatório.
3. Coloque os arquivos em `jupiter_execucoes/execucaoN/` e rode `pip install numpy pandas matplotlib && python gerar_resultados.py`.
4. (Opcional) `python spn_web.py` recalcula a solução analítica.

## Resultados
Simulação estacionária do Jupiter, 32 a 250 repetições por execução, IC de 95%. Diferença máxima para o analítico: 0,35% (TP, U), 0,96% (MRT), 0,25 p.p. (DP).
