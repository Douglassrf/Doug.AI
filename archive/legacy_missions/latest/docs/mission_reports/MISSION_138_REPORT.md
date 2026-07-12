# Missão 138 — Multi-Timeframe Consensus Engine

## Objetivo
Motor de consenso que agrega sinais de 10 timeframes (TICK→Monthly) com votação ponderada por regime, detecção de divergências e geração de recomendações.

## Módulo
`doug_os/discovery/multi_timeframe_consensus_engine.py`

## Classes
- `Timeframe` — enum com 10 horizontes temporais
- `SignalType` — BUY / SELL / NEUTRAL / STRONG_BUY / STRONG_SELL
- `TimeframeSignal` — sinal de um timeframe com strength e confidence
- `ConsensusResult` — resultado do consenso com votos, pesos, divergências
- `MultiTimeframeConsensusEngine` — motor principal

## Funcionalidades
- Pesos dinâmicos por regime (trending_bull/bear, ranging, high_volatility, crisis)
- Detecção de divergências entre sinais opostos (BUY vs SELL)
- consensus_score = 1 - (divergências / total sinais)
- Cap de 100 sinais por timeframe (sliding window)

## Testes
- **12 testes, 12 passando**

## Resultado
✅ 12/12 testes passando
