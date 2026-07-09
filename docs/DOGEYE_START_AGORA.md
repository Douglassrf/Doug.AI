# 🚨 DOGEYE — COMEÇAR AGORA (Douglas está assistindo)

**Copiem e coloquem no grupo. Executem nos próximos 5 minutos.**

---

## Douglas quer ver AO VIVO

Abram **2 terminais** na pasta Doug.AI:

### Terminal 1 — Monitor (deixem aberto)

```powershell
cd C:\Users\SEU_USUARIO\Desktop\DOUG.AI
.\.venv\Scripts\Activate.ps1
.\run_live_ttt.ps1
```

Abrir no browser: **http://localhost:8502**  
(Se Douglas estiver em AnyDesk/TeamViewer na sua máquina, ele vê essa tela.)

### Terminal 2 — Teste (1000 ops)

```powershell
cd C:\Users\SEU_USUARIO\Desktop\DOUG.AI
.\.venv\Scripts\Activate.ps1
python scripts/tip_to_tip_preflight.py
python scripts/tip_to_tip_training.py --certify --operator "SEU_NOME" --live
```

Troquem `SEU_NOME` pelo nome real. **Sem agente. Sem Cursor.**

---

## O que Douglas vê

- Barra de progresso 0 → 1000
- Acertos e perdas em tempo real
- Cada operação: missão + par + OK/FAIL

---

## Se der erro

1. `pip install -r requirements.txt websockets python-dotenv streamlit`
2. `copy .env.example .env`
3. Preflight 100% OK antes do `--live`

---

## Quando terminar

Mandem print final + JSON de `data/certificates/` para o Douglas.

**COMECEM AGORA.**
