## Missão 22 – Forex Connector

* **Objetivo:** implementar um conector de dados de Forex que forneça cotações de pares cambiais em modo somente leitura.  O conector deve integrar‑se à camada de conectores criada na missão anterior.
* **Ações executadas:**
  - Criado `connectors/forex_connector.py` com a classe `ForexConnector`, que herda de `BaseDataConnector` e define o atributo `name = "forex"`.  São definidos valores estáticos para os pares **EURUSD**, **USDJPY**, **GBPUSD**, **AUDUSD**, **USDCAD** e **USDCHF**【841817473300418†L20-L30】.
  - Implementados os métodos `get_available_symbols` e `get_price`; `get_price` converte o símbolo para maiúsculas e lança `KeyError` para pares não suportados【841817473300418†L32-L39】.
  - Adicionado teste `test_forex_connector.py` verificando que o conector retorna as cotações corretas via `DataConnectorLayer` e que pares desconhecidos geram erro.
* **Resultado:** o conector de Forex funciona corretamente com a camada unificada de conectores.  Todos os testes passam e a arquitetura permanece 100% read‑only.  A etapa de integração de dados de criptomoedas é o próximo passo natural.
