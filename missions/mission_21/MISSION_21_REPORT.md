# Missão 21 – Data Connector Layer

## Objetivo

Padronizar o acesso a dados de mercado criando uma **camada única de conectores** em modo somente leitura.  A camada deve abstrair a origem dos dados (Forex, cripto, etc.) e garantir que nenhuma funcionalidade de execução de ordens seja exposta.  Essa infraestrutura servirá de base para adicionar conectores específicos nas missões 22 e 23.

## Ações Realizadas

1. **Criação da interface de conectores.**  Implementada a classe abstrata `BaseDataConnector` no módulo `connectors/data_connector.py`.  Ela define dois métodos obrigatórios: `get_available_symbols` e `get_price`, além do atributo `name` que identifica o conector【46526513029261†L24-L40】.  Métodos de execução foram propositalmente omitidos para reforçar o modo read‑only.
2. **Implementação do registrador.**  A classe `DataConnectorLayer` mantém uma lista ordenada de conectores registrados e fornece o método `get_price` que itera sobre os conectores e retorna o preço do primeiro que suporte o símbolo pesquisado【46526513029261†L46-L82】.  Se nenhum conector suportar o símbolo, é levantado `KeyError`.
3. **Conector de preço mock.**  Foi criado o `MockPriceConnector`, uma implementação simples de `BaseDataConnector` que retorna valores fixos para símbolos previamente configurados【46526513029261†L84-L104】.  Esse conector é utilizado em testes para evitar dependências externas.
4. **Testes.**  Adicionado o arquivo `tests/test_data_connector_layer.py` com casos que verificam: (a) a camada retorna corretamente preços para símbolos suportados; (b) a precedência entre conectores respeita a ordem de registro; e (c) pedir um símbolo não suportado gera um erro.

## Resultados

* A camada de conectores foi integrada ao projeto sem impactar motores ou servos existentes.  Todos os testes – incluindo as suites das missões anteriores – continuam passando.
* A arquitetura em duas etapas (interface e registrador) permite adicionar facilmente conectores de Forex e criptomoedas nas próximas missões sem modificar a lógica central.
* A ausência de métodos de execução de ordens garante conformidade com o requisito de operar apenas em modo de leitura.

## Próximos Passos

* **Missão 22:** implementar um conector de Forex que herde de `BaseDataConnector` e forneça preços para pares cambiais (por exemplo, EURUSD, USDJPY).  Deverá utilizar a nova camada de registrador.
* **Missão 23:** implementar conectores para criptomoedas (BTC, ETH, SOL e outras), também em modo somente leitura.

---

*Relatório gerado automaticamente na conclusão da Missão 21.*