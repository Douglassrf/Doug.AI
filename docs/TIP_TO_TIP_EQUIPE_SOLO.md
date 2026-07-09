# DogEye — Teste Tip-to-Tip SOLO (sem agente)

> **Para Douglas:** repasse este arquivo à equipe. Eles rodam sozinhos. Você valida pelo JSON + print do terminal.

---

## Regra de ouro

**Durante o teste, ninguém usa Cursor, ChatGPT ou agente.**  
Se precisarem de ajuda, **param**, corrigem o ambiente e **recomeçam do zero**.  
O objetivo é provar que sabem operar Doug.AI **sem IA ao lado**.

---

## O que vocês vão fazer

| Item | Valor |
|------|-------|
| Operações totais | **1000** |
| Formato | 10 missões × 10 pares × 10 repetições |
| Tempo estimado | 10–25 minutos (depende da rede) |
| Aprovação | **≥ 95%** (950+ acertos) e nota **A ou B** |
| Modo | Demo público Deriv (`DOUG_MODE=demo`, sem token obrigatório) |

**Não é trading real.** É prova de que vocês conseguem: clonar repo, configurar `.env`, passar preflight, rodar o benchmark e entregar evidência.

---

## Passo 0 — Clone o repositório (se ainda não tiver)

```powershell
cd $env:USERPROFILE\Desktop
git clone https://github.com/Douglassrf/Doug.AI.git
cd Doug.AI
git pull origin master
```

Confirme que está na pasta certa:

```powershell
dir scripts\tip_to_tip_training.py
```

Se o arquivo não existir, o repo está incompleto ou na pasta errada.

---

## Passo 1 — Ambiente Python (vocês fazem)

```powershell
cd C:\Users\SEU_USUARIO\Desktop\DOUG.AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install websockets python-dotenv
```

**Check:** `python --version` deve ser **3.10 ou superior**.

---

## Passo 2 — Configurar `.env` (sem token no GitHub)

```powershell
copy .env.example .env
notepad .env
```

Confirme estas linhas (não inventem outras):

```env
DERIV_APP_ID=1089
DERIV_API_TOKEN=
DOUG_MODE=demo
DERIV_LIVE_ENABLED=false
DERIV_MOCK_ENABLED=true
```

- **Token:** pode ficar vazio para este teste.
- **Nunca** commitem `.env` nem mandem token no WhatsApp/Discord.

---

## Passo 3 — Preflight obrigatório

```powershell
python scripts/tip_to_tip_preflight.py
```

**Todos os itens devem mostrar `[OK]`.**  
Se aparecer `[FAIL]`:

| FAIL comum | O que fazer (sozinhos) |
|------------|-------------------------|
| `.env existe` | `copy .env.example .env` |
| `pacote websockets` | `pip install websockets` |
| `DOUG_MODE=demo` | Edite `.env` e salve |
| `test_deriv_demo public` | Verifique internet; firewall; tente de novo em 1 min |
| `DerivBridge` | Confirme `git pull` e pasta `integrations/` |

**Só avance quando preflight = 100% OK.**

---

## Passo 4 — Certificação (teste completo)

Substitua `SEU_NOME` pelo nome real (ex.: `Maria`, `Joao_Silva`):

```powershell
python scripts/tip_to_tip_training.py --certify --operator "SEU_NOME"
```

O script vai:

1. Rodar preflight de novo  
2. Executar **1000 operações**  
3. Mostrar **acertos** e **perdas**  
4. Salvar certificado em `data/certificates/SEU_NOME_....json`

**Proibido:**

- `--quick` (não vale para certificação)  
- Rodar sem `--operator`  
- Pedir ao agente para “consertar” no meio do teste  

---

## Passo 5 — O que entregar ao Douglas

Envie **os 3 itens**:

1. **Print do terminal** com a linha final, por exemplo:  
   `Score: 987/1000 (98.7%) — Nota A`  
   `Acertos: 987 | Perdas: 13`

2. **Arquivo JSON** de `data/certificates/` (o mais recente com seu nome)

3. **Uma frase:** o que foi a missão com mais falha (olhem o `.md` ao lado do JSON)

Modelo de mensagem:

```
DogEye certificacao — [SEU_NOME]
Score: ___/1000 (___%) — Nota ___
Acertos: ___ | Perdas: ___
Hostname: ___
Anexo: [arquivo .json]
```

---

## Critérios de nota (Douglas usa isso)

| Nota | % acertos | Certificado? |
|------|-----------|--------------|
| A | ≥ 95% | Sim |
| B | ≥ 85% | Sim |
| C | ≥ 70% | Não — treinar de novo |
| D/F | < 70% | Não — revisar setup |

Missões **TTT-M07** (live bloqueado): acerto = live **continua bloqueado**.  
Se alguém “passar” com live habilitado, **desqualifica**.

---

## As 10 missões (saibam o que está sendo testado)

| ID | Vocês provam que… |
|----|-------------------|
| TTT-M01 | Bridge Deriv carrega e live está off |
| TTT-M02 | API responde ping |
| TTT-M03 | Tick público chega por par |
| TTT-M04 | Paper trade abre e fecha |
| TTT-M05 | Tick → decisão → audit log |
| TTT-M06 | Proposta dry-run não compra |
| TTT-M07 | Live gate bloqueia trading real |
| TTT-M08 | E2E integração (M299) passa |
| TTT-M09 | Audit trail grava |
| TTT-M10 | Snapshot público por par |

## Os 10 pares

`R_100`, `R_75`, `R_50`, `cryBTCUSD`, `cryETHUSD`, `frxEURUSD`, `frxGBPUSD`, `frxUSDJPY`, `BOOM1000`, `CRASH1000`

---

## Troubleshooting (sem agente)

**ModuleNotFoundError: dashboard**  
→ Rode sempre da raiz `Doug.AI`, com venv ativado.

**Timeout / tick falhou**  
→ Rede instável. Espere 60s e rode **só o preflight** de novo. Se OK, repita certificação.

**Score baixo em M03/M10**  
→ Problema de rede Deriv. Não mude código; estabilize conexão e repita.

**Reprovou (< 95%)**  
→ Leiam `data/certificates/...md`, vejam falhas, corrijam ambiente, **nova certificação do zero**.

---

## Checklist antes de dizer “terminei”

- [ ] Preflight 100% OK (duas vezes: antes e durante `--certify`)
- [ ] 1000 operações (não usou `--quick`)
- [ ] Nome em `--operator` correto
- [ ] JSON em `data/certificates/` gerado
- [ ] Print do terminal salvo
- [ ] Douglas recebeu os 3 itens do Passo 5
- [ ] Ninguém usou agente durante o teste

---

## Comando único (referência)

```powershell
cd C:\Users\SEU_USUARIO\Desktop\DOUG.AI
.\.venv\Scripts\Activate.ps1
python scripts/tip_to_tip_preflight.py
python scripts/tip_to_tip_training.py --certify --operator "SEU_NOME"
```

**Boa sorte — sem mim do lado, vocês se garantem ou aprendem onde falta.**
