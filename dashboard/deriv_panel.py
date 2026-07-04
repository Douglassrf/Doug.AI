"""Deriv Demo dashboard panel."""
from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from dashboard.data_store import append_audit_entry, load_settings, save_settings
from integrations.deriv_demo import (
    DerivLiveGate,
    current_doug_mode_label,
    is_deriv_live_enabled,
    is_doug_demo_mode,
    is_doug_live_mode,
    load_config,
    load_deriv_status,
    run_public_demo_snapshot,
    run_snapshot,
)


def _token_configured(settings: dict) -> bool:
    token, _ = load_config()
    deriv_settings = settings.get("deriv", {})
    return bool(token or str(deriv_settings.get("api_token", "")).strip())


def page_deriv_demo(settings: dict) -> None:
    st.markdown('<p class="doug-header">Deriv Demo — Paper Trading</p>', unsafe_allow_html=True)
    st.caption(
        "Conta **virtual/demo** apenas. Nenhuma ordem com dinheiro real. "
        "Sinais locais vão para `data/audit_log.jsonl`."
    )

    mode_label = current_doug_mode_label()
    token_ok = _token_configured(settings)
    live_gate = DerivLiveGate().check()

    mode_col, token_col, doc_col = st.columns([1, 1, 2])
    with mode_col:
        if mode_label == "LIVE":
            st.error(f"**Modo atual:** {mode_label}")
            if is_deriv_live_enabled():
                st.warning("DERIV_LIVE_ENABLED=true — live ainda bloqueado pelos portões.")
            else:
                st.caption("DERIV_LIVE_ENABLED=false (seguro)")
        elif mode_label == "DEMO":
            st.success(f"**Modo atual:** {mode_label}")
        else:
            st.info(f"**Modo atual:** {mode_label}")
    with token_col:
        if token_ok:
            st.success("**Token:** configurado")
        else:
            st.warning("**Token:** não configurado")
    with doc_col:
        st.markdown(
            "📖 [Guia Deriv API (demo → live)](docs/DERIV_API_SETUP.md) — "
            "Fase 1: demo agora · Fase 2: oficial depois"
        )

    if is_doug_live_mode() and not live_gate.allowed:
        st.warning(f"Live bloqueado: {live_gate.reason}")
        with st.expander("Portões pendentes (Fase 2)"):
            for gate in live_gate.gates_pending:
                st.markdown(f"- `{gate}`")

    demo_mode = (
        is_doug_demo_mode()
        or os.environ.get("DEMO_MODE", "").lower() in ("1", "true", "yes")
        or not token_ok
    )
    cached = load_deriv_status()

    if demo_mode and not token_ok:
        st.info(
            "**Modo demo (DOUG_MODE=demo)** — ticks públicos via app_id **1089**, sem token. "
            "Use **Atualizar demo público** abaixo ou configure `DERIV_API_TOKEN` para saldo real da conta demo."
        )
        if cached is None:
            with st.spinner("Carregando ticks públicos Deriv..."):
                run_public_demo_snapshot(log_paper=False)
                cached = load_deriv_status()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Token configurado", "Sim" if token_ok else "Não")
    with c2:
        connected = cached.get("connected") if cached else False
        st.metric("Última conexão", "OK" if connected else "—")
    with c3:
        if cached and cached.get("account"):
            bal = cached["account"].get("balance", 0)
            cur = cached["account"].get("currency", "USD")
            st.metric("Saldo demo", f"{bal:.2f} {cur}")
        else:
            st.metric("Saldo demo", "—")

    if cached and cached.get("error"):
        st.error(cached["error"])
    elif not token_ok and not demo_mode:
        st.warning(
            "Configure `DERIV_API_TOKEN` no arquivo `.env` (recomendado) "
            "ou no formulário abaixo. **Use apenas token da conta DEMO.**"
        )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🔄 Atualizar agora", type="primary", disabled=not token_ok):
            with st.spinner("Conectando Deriv demo..."):
                snap = run_snapshot(log_paper=True)
                if snap.error:
                    st.error(snap.error)
                else:
                    st.success("Snapshot atualizado.")
                    st.rerun()
    with col_b:
        if st.button("📋 Testar sem ordens (só ticks)", disabled=not token_ok):
            with st.spinner("Lendo ticks..."):
                snap = run_snapshot(log_paper=False)
                if snap.error:
                    st.error(snap.error)
                else:
                    st.success("Ticks lidos (sem log de paper).")
                    st.rerun()
    with col_c:
        if st.button("🌐 Atualizar demo público", disabled=not demo_mode):
            with st.spinner("Ticks públicos (app_id 1089)..."):
                snap = run_public_demo_snapshot(log_paper=False)
                if snap.error:
                    st.error(snap.error)
                else:
                    st.success("Demo público atualizado (sem token).")
                    st.rerun()

    cached = load_deriv_status()
    if cached:
        st.caption(f"Última verificação: {cached.get('checked_at', '—')}")
        acct = cached.get("account")
        if acct:
            st.info(
                f"Conta **{acct.get('loginid')}** (virtual={acct.get('is_virtual')}) — "
                f"{acct.get('fullname') or acct.get('email') or 'demo'}"
            )

        ticks = cached.get("ticks", {})
        if ticks:
            st.subheader("Últimos ticks")
            rows = []
            for sym, t in ticks.items():
                rows.append(
                    {
                        "Símbolo": sym,
                        "Quote": t.get("quote", "—"),
                        "Epoch": t.get("epoch", "—"),
                        "Erro": t.get("error", ""),
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        candles = cached.get("candles", {})
        if candles:
            st.subheader("Candles (1 min, últimos 5)")
            for sym, cs in candles.items():
                if cs:
                    st.markdown(f"**{sym}**")
                    st.dataframe(pd.DataFrame(cs), use_container_width=True, hide_index=True)

        signals = cached.get("paper_signals", [])
        if signals:
            st.subheader("Sinais paper (simulação local)")
            st.dataframe(pd.DataFrame(signals), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Configuração Deriv (settings)")
    deriv_cfg = settings.get("deriv", {})
    with st.form("deriv_settings"):
        st.caption(
            "Preferência: variável `DERIV_API_TOKEN` no `.env` (não versionado). "
            "O campo abaixo grava em `data/settings.json` — use só se necessário."
        )
        api_token = st.text_input(
            "API Token (demo)",
            value="",
            type="password",
            placeholder="Deixe vazio para manter token atual / usar .env",
        )
        app_id = st.number_input("App ID", min_value=1, value=int(deriv_cfg.get("app_id", 1089)))
        symbols_raw = st.text_input(
            "Símbolos (vírgula)",
            value=",".join(deriv_cfg.get("symbols", ["R_100", "cryBTCUSD"])),
        )
        enabled = st.toggle("Deriv demo habilitado", value=bool(deriv_cfg.get("enabled", True)))
        submitted = st.form_submit_button("Salvar Deriv settings")

    if submitted:
        new_deriv = {
            "enabled": enabled,
            "app_id": int(app_id),
            "symbols": [s.strip() for s in symbols_raw.split(",") if s.strip()],
        }
        if api_token.strip():
            new_deriv["api_token"] = api_token.strip()
        elif deriv_cfg.get("api_token"):
            new_deriv["api_token"] = deriv_cfg["api_token"]
        merged = dict(settings)
        merged["deriv"] = new_deriv
        save_settings(merged)
        append_audit_entry(
            "deriv_config_saved",
            {"app_id": app_id, "symbols": new_deriv["symbols"], "enabled": enabled},
        )
        st.success("Configuração Deriv salva.")
        st.rerun()

    st.markdown(
        """
        #### Como obter token DEMO (Deriv)
        1. Acesse [home.deriv.com](https://home.deriv.com/dashboard/home) e faça login.
        2. No canto superior, selecione **Conta demo** (saldo virtual, ex.: USD 10.000).
        3. **Configurações da conta** → **API token** → **Criar**
           ([app.deriv.com/account/api-token](https://app.deriv.com/account/api-token)).
        4. Escopos: **Read** + **Trade** (somente na conta demo).
        5. Copie o token para `.env` como `DERIV_API_TOKEN=...`
        6. Rode: `python scripts/test_deriv_demo.py`

        Documentação completa: `docs/DERIV_API_SETUP.md`
        """
    )
