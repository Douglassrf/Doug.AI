# Fase XXII — Cognitive Trading Loop (CTL)

Esta fase transforma o plano de evolução contínua em componentes testáveis e seguros para pesquisa/paper trading:

1. **Memória Epistêmica** — registra decisões com snapshot de mercado, parâmetros e resultado.
2. **Simulação Proativa** — calcula probabilidade empírica por cenários semelhantes, sem prometer acerto fixo.
3. **Evolução Genética Controlada** — propõe mutações dentro de limites e promove apenas parâmetros validados.
4. **Supervisor de Significância** — bloqueia operação quando amostra, vantagem estatística ou risco não são suficientes.

> Segurança: esta fase não executa ordens reais. Ela produz vereditos `APPROVED`, `STANDBY` ou `PROTECTIVE_STOP` para integração com motores paper/shadow.
