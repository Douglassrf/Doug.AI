# Binance API — Aprendizes Doug.AI / Guiai

> **Douglas:** o agente **nao** entra na sua Binance. Cada aprendiz cria chave **testnet** (dinheiro falso). Chaves ficam so no `.env` local.

---

## Por que Testnet e nao conta real?

| | Testnet | Conta real |
|---|---------|------------|
| Dinheiro | Falso (gratis) | Real |
| Risco | Zero | Alto |
| Quem cria | Cada aprendiz | So Douglas, depois |
| URL | [testnet.binance.vision](https://testnet.binance.vision/) | [binance.com dashboard](https://www.binance.com/pt-BR/my/dashboard) |

---

## Passo a passo — cada aprendiz (5 min)

### 1. Criar chave testnet

1. Abra **https://testnet.binance.vision/**
2. Login (GitHub ou Google)
3. **Generate HMAC_SHA256 Key**
4. Copie **API Key** + **Secret** (secret so aparece uma vez)

### 2. Configurar Doug.AI

```powershell
cd Desktop\DOUG.AI
copy .env.example .env
notepad .env
```

```env
BINANCE_USE_TESTNET=true
BINANCE_LIVE_ENABLED=false
BINANCE_MOCK_ENABLED=false
BINANCE_API_KEY=sua_key_aqui
BINANCE_API_SECRET=seu_secret_aqui
```

### 3. Testar

```powershell
python scripts/setup_binance_api.py
python scripts/test_binance_testnet.py
python scripts/test_binance_testnet.py --public-only
```

### 4. Treinar

```powershell
python scripts/binance_apprentice_training.py --once
python scripts/binance_apprentice_training.py --interval 120
python scripts/dogeye_continuous_training.py --coach
```

---

## 10 pares para aprendizes

`BTCUSDT`, `ETHUSDT`, `BNBUSDT`, `SOLUSDT`, `XRPUSDT`, `ADAUSDT`, `DOGEUSDT`, `AVAXUSDT`, `LINKUSDT`, `DOTUSDT`

---

## Conta real Binance (futuro — so Douglas)

1. [Dashboard Binance](https://www.binance.com/pt-BR/my/dashboard)
2. [Gestao API](https://www.binance.com/pt-BR/my/settings/api-management)
3. Criar API com **somente Leitura** para treino inicial
4. **Nunca** habilitar saque
5. No `.env`: `BINANCE_USE_TESTNET=false` + `BINANCE_LIVE_ENABLED=false` ate certificacao O10

---

## Regras de seguranca

1. **Nunca** commitar `.env` ou mandar secret no chat
2. Uma chave **por aprendiz** (testnet)
3. Professor (`--coach`) corrige erros — obedeçam
4. Meta: evoluir niveis Aprendiz → Mestre antes de pensar em live

---

## Arquivos

| Arquivo | Funcao |
|---------|--------|
| `integrations/binance_apprentice.py` | Cliente seguro testnet |
| `scripts/setup_binance_api.py` | Guia interativo |
| `scripts/test_binance_testnet.py` | Teste conexao |
| `scripts/binance_apprentice_training.py` | Treino Binance + professor |
| `data/training/binance_apprentice.jsonl` | Log de treinos |

**Preparem-se para serem fera — com disciplina, testnet e professor.**
