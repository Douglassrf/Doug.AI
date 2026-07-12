# Missão 30 – Stablecoin Flow Intelligence

## Objetivo

A missão 30 teve como foco aprimorar o monitoramento de stablecoins iniciado no núcleo on‑chain.  O objetivo foi analisar **fluxos de entrada e saída** de stablecoins (USDT, USDC, DAI e FDUSD) nas exchanges e inferir se há **pressão de compra ou venda**.  Diferentemente do `StablecoinTracker` básico, que apenas soma depósitos e retiradas, este motor calcula o **saldo líquido** e classifica a pressão de mercado.

## Implementação

* **Módulo `doug_os/onchain/stablecoin_flow_engine.py`** – Foi criada a classe `StablecoinFlowEngine`, que recebe três parâmetros na construção: a lista de stablecoins a monitorar, um conjunto de endereços de exchanges e um `pressure_threshold` (padrão 0,55).  Ao processar uma lista de transações (dicionários contendo `symbol`, `sender`, `receiver` e `amount`), o motor determina se a transferência representa um **depósito** (usuário → exchange) ou uma **retirada** (exchange → usuário).  Cada stablecoin monitora separadamente os totais depositados e retirados.
* **Fluxos e pressão:** O método `net_flows()` retorna para cada moeda o saldo líquido de depósitos menos retiradas.  Já o método `pressure()` calcula a razão entre depósitos e o total de transações (depósitos + retiradas).  Se a razão excede `pressure_threshold`, considera‑se **pressão de compra** (“buy”); se for menor que `1 − pressure_threshold`, considera‑se **pressão de venda** (“sell”); caso contrário, a pressão é **neutra**.  O método `reset()` permite limpar os contadores para uma nova janela de análise.
* **Exposição pública:** O pacote `doug_os/onchain/__init__.py` foi atualizado para exportar o `StablecoinFlowEngine`, permitindo sua importação direta via `from doug_os.onchain import StablecoinFlowEngine`.

## Testes

* Foi criada a suite **`tests/test_stablecoin_flow_engine.py`**.  O teste principal instanciará o `StablecoinFlowEngine` com USDT e USDC, definirá um limiar de 0,6 e injetará transações em duas rodadas.  Na primeira, o volume de depósitos para USDT excede o de retiradas, resultando em **pressão de compra**; para USDC, depósitos e retiradas se equilibram, gerando **pressão neutra**.  Na segunda rodada, um grande saque de USDC causa **pressão de venda**.  O teste verifica os valores de `net_flows()` e os rótulos retornados por `pressure()`.
* Todos os testes existentes (das missões anteriores) foram executados com sucesso.  A introdução do novo engine não quebrou a funcionalidade do `StablecoinTracker` nem do núcleo on‑chain.

## Atualização da Memória

A documentação interna foi atualizada para refletir esta missão:

* **`CURRENT_STATE.md`** – O título foi alterado para “após Missão 30” e foi incluído um novo subtítulo **Stablecoin Flow Intelligence** que descreve o funcionamento do `StablecoinFlowEngine`.  A lista de “Próximos Passos” foi atualizada para apontar às missões 31 a 37.
* **`MISSION_HISTORY.md`** – Foi adicionada uma seção detalhando as ações executadas na Missão 30, incluindo o novo módulo, os métodos implementados, os testes criados e o resultado.
* **`ROADMAP.md`** – A linha correspondente à Missão 30 foi marcada como **Concluída**, explicando que o Stablecoin Flow Engine monitora depósitos e retiradas e infere pressão de compra/venda.
* **`OPEN_ISSUES.md`** – A questão “Inteligência de fluxo de stablecoins” foi marcada como **Resolvida**, registrando que a Missão 30 atendeu ao requisito.

## Resultado

Com a Missão 30 concluída, o Doug.OS ganhou a capacidade de identificar movimentos de stablecoins em exchanges e derivar um sinal de pressão de compra ou venda.  Esse motor complementa a camada on‑chain, fornecendo ao conselho de inteligência dados adicionais para interpretar a dinâmica do mercado.  A estrutura permanece 100 % em modo leitura e segura, respeitando as diretrizes do projeto.  Todos os testes (31 no total) continuam passando e a cobertura global de código se mantém elevada.