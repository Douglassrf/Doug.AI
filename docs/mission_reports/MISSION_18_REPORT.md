## Missão 18 – Servo Hardening

* **Objetivo:** eliminar avisos vazios, padronizar servos, remover valores mágicos e aumentar cobertura de testes.
* **Ações executadas:**
  - Criado o módulo `doug_os/config.py` para centralizar valores de configuração como símbolos padrão e limites de cada servo.
  - Atualizados os servos `market`, `news_psychology`, `onchain`, `evolution_research` e `risk_empire` para usar `DEFAULT_SYMBOL` e thresholds definidos em `config.py`.  Assim, valores “mágicos” foram removidos do código.
  - Ajustadas as estruturas de avisos para que tuplas de warnings sejam vazias quando nenhuma condição de alerta é disparada.
  - Implementada uma suite de testes (`tests/test_servo_hardening.py`) garantindo que os warnings não incluam strings vazias, que os servos respeitam os limites configurados e que o símbolo padrão é usado quando nenhum símbolo é fornecido.
* **Resultado:** todos os testes existentes e novos passam.  Os servos estão padronizados e prontos para a próxima missão.

