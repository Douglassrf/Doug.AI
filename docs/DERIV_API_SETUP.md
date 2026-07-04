# Deriv API — Configuração Doug.AI

Guia em duas fases: **demo agora**, conta **oficial/live depois** — sempre com travas de segurança.

---

## Fase 1 — Demo (agora)

### Opção A — Demo público (sem token)

Ideal para validar o dashboard e ticks sem criar conta API.

| Variável | Valor |
|----------|-------|
| `DOUG_MODE` | `demo` |
| `DERIV_APP_ID` | `1089` (público Deriv) |
| `DERIV_API_TOKEN` | *(vazio)* |

```powershell
copy .env.example .env
# Edite .env: DOUG_MODE=demo, DERIV_APP_ID=1089
python scripts/test_deriv_demo.py --public-only
```

### Opção B — Conta demo com token (recomendado)

Saldo virtual real, autorização completa, ainda **sem dinheiro real**.

1. Acesse [home.deriv.com](https://home.deriv.com/dashboard/home) e faça login.
2. No canto superior, selecione **Conta demo** (saldo virtual, ex.: USD 10.000).
3. Vá em **Configurações da conta** → **API token** → **Criar**.
   - Alternativa: [app.deriv.com/account/api-token](https://app.deriv.com/account/api-token)
4. Escopos: **Read** + **Trade** (somente na conta demo).
5. Copie o token para `.env`:

```env
DERIV_APP_ID=1089
DERIV_API_TOKEN=seu_token_demo_aqui
DOUG_MODE=demo
DERIV_LIVE_ENABLED=false
```

6. Teste:

```powershell
python scripts/test_deriv_demo.py
```

### Proteções automáticas (demo)

O código em `integrations/deriv_demo.py`:

- Valida `is_virtual`, prefixo `VRT*` e `account_type` demo/virtual.
- Chama `assert_demo_account()` antes de qualquer operação autenticada.
- **Bloqueia** tokens de conta real — erro `DerivNotDemoAccountError`.
- Sinais são **paper/local** — nunca envia ordens reais na Fase 1.

### Endpoint WebSocket

| Modo | URL |
|------|-----|
| Demo (público ou token virtual) | `wss://ws.derivws.com/websockets/v3?app_id=1089` |

---

## Fase 2 — Oficial / Live (depois, com portões)

> **Não habilite live trading sem passar por todos os portões abaixo.**

### Pré-requisitos obrigatórios

Antes de `DOUG_MODE=live`, o sistema exige (heurística documentada):

| Portão | Classe / artefato | Descrição |
|--------|-------------------|-----------|
| 1 | `SmallCapitalReadinessGate` | Critérios de prontidão (drawdown, win rate, expectativa) |
| 2 | `HumanSupervisedMicroLive` | Micro-live com aprovação humana e kill switch |
| 3 | Certificação GO | Veredito explícito de certificação da plataforma |

### Variáveis de ambiente (live)

```env
DOUG_MODE=live
DERIV_LIVE_ENABLED=false   # padrão — NUNCA auto-habilitar
DERIV_API_TOKEN=           # token da conta REAL (só após portões)
DERIV_APP_ID=              # seu app_id registrado em api.deriv.com
```

### Como habilitar live (manual, dupla confirmação)

1. Concluir Fase 1 com histórico estável em demo.
2. Executar `SmallCapitalReadinessGate` → veredito **GO**.
3. Completar `HumanSupervisedMicroLive` com supervisão humana.
4. Obter certificação GO documentada.
5. Definir explicitamente no `.env`:
   - `DOUG_MODE=live`
   - `DERIV_LIVE_ENABLED=true`
6. Confirmar interativamente via `DerivLiveGate.confirm_human()` (stub — implementação futura).

**O Doug.AI nunca ativa live automaticamente.** `DerivLiveGate` rejeita qualquer operação live se `DERIV_LIVE_ENABLED` não for `true` ou se os portões não estiverem satisfeitos.

### Endpoint WebSocket (live)

| Modo | URL |
|------|-----|
| Live (conta real) | `wss://ws.derivws.com/websockets/v3?app_id=<seu_app_id>` |

> Mesmo host — a separação é por **modo** (`DOUG_MODE`), **flag** (`DERIV_LIVE_ENABLED`) e **validação de conta**, não por URL diferente.

---

## Dashboard

Abra o painel **Deriv Demo** em `http://localhost:8501`:

- **Modo atual** — DEMO ou LIVE (badge no topo do painel).
- **Status do token** — configurado / ausente.
- Link para este documento.

```powershell
.\run_dashboard.ps1
```

---

## Scripts úteis

| Script | Uso |
|--------|-----|
| `scripts/test_deriv_demo.py` | Teste de conexão demo |
| `scripts/setup_deriv_api.py` | Assistente de configuração `.env` |
| `scripts/deriv_worker.py` | Refresh automático (Docker profile `deriv`) |

---

## Segurança — checklist

- [ ] `.env` está no `.gitignore` — **nunca** commitar tokens.
- [ ] `DERIV_LIVE_ENABLED=false` por padrão.
- [ ] Token demo só na conta virtual (`VRT*`).
- [ ] `audit_log.jsonl` e `deriv_status.json` são locais (não versionados).
- [ ] Live só após portões + confirmação humana explícita.

---

## Referências

- [Deriv API — documentação](https://api.deriv.com/)
- [Criar API token](https://app.deriv.com/account/api-token)
- Código: `integrations/deriv_demo.py`, `dashboard/deriv_panel.py`
