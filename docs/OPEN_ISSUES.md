# Open Issues – Após Missão 37

As questões pendentes e resolvidas após a Missão 32 são listadas a seguir.  Itens marcados como **(Resolvido)** já foram tratados nas missões anteriores.

1. **(Resolvido) Centralização completa de parâmetros:** a Missão 19 expandiu `config.py` para incluir pesos dinâmicos, limites do Risk Empire, limiares do `RegimeDetector`, critérios de bloqueio de `IntentVector` e níveis de confiança.  Agora todos os valores críticos estão centralizados.
2. **(Resolvido) Cobertura de testes para cenários extremos:** a Missão 20 criou uma suite avançada de testes que aborda manipulação severa, liquidez falsa, drawdowns e volatilidade extremos e eventos inesperados.  Essa questão está fechada.
3. **(Resolvido) Camada de conectores heterogênea:** a Missão 21 criou uma camada unificada de conectores, incluindo uma classe base e um gerenciador de conectores com comportamento somente leitura.  Conectores heterogêneos agora podem ser registrados e consultados por símbolo.
4. **(Resolvido) Implementar conectores específicos:** a camada de conectores agora possui um `ForexConnector` com cotações estáticas (Missão 22) e um `CryptoConnector` que cobre BTCUSD, ETHUSD, SOLUSD, ADAUSD e DOGEUSD (Missão 23).  Ambos são somente leitura e integrados ao `DataConnectorLayer`.
5. **(Resolvido) Memória limitada:** a Missão 24 criou a classe `ExperienceStore`, que registra contexto, regime, decisão, resultado e PnL em um banco SQLite.  O armazenamento antigo limitado foi substituído e é possível recuperar experiências similares.
6. **(Resolvido) Ausência de simulação multi‑ativo:** a Missão 26 introduziu o `MultiAssetSimulator`, que simula pares Forex, ouro, prata e criptomoedas via random walk e permite consultar preços via métodos dedicados.
7. **(Resolvido) Loop de aprendizado ausente:** a Missão 27 introduziu o `LearningLoop`, que grava experiências, calcula probabilidades e retorna métricas para ajuste; futuras versões poderão utilizá‑lo para atualizar parâmetros automaticamente.
8. **(Resolvido) Falta de inteligência on‑chain básica:** a Missão 28 adicionou o núcleo on‑chain, incluindo detectores de baleias, rastreadores de fluxo de exchange, monitoramento de stablecoins, observação de carteiras e um registro de eventos.  A camada opera em modo leitura e foi totalmente testada, fechando esta questão.
9. **(Resolvido) Detecção de padrões de baleias:** a Missão 29 criou o `WhaleMirrorEngine`, que acumula estatísticas de transações de baleias e calcula scores de influência normalizados.  Esse motor está pronto para ser aprimorado com algoritmos de padrões temporais em missões futuras.
10. **(Resolvido) Inteligência de fluxo de stablecoins:** a Missão 30 implementou o `StablecoinFlowEngine`, capaz de monitorar depósitos e retiradas de stablecoins (USDT, USDC, DAI, FDUSD), calcular fluxos líquidos e inferir pressão de compra/venda.  Esta questão está encerrada.
11. **(Resolvido) Evolução da camada de manipulação:** a Missão 31 implementou o `MarketIntegrityV2Engine`, que recebe pontuações de spoofing, armadilhas de liquidez, falsos rompimentos e wash trading, calcula uma média ponderada e classifica o risco como “dangerous”, “warning” ou “ok”.  Os testes cobrem cenários de risco alto, moderado e baixo.
12. **(Resolvido) Riscos de liquidez:** a Missão 32 implementou o `LiquidityRiskEngine`, que calcula risco de liquidez com base na profundidade do livro e no volume diário, classifica o risco em "collapse", "stress", "vacuum" ou "normal" e retorna um ajuste de confiança proporcional.
13. **(Resolvido) Inteligência de notícias e macro:** as missões 33 e 34 implementaram os servos `NewsIntelligenceServo` e `MacroEconomicServo`, que coletam, classificam e interpretam notícias e indicadores macro.  A questão está fechada.
14. **(Resolvido) Experience Probability Engine v2:** a Missão 35 entregou o `ProbabilityEngineV2` com recorrência temporal, confiança histórica e ponderação por regime, encerrando esta questão.
15. **(Resolvido) Brian Supreme:** a Missão 36 criou a camada supervisora `BrianSupremeV1` que audita decisões, detecta inconsistências e sugere ajustes.  A arquitetura está definida e a questão foi resolvida.
16. **(Resolvido) Camada de inteligência unificada:** a Missão 37 implementou a `UnifiedIntelligenceLayer`, unificando servos técnicos, on‑chain, macro, notícias e integrando memória e supervisão.  A integração está completa.

\*

Todos os itens pendentes foram resolvidos até a Missão 37.  Não há questões abertas no momento; o bloco 03 está concluído.