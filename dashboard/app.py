"""Doug.AI Constitutional Trading — Operations Dashboard (Docker MVP)."""
from __future__ import annotations

import os
import random
import time
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.data_store import (
    DEMO_AUDIT_LOG_PATH,
    append_audit_entry,
    load_settings,
    read_audit_log,
    save_settings,
)
from dashboard.decision_panel import page_decisions
from dashboard.deriv_panel import page_deriv_demo
from dashboard.preflight_bridge import (
    get_council_snapshot,
    get_layer_scores,
    get_red_team_snapshot,
    get_signal_counts,
    get_thermometer,
    probe_missions,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Doug.AI — Constitutional Trading",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODE = os.environ.get("DOUG_MODE", "paper").upper()
if MODE == "PAPER":
    MODE_LABEL = "PAPER"
elif MODE == "DEMO":
    MODE_LABEL = "DEMO"
elif MODE == "SHADOW":
    MODE_LABEL = "SHADOW"
elif MODE == "LIVE":
    MODE_LABEL = "LIVE"
else:
    MODE_LABEL = "FLAT"

THEME_CSS = """
<style>
    .main { background-color: #0e1117; }
    .doug-header { color: #00d4aa; font-size: 1.6em; font-weight: 700; }
    .doug-sub { color: #888; font-size: 0.95em; }
    .status-green { color: #00d4aa; font-weight: bold; font-size: 1.3em; }
    .status-yellow { color: #ffa500; font-weight: bold; font-size: 1.3em; }
    .status-red { color: #ff4b4b; font-weight: bold; font-size: 1.3em; }
    .footer-disclaimer {
        color: #666; font-size: 0.8em; border-top: 1px solid #333;
        padding-top: 12px; margin-top: 24px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.8em !important; }
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


def _maybe_demo_tick(settings: dict) -> None:
    """Append a demo audit entry when generator is enabled."""
    if not settings.get("demo_generator"):
        return
    interval = max(5, int(settings.get("refresh_interval_sec", 30)))
    key = "last_demo_tick"
    now = time.time()
    if key not in st.session_state:
        st.session_state[key] = now
        return
    if now - st.session_state[key] >= interval:
        rng = random.Random(int(now))
        action = rng.choice(["BUY", "SELL", "HOLD"])
        conf = round(rng.uniform(0.5, 0.9), 2)
        # Grava em arquivo SEPARADO do audit_log real (path=DEMO_AUDIT_LOG_PATH)
        # — nunca deve ficar indistinguivel de uma decisao real do Doug.AI.
        append_audit_entry(
            "demo_trade_decision",
            {
                "asset": rng.choice(["BTC/USDT", "ETH/USDT", "EUR/USD", "GOLD"]),
                "action": action,
                "confidence": conf,
                "mode": settings.get("mode", MODE_LABEL),
                "red_team": rng.choice(["PASS", "—", "REDUCE"]) if action == "BUY" else "—",
                "layer_score": int(conf * 100),
                "cycle_id": f"cyc_{rng.randbytes(3).hex()}",
                "synthetic": True,
            },
            path=DEMO_AUDIT_LOG_PATH,
        )
        st.session_state[key] = now


def _thermometer_chart(value: int) -> go.Figure:
    color = "#ff4b4b" if value < 40 else ("#ffa500" if value < 65 else "#00d4aa")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 40, "color": color}},
            title={"text": "Termômetro Constitucional (0–100)", "font": {"color": "#aaa"}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "bgcolor": "#1e2130",
                "steps": [
                    {"range": [0, 40], "color": "#1a0a0a"},
                    {"range": [40, 65], "color": "#1a1a0a"},
                    {"range": [65, 100], "color": "#0a1a0a"},
                ],
            },
        )
    )
    fig.update_layout(paper_bgcolor="#0e1117", height=260, margin=dict(t=40, b=10, l=20, r=20))
    return fig


def _layers_chart(layers: list[dict]) -> go.Figure:
    colors = {"green": "#00d4aa", "yellow": "#ffa500", "red": "#ff4b4b"}
    df = pd.DataFrame(layers)
    fig = px.bar(
        df,
        x="name",
        y="score",
        color="status",
        color_discrete_map=colors,
        labels={"name": "Camada", "score": "Score"},
    )
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1e2130",
        font_color="white",
        height=400,
        showlegend=False,
        xaxis_tickangle=-35,
    )
    fig.update_yaxes(range=[0, 100], gridcolor="#333")
    return fig


def page_overview(settings: dict, bridge_status) -> None:
    audit = read_audit_log(50)
    layers, layer_source = get_layer_scores()
    thermo = get_thermometer(layers)
    counts = get_signal_counts(audit)
    mode = settings.get("mode", MODE_LABEL)

    st.markdown('<p class="doug-header">Overview — Constitutional Trading</p>', unsafe_allow_html=True)
    st.caption(f"Dados de camadas: **{layer_source}** | Bridge: **{bridge_status.source}**")

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        st.plotly_chart(_thermometer_chart(thermo), use_container_width=True)
    with c2:
        st.metric("🟢 Green", counts["green"])
    with c3:
        st.metric("🟡 Yellow", counts["yellow"])
    with c4:
        st.metric("🔴 Red", counts["red"])

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Modo operacional", mode)
    with m2:
        st.metric("Horizonte", settings.get("horizon", "daily").title())
    with m3:
        st.metric("Max ativos", settings.get("max_assets", 3))

    st.divider()
    st.subheader("Últimas operações")
    if audit:
        rows = []
        for e in audit[:10]:
            p = e.get("payload", {})
            ts = e.get("timestamp", "")[:19].replace("T", " ")
            rows.append(
                {
                    "Hora (UTC)": ts,
                    "Ativo": p.get("asset", "—"),
                    "Ação": p.get("action", "—"),
                    "Conf.": p.get("confidence", "—"),
                    "Red Team": p.get("red_team", "—"),
                    "Modo": p.get("mode", mode),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma entrada no audit log. Ative o demo generator ou rode `scripts/run_preflight_demo.py`.")


def page_layers(settings: dict) -> None:
    layers, source = get_layer_scores()
    st.markdown('<p class="doug-header">10 Camadas Constitucionais</p>', unsafe_allow_html=True)
    st.caption(f"Fonte: **{source}** — L1–L3 tentam importar `ThreeLayerAlertSystem` de `/app/latest` ou `/app/missions`")
    st.plotly_chart(_layers_chart(layers), use_container_width=True)

    df = pd.DataFrame(layers)
    st.dataframe(
        df.rename(columns={"layer": "#", "name": "Camada", "score": "Score", "status": "Status"}),
        use_container_width=True,
        hide_index=True,
    )


def page_operations(settings: dict) -> None:
    st.markdown('<p class="doug-header">Operations Log</p>', unsafe_allow_html=True)
    audit = read_audit_log(200)
    if not audit:
        st.warning("Audit log vazio em `data/audit_log.jsonl`.")
        return

    rows = []
    for e in audit:
        p = e.get("payload", {})
        rows.append(
            {
                "timestamp": e.get("timestamp", ""),
                "event_type": e.get("event_type", ""),
                "asset": p.get("asset", ""),
                "action": p.get("action", ""),
                "confidence": p.get("confidence", ""),
                "red_team": p.get("red_team", ""),
                "layer_score": p.get("layer_score", ""),
                "mode": p.get("mode", ""),
                "cycle_id": p.get("cycle_id", ""),
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Exportar CSV", csv, "audit_log_export.csv", "text/csv")


def page_settings(settings: dict) -> None:
    st.markdown('<p class="doug-header">Settings Panel</p>', unsafe_allow_html=True)

    with st.form("settings_form"):
        refresh = st.slider("Refresh interval (segundos)", 5, 120, int(settings.get("refresh_interval_sec", 30)))
        horizon = st.selectbox("Horizonte", ["daily", "weekly", "monthly"], index=["daily", "weekly", "monthly"].index(settings.get("horizon", "daily")))
        paper = st.toggle("Paper mode (sem ordens reais)", value=bool(settings.get("paper_mode", True)))
        max_assets = st.number_input("Max ativos alocados", 1, 10, int(settings.get("max_assets", 3)))
        theme = st.selectbox("Tema", ["dark", "light"], index=0 if settings.get("theme") == "dark" else 1)
        demo_gen = st.toggle(
            "Demo generator (dados sinteticos — grava em audit_log_demo.jsonl, NUNCA no log real)",
            value=bool(settings.get("demo_generator", False)),
        )
        mode = st.selectbox("Modo", ["PAPER", "SHADOW", "LIVE", "FLAT"], index=["PAPER", "SHADOW", "LIVE", "FLAT"].index(settings.get("mode", MODE_LABEL)))
        submitted = st.form_submit_button("Salvar configurações")

    if submitted:
        new_settings = {
            "refresh_interval_sec": refresh,
            "horizon": horizon,
            "paper_mode": paper,
            "max_assets": max_assets,
            "theme": theme,
            "demo_generator": demo_gen,
            "mode": mode,
        }
        save_settings(new_settings)
        st.success("Configurações salvas em `data/settings.json`.")
        st.rerun()

    st.divider()
    st.subheader("Variáveis de ambiente (somente leitura)")
    st.code(f"DOUG_MODE={os.environ.get('DOUG_MODE', 'paper')}\nDOUG_DATA_DIR={os.environ.get('DOUG_DATA_DIR', '/app/data')}")


def page_council(settings: dict) -> None:
    council = get_council_snapshot()
    red_team = get_red_team_snapshot(council)

    st.markdown('<p class="doug-header">Council / Red Team</p>', unsafe_allow_html=True)
    st.caption("Painéis placeholder — dados demo com regime live quando importável.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚖️ Intelligence Council")
        dec = council["decision"]
        color = "#00d4aa" if dec == "BUY" else ("#ff4b4b" if dec == "SELL" else "#ffa500")
        st.markdown(f"<div style='font-size:2.5em;font-weight:bold;color:{color}'>{dec}</div>", unsafe_allow_html=True)
        st.metric("Confiança", f"{council['confidence']:.0%}")
        st.metric("Regime", council["regime"].replace("_", " "))
        for agent in council["agents"]:
            st.caption(f"{agent['name']}: {agent['vote']} (peso {agent['weight']:.0%})")
            st.progress(agent["weight"])

    with c2:
        st.subheader("🔴 Red Team Adversarial")
        verdict = red_team["verdict"]
        if verdict == "INACTIVE":
            st.info("Inativo — Council não emitiu BUY com confiança ≥ 60%")
        else:
            vcolor = "#ff4b4b" if verdict == "BLOCK" else ("#ffa500" if verdict == "REDUCE" else "#00d4aa")
            st.markdown(f"<div style='font-size:2em;font-weight:bold;color:{vcolor}'>{verdict}</div>", unsafe_allow_html=True)
            st.metric("Adversarial score", f"{red_team['score']:.3f}")
            for arg in red_team.get("arguments", []):
                st.warning(arg)

    st.divider()
    st.subheader("Brian Supreme (placeholder)")
    st.markdown(
        """
        > *Explicação constitucional gerada offline.* O Council agregou votos dos agentes
        > especializados; o Red Team validou adversarialmente antes de qualquer execução shadow.
        > Nenhuma ordem real é enviada enquanto **paper mode** estiver ativo.
        """
    )


def main() -> None:
    settings = load_settings()
    _maybe_demo_tick(settings)
    bridge_status = probe_missions()

    with st.sidebar:
        st.markdown("## ⚖️ Doug.AI")
        st.caption("Constitutional Trading")
        st.divider()
        page = st.radio(
            "Navegação",
            ["Overview", "Cérebro (Decisões)", "10 Layers", "Operations", "Deriv Demo", "Settings", "Council / Red Team"],
            label_visibility="collapsed",
        )
        st.divider()
        auto = st.toggle("Auto-refresh", value=True)
        if auto:
            st.caption(f"🟢 Live — {settings.get('refresh_interval_sec', 30)}s")
        if bridge_status.modules_loaded:
            st.success(f"✅ {len(bridge_status.modules_loaded)} módulos")
        else:
            st.warning("⚠️ Modo demo")
        st.caption(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

    if page == "Overview":
        page_overview(settings, bridge_status)
    elif page == "Cérebro (Decisões)":
        page_decisions(settings)
    elif page == "10 Layers":
        page_layers(settings)
    elif page == "Operations":
        page_operations(settings)
    elif page == "Deriv Demo":
        page_deriv_demo(settings)
    elif page == "Settings":
        page_settings(settings)
    elif page == "Council / Red Team":
        page_council(settings)

    st.markdown(
        """
        <div class="footer-disclaimer">
        <b>Disclaimer:</b> Doug.AI é software de pesquisa e educação. Não constitui aconselhamento
        financeiro. Operações são paper/shadow por padrão — sem dinheiro real, sem ordens em exchange.
        Use por sua conta e risco. © 2026 Doug.AI — Constitutional Trading.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if auto:
        time.sleep(0.3)
        st.rerun()


if __name__ == "__main__":
    main()
