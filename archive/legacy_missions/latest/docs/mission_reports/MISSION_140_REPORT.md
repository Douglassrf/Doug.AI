# Missão 140 — Intelligent Order Routing Engine

## Objetivo
Motor de roteamento inteligente de ordens com scoring multi-fator (liquidez, custo, confiabilidade, fill time) e seleção por preferência (balanced/fast/cheap/reliable).

## Módulo
`doug_os/discovery/intelligent_order_routing_engine.py`

## Classes
- `OrderRoute` — rota com exchange, scores, fill time, slippage
- `RoutingDecision` — decisão de roteamento com rota selecionada e alternativas
- `IntelligentOrderRoutingEngine` — motor principal

## Funcionalidades
- Geração de rotas por exchange com score ponderado (liq 30% + cost 30% + rel 25% + speed 15%)
- Seleção por preferência (balanced, fast, cheap, reliable)
- Confidence baseada na margem entre melhor e segunda rota
- Resumo de usage por exchange

## Testes
- **14 testes, 14 passando**

## Resultado
✅ 14/14 testes passando
