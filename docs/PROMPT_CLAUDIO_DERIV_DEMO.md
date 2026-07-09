# Prompt para colar ao Claudio — Token API Deriv DEMO (Virtual) Doug.AI

Links: https://home.deriv.com/dashboard/home · https://developers.deriv.com/
Projeto: `C:\Users\USUÁRIO\Desktop\DOUG.AI`
Repo: https://github.com/Douglassrf/Doug.AI

Objetivo: gerar token API da conta DEMO (virtual) Deriv e configurar no `.env` local
para testes Doug.AI / DogEye. Sem live. Sem commit de secrets.

## Regras obrigatórias

- Só conta DEMO — `loginid` deve começar com `VRT` ou `is_virtual=true`.
- Nunca commitar `.env` nem colar token no GitHub/chat.
- `DERIV_LIVE_ENABLED=false` sempre.
- `DOUG_MODE=demo`.
- Evidência: saída literal de `python scripts/test_deriv_demo.py`.

## Passo 1 — Ambiente

```powershell
cd C:\Users\USUÁRIO\Desktop\DOUG.AI
git pull origin master
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install websockets python-dotenv
copy .env.example .env
```

## Passo 2 — Criar token DEMO na Deriv (manual no browser)

1. Abrir: https://app.deriv.com/account/api-token
2. Login na Conta demo (virtual — canto superior, saldo fictício).
3. Create / Criar token.
4. Escopos: Read + Trade (somente demo).
5. Copiar o token (uma vez).

App ID: `1089` (público, MVP — não precisa registrar app customizado).

## Passo 3 — Colar no .env

Editar `C:\Users\USUÁRIO\Desktop\DOUG.AI\.env`:

```env
DERIV_APP_ID=1089
DERIV_API_TOKEN=COLAR_TOKEN_DEMO_AQUI
DOUG_MODE=demo
DERIV_LIVE_ENABLED=false
DERIV_MOCK_ENABLED=true
DOUG_DATA_DIR=data
```

Ou, mais seguro, colar o token direto no terminal (nunca no chat) com o script
que já grava no `.env` e testa a conexão sozinho:

```powershell
.\scripts\paste_deriv_token.ps1
```

Ou rodar o guia interativo (abre as URLs, valida o `.env`, mas não pede o token):

```powershell
python scripts/setup_deriv_api.py
```

## Passo 4 — Testar (obrigatório)

```powershell
$env:PYTHONPATH="C:\Users\USUÁRIO\Desktop\DOUG.AI"
python scripts/test_deriv_demo.py
python scripts/test_deriv_demo.py --json
```

Passou se: `[OK] Conta DEMO: VRT... · Virtual: True · ticks com quote`.

Teste público (sem token, fallback):

```powershell
python scripts/test_deriv_demo.py --public-only
```

Testes FastAPI (após pull):

```powershell
$env:PYTHONPATH="src"
pytest -q src/app/tests/test_deriv_integration.py
```

## Passo 5 — Tip-to-tip / treino (opcional)

```powershell
python scripts/tip_to_tip_preflight.py
python scripts/tip_to_tip_training.py --certify --operator "Claudio" --live
python scripts/dogeye_continuous_training.py --coach
```

## Entrega para Douglas

- Print do terminal com `test_deriv_demo.py` OK.
- Confirmar: token só no `.env` local.
- Confirmar: conta VRT* / virtual.
- Não fazer push do `.env`.

## Referências no repo

- `docs/DERIV_API_SETUP.md`
- `integrations/deriv_demo.py`
- `scripts/setup_deriv_api.py`
- `scripts/test_deriv_demo.py`

Fim da missão. Token demo Deriv configurado + teste verde = concluído.
