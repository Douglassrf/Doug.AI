# Missão 34 – Macro Economic Servo

## Objetivo

Implementar um servo capaz de interpretar indicadores macroeconômicos (juros, inflação, payroll, CPI, decisões FOMC/BCE) e traduzi‑los em sinais de trading (BUY/SELL/HOLD) com métricas de confiança e risco adequadas.

## Implementação

1. **Servo Macro Economic** – Criado o módulo `doug_os/servos/macro_economic_servo.py` com a classe `MacroEconomicServo`.  O servo extrai indicadores do dicionário `macro_data`, aplica limiares configuráveis de inflação e juros (definidos em `SERVO_THRESHOLDS['macro_economic']`) e decide a direção: SELL quando inflação ou juros estão acima do limiar alto, BUY quando ambos estão abaixo do limiar baixo e HOLD nos casos intermediários.  Risco, confiança e demais métricas são calculados a partir das combinações de indicadores, decisões hawkish/dovish e variações de payroll/CPI.
2. **Configuração** – `config.py` recebeu limiares de inflação/juros e um peso específico na matriz de pesos dinâmicos para o servo macroeconômico.  O `ServoName` foi ampliado em `intent_vector.py` para incluir `macro_economic`.
3. **Exportação** – O servo foi exportado em `servos/__init__.py` para facilitar sua importação.
4. **Testes** – Criado `tests/test_macro_economic_servo.py` com três cenários: inflação e juros elevados (esperando SELL), baixos (BUY) e intermediários (HOLD).  Os testes verificam direção, risco e confiança ajustados corretamente pelas decisões hawkish/dovish e variações de payroll/CPI.

## Resultados

* O `MacroEconomicServo` integra indicadores macroeconômicos ao Doug.OS, permitindo que decisões considerem políticas monetárias e dados econômicos de alta relevância.
* Os testes passam sem regressões.  Limiar e pesos podem ser ajustados em `config.py` de forma centralizada.
* A combinação de risco e confiança reflete a lógica de que inflação/juros altos aumentam exposição e reduzem confiança, enquanto payroll positivo e decisões dovish reduzem risco.
