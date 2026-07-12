# Fase XVIII — Quantum Trading Intelligence (Missões 278-287)

Scripts corrigidos a partir do código colado por Douglas, salvos em Doug.AI.

## Estrutura

```
fase_xviii_quantum_trading_intelligence/
├── missions/
│   ├── mission_278_market_dna_engine.py              (completo, corrigido)
│   ├── mission_279_institutional_intention_detector.py (completo, corrigido)
│   ├── mission_280_adaptive_alpha_laboratory.py      (completo, bug combine corrigido)
│   ├── mission_281_capital_preservation_ai.py        (completo, corrigido)
│   ├── mission_282_precision_entry_engine.py         (completado)
│   ├── mission_283_precision_exit_engine.py          (stub)
│   ├── mission_284_quantum_trade_orchestrator.py     (stub)
│   ├── mission_285_adaptive_position_sizer.py        (stub)
│   ├── mission_286_quantum_risk_fusion_engine.py     (stub)
│   └── mission_287_quantum_trading_intelligence_hub.py (stub)
├── tests/
│   └── test_missions_278_287.py
├── requirements.txt
└── README.md
```

## Correções aplicadas

- Missão 280: `_apply_mutation` combine comparava `a.id != formula` (str) — corrigido para `a.id != parent_id`
- Missão 280: `random` substituído por helpers determinísticos (`hashlib`) para mutações reproduzíveis
- Missão 282: `PrecisionEntryEngine` completado (evaluate_entry, simulate_entry, dashboard)
- Missão 282: `_decisions: List[EntryDecision] = []` (não `{}`)
- Stubs mínimos para Missões 283-287 (não coladas no chat)

## Testes

```bash
cd fase_xviii_quantum_trading_intelligence
pip install -r requirements.txt
pytest tests/test_missions_278_287.py -q
```

Modo shadow — não conecta a exchanges reais.
