# Prompt para colar ao Claudio — Token API Binance DEMO (Testnet) Doug.AI

## Missão Claudio — Binance Testnet API para aprendizes Doug.AI

**Projeto:** `C:\Users\USUÁRIO\Desktop\DOUG.AI`
**Repo:** https://github.com/Douglassrf/Doug.AI
**Objetivo:** Gerar chave API na **Binance Spot Testnet** (dinheiro falso, demo) e configurar no `.env` local para treino Doug.AI / DogEye. **Sem live. Sem commit de secrets.**

---

### Regras obrigatórias

1. **Só testnet** — https://testnet.binance.vision/ (não é dinheiro real).
2. **Nunca** commitar `.env` nem colar Key/Secret no GitHub/chat.
3. `BINANCE_USE_TESTNET=true` sempre.
4. `BINANCE_LIVE_ENABLED=false` sempre.
5. Evidência: saída literal de `python scripts/test_binance_testnet.py`.

---

### Passo 1 — Ambiente

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
git pull origin master
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install websockets python-dotenv
copy .env.example .env
```

---

### Passo 2 — Criar chave DEMO na Binance Testnet (browser)

**Opção A — Testnet (recomendado para aprendizes):**

1. Abrir: https://testnet.binance.vision/
2. **Log In with GitHub** (ou Google).
3. Ir para: https://testnet.binance.vision/key/generate
4. Clicar **Generate HMAC_SHA256 Key**.
5. Copiar **API Key** + **Secret** (Secret aparece **uma vez só**).

**Opção B — Se usar formulário com nome (Binance API Management):**

- Nome (1–20 chars, único): `DougAI-Treino01`
- Marcar: **DADOS DO USUÁRIO** (+ **TROCA** se for simular ordens no testnet)
- **Não** marcar: saque, FIX_API
- Confirmar 2FA se pedir

---

### Passo 3 — Colar no `.env`

Editar `C:\Users\USUÁRIO\Desktop\DOUG.AI\.env`:

```env
BINANCE_USE_TESTNET=true
BINANCE_LIVE_ENABLED=false
BINANCE_MOCK_ENABLED=false
BINANCE_API_KEY=COLAR_API_KEY_AQUI
BINANCE_API_SECRET=COLAR_SECRET_AQUI
BINANCE_TIMEOUT_SECONDS=15
```

**Ou usar script seguro (preferido):**

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
.\scripts\paste_binance_keys.ps1
```

(Cole Key e Secret quando o PowerShell pedir — não colar no chat.)

Guia interativo:

```powershell
python scripts/setup_binance_api.py
```

---

### Passo 4 — Testar (obrigatório)

```powershell
$env:PYTHONPATH="C:\Users\USUÁRIO\Desktop\DOUG.AI"
python scripts/test_binance_testnet.py
python scripts/test_binance_testnet.py --json
```

**Passou se:** `[OK] Conectado | testnet=True` + preços (BTCUSDT, ETHUSDT, etc.).

Teste público (sem chave, fallback):

```powershell
python scripts/test_binance_testnet.py --public-only
```

---

### Passo 5 — Treino aprendizes (opcional)

```powershell
python scripts/binance_apprentice_training.py --once
python scripts/binance_apprentice_training.py --interval 120
python scripts/dogeye_continuous_training.py --coach
python scripts/dogeye_continuous_training.py --report
```

Treino contínuo (deixar rodando):

```powershell
.\run_continuous_training.ps1
```

---

### 10 pares configurados

`BTCUSDT`, `ETHUSDT`, `BNBUSDT`, `SOLUSDT`, `XRPUSDT`, `ADAUSDT`, `DOGEUSDT`, `AVAXUSDT`, `LINKUSDT`, `DOTUSDT`

---

### Entrega para Douglas

1. Print do terminal com `test_binance_testnet.py` OK.
2. Confirmar: Key/Secret **só** no `.env` local.
3. Confirmar: `testnet=True`, live desligado.
4. **Não** fazer push do `.env`.
5. (Opcional) 1 ciclo de `binance_apprentice_training.py --once` com saída JSON.

---

### Referências no repo

| Arquivo | Função |
|---------|--------|
| `docs/BINANCE_API_APRENDIZES.md` | Guia completo |
| `integrations/binance_apprentice.py` | Cliente testnet |
| `scripts/paste_binance_keys.ps1` | Cola keys no `.env` |
| `scripts/test_binance_testnet.py` | Teste conexão |
| `scripts/binance_apprentice_training.py` | Treino |
| `training/coach.py` | Professor (corrige erros) |

---

### Troubleshooting

| Problema | Solução |
|----------|---------|
| `/key/generate` → "Something bad happened" | Fazer login GitHub **na mesma aba** antes de gerar |
| Nome API rejeitado | Usar `DougAI-Treino02` (sem espaços, max 20 chars) |
| `.env` vazio após gerar | Rodar `paste_binance_keys.ps1` |
| Teste OK só `--public-only` | Key/Secret incorretos ou expirados — gerar nova |

---

**Fim da missão.** Binance testnet configurada + teste verde = concluído.
