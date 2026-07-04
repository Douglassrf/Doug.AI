# Missão 23 – Crypto Connector

## Contexto

Nas missões anteriores foi implementada uma **camada unificada de conectores** de dados (Missão 21) e um **ForexConnector** fornecendo cotações estáticas de pares cambiais (Missão 22).  A próxima etapa no roteiro era estender essa infraestrutura para o universo de criptomoedas, de modo que o núcleo Doug.OS possa consultar cotações de BTC, ETH, SOL e outros ativos digitais sem acoplar‑se a APIs externas ou executar ordens reais.

## Implementação

### Novo módulo `crypto_connector.py`

Foi criado o arquivo [`connectors/crypto_connector.py`](doug_os/connectors/crypto_connector.py) contendo a classe `CryptoConnector`.  Esta classe herda de `BaseDataConnector` e define um dicionário de preços estáticos (`_prices`) para os pares **BTCUSD**, **ETHUSD**, **SOLUSD**, **ADAUSD** e **DOGEUSD**.  Os símbolos são tratados de maneira case‑insensível e o método `get_available_symbols()` retorna a lista de ativos disponíveis.  Chamadas a `get_price()` com símbolos não suportados levantam `KeyError`.  Desta forma, o conector permanece 100 % read‑only e isolado de qualquer API externa.

```python
class CryptoConnector(BaseDataConnector):
    name = "crypto"
    _prices = {
        "BTCUSD": 50_000.0,
        "ETHUSD": 3_000.0,
        "SOLUSD": 100.0,
        "ADAUSD": 0.50,
        "DOGEUSD": 0.06,
    }
    def get_available_symbols(self) -> list[str]:
        return list(self._prices.keys())
    def get_price(self, symbol: str) -> float:
        normalized = symbol.upper()
        if normalized in self._prices:
            return self._prices[normalized]
        raise KeyError(f"Symbol {symbol} not supported")
```

O código acima (parcial) demonstra como o conector expõe símbolos disponíveis e preços, normalizando a entrada para maiúsculas e gerando exceção quando necessário.

### Ajuste no `DataConnectorLayer`

Durante a implementação do conector de criptomoedas notou‑se que o método `get_price` da
`DataConnectorLayer` fazia uma verificação direta de pertencimento do símbolo
(`symbol in connector.get_available_symbols()`), o que tornava as consultas
sensíveis a caixa.  Para suportar símbolos em qualquer capitalização e
permitir que cada conector execute sua própria normalização, o método foi
refatorado para delegar a busca diretamente ao conector e capturar
`KeyError` quando o símbolo não é suportado.  O laço percorre todos os
conectores registrados e retorna o preço assim que o primeiro conector
responde.  Caso nenhum conector forneça o símbolo, um `KeyError` é
levantado【281797822982574†L68-L96】.

### Testes

O arquivo `tests/test_crypto_connector.py` contém três testes principais:

1. **`test_crypto_connector_prices`** – garante que o `CryptoConnector` retorna os preços esperados para cada símbolo suportado (BTCUSD=50 000, ETHUSD=3 000, SOLUSD=100 etc.) e que o conector ignora diferenças de capitalização.
2. **`test_crypto_connector_unknown_symbol`** – verifica que uma solicitação de símbolo inexistente (ex.: `XYZUSD`) lança `KeyError`.
3. **`test_connector_precedence`** – verifica que, quando mais de um conector está registrado no `DataConnectorLayer` para o mesmo símbolo, prevalece o primeiro da lista.  Um conector parcial retornando BTC a 60 000 foi registrado antes do `CryptoConnector` padrão, e os testes confirmam que a cotação do BTC foi 60 000 enquanto os demais ativos foram obtidos do conector padrão.

### Atualizações de documentação

* **`MISSION_HISTORY.md`** – adicionou‑se uma seção descrevendo a Missão 23, detalhando o objetivo, as ações tomadas e os resultados obtidos.
* **`CURRENT_STATE.md`** – a seção “Camada de Conectores” foi atualizada para mencionar o novo `CryptoConnector` e as criptos suportadas.
* **`ROADMAP.md`** – o item correspondente à Missão 23 foi marcado como **Concluído**, assim como o da Missão 22; as próximas missões permanecem em aberto.
* **`OPEN_ISSUES.md`** – a questão “Implementar conectores específicos” foi marcada como resolvida, pois agora existem conectores de Forex e de criptomoedas.

## Resultado

Com a adição do `CryptoConnector`, o Doug.OS agora possui uma **camada de dados unificada** capaz de fornecer cotações tanto de Forex quanto de criptomoedas em modo somente leitura.  Os testes confirmam que as cotações retornadas são consistentes e que o comportamento de precedência entre múltiplos conectores funciona corretamente.  Isso encerra a etapa de integração de dados de mercados financeiros e abre espaço para focar em memória de mercado e aprendizado nas missões seguintes.
