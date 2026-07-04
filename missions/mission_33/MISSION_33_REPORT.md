# Missão 33 – News Intelligence Servo

## Objetivo

Criar um servo especializado em notícias capaz de coletar manchetes, classificá‑las quanto ao sentimento, avaliar o impacto e atribuir um score de confiança à fonte, transformando o fluxo noticioso em um sinal quantitativo para o Doug.OS.

## Implementação

1. **Servo News Intelligence** – Foi criado o módulo `doug_os/servos/news_intelligence_servo.py` implementando a classe `NewsIntelligenceServo`.  O servo aceita uma lista de itens de notícia contendo `sentiment_score`, `impact_score` e `source_confidence` e calcula médias para cada métrica.  A direção (BUY, SELL ou HOLD) é determinada comparando o sentimento médio com limiares configuráveis (`sentiment_buy_threshold` e `sentiment_sell_threshold`), definidos em `config.py`.  O servo gera um `IntentVector` com os campos padrão e calcula métricas auxiliares como risco, evidência, risco de manipulação, entropia, realidade e oportunidade.
2. **Configuração** – O `config.py` foi estendido com a seção `SERVO_THRESHOLDS['news_intelligence']` para definir limiares de compra e venda, e os pesos dinâmicos foram ajustados para incluir o novo servo.
3. **Exportação e Tipagem** – O arquivo `servos/__init__.py` passou a exportar o `NewsIntelligenceServo`; a tipagem de `ServoName` em `intent_vector.py` foi atualizada para incluir `news_intelligence`.
4. **Testes** – Foi criado o teste `tests/test_news_intelligence_servo.py` que cobre quatro cenários: (a) notícias positivas resultando em BUY, (b) notícias negativas resultando em SELL, (c) notícias neutras resultando em HOLD e (d) ausência de notícias retornando um vetor neutro.  Asserções verificam direção, confiança, risco, evidência e razões.

## Resultados

* Todos os testes existentes e o novo teste passam sem regressões.  O servo se integra aos demais módulos via `DougBus` e `Intelligence Council`.
* A implementação permite ajustar os limiares de sensibilidade em `config.py` sem modificar o código do servo.
* O `NewsIntelligenceServo` adiciona uma importante dimensão qualitativa ao Doug.OS, permitindo incorporar sentimento noticioso de forma auditável.
