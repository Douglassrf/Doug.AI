"""
DOUG.AI — Intelligence Council Dashboard
Dashboard visual em Streamlit para monitorar decisões do IntelligenceCouncil em tempo real.

Run: streamlit run dashboard/app.py
"""
import sys
import os
import json
import time
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─────────────────────────────────────────────────────────────────────────────
# Configuração da página
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DOUG.AI — Intelligence Council",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS customizado
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #00d4aa;
        margin-bottom: 10px;
    }
    .buy-badge  { color: #00d4aa; font-weight: bold; font-size: 1.4em; }
    .sell-badge { color: #ff4b4b; font-weight: bold; font-size: 1.4em; }
    .hold-badge { color: #ffa500; font-weight: bold; font-size: 1.4em; }
    .block-badge { color: #ff4b4b; font-weight: bold; }
    .pass-badge  { color: #00d4aa; font-weight: bold; }
    .reduce-badge { color: #ffa500; font-weight: bold; }
    .section-title { color: #00d4aa; font-size: 1.1em; font-weight: bold; margin-top: 10px; }
    div[data-testid="stMetricValue"] { font-size: 2em !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Importa módulos DOUG.AI (com fallback para demo se não disponíveis)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from doug_os.discovery.agent_consensus_council import AgentConsensusCouncil, AgentVote
    from doug_os.discovery.red_team_adversarial import RedTeamAdversarial
    from doug_os.discovery.capital_router import CapitalRouter
    from doug_os.discovery.agent_reputation_engine import AgentReputationEngine, AgentPerformance
    from doug_os.discovery.formal_decision_verification import FormalDecisionVerification
    _DOUG_AVAILABLE = True
except ImportError:
    _DOUG_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Simulador de dados demo (quando módulos não estão no path)
# ─────────────────────────────────────────────────────────────────────────────

def _demo_council_state() -> Dict[str, Any]:
    rng = random.Random(int(time.time()) // 30)  # muda a cada 30s
    agents = ["MarketAgent", "RiskAgent", "DiscoveryAgent", "LearningAgent", "AuditAgent"]
    options = ["BUY", "SELL", "HOLD"]
    votes = []
    for ag in agents:
        opt = rng.choices(options, weights=[0.5, 0.2, 0.3])[0]
        votes.append({
            "agent_id": ag,
            "option": opt,
            "confidence": round(rng.uniform(0.55, 0.95), 2),
            "expertise_weight": round(rng.uniform(0.6, 1.0), 2),
        })
    # weighted tally
    tally: Dict[str, float] = {}
    for v in votes:
        tally[v["option"]] = tally.get(v["option"], 0) + v["expertise_weight"] * v["confidence"]
    decision = max(tally, key=lambda k: tally[k])
    total_w = sum(tally.values())
    confidence = round(tally[decision] / total_w, 3) if total_w else 0.5
    return {"votes": votes, "decision": decision, "confidence": confidence, "tally": tally}


def _demo_red_team(council: Dict[str, Any]) -> Dict[str, Any]:
    rng = random.Random(int(time.time()) // 30)
    if council["decision"] != "BUY" or council["confidence"] < 0.60:
        return {"verdict": "INACTIVE", "adversarial_score": 0.0, "arguments": [], "size_multiplier": 1.0}
    adv = round(rng.uniform(0.10, 0.85), 3)
    verdict = "BLOCK" if adv >= 0.70 else ("REDUCE" if adv >= 0.40 else "PASS")
    args = []
    if adv > 0.5:
        args.append("RSI sobrecomprado (73) — risco de reversão")
    if adv > 0.65:
        args.append("2 BUYs bloqueados neste regime nas últimas 24h (média -3.2%)")
    return {
        "verdict": verdict,
        "adversarial_score": adv,
        "historical_loss_score": round(adv * 0.4, 3),
        "logical_argument_score": round(adv * 0.3, 3),
        "shadow_divergence_score": round(adv * 0.3, 3),
        "arguments": args,
        "size_multiplier": 0.0 if verdict == "BLOCK" else (0.5 if verdict == "REDUCE" else 1.0),
    }


def _demo_capital_router() -> List[Dict[str, Any]]:
    assets = [
        ("BTC/USDT", "crypto", 0.82, 0.88, 1.0),
        ("ETH/USDT", "crypto", 0.75, 0.80, 0.95),
        ("EUR/USD", "fx", 0.70, 0.75, 0.90),
        ("GOLD", "commodities", 0.65, 0.70, 0.85),
        ("SOL/USDT", "crypto", 0.60, 0.65, 0.80),
        ("GBP/USD", "fx", 0.55, 0.68, 0.88),
        ("XRP/USDT", "crypto", 0.50, 0.60, 0.75),
        ("OIL", "commodities", 0.45, 0.55, 0.70),
    ]
    result = []
    for i, (asset, cluster, conf, rq, liq) in enumerate(assets):
        score = conf * rq * 0.58 * liq * (0.8 if cluster == "crypto" and i > 0 else 1.0)
        result.append({
            "asset": asset,
            "cluster": cluster,
            "opportunity_score": round(score, 3),
            "confidence": conf,
            "regime_quality": rq,
            "liquidity_score": liq,
            "allocated": i < 3,
            "allocated_fraction": round(1/3, 3) if i < 3 else 0.0,
        })
    return sorted(result, key=lambda x: x["opportunity_score"], reverse=True)


def _demo_reputation() -> List[Dict[str, Any]]:
    agents = ["MarketAgent", "RiskAgent", "DiscoveryAgent", "LearningAgent", "AuditAgent"]
    scores = [0.84, 0.91, 0.72, 0.78, 0.88]
    trends = ["improving", "stable", "declining", "stable", "improving"]
    return [{"agent": a, "score": s, "trend": t} for a, s, t in zip(agents, scores, trends)]


def _demo_audit_log() -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    entries = []
    actions = ["BUY", "HOLD", "SELL", "BUY", "BUY", "HOLD", "BUY", "SELL"]
    verdicts = ["PASS", "—", "—", "REDUCE", "BLOCK", "—", "PASS", "—"]
    assets = ["BTC/USDT", "ETH/USDT", "EUR/USD", "BTC/USDT", "SOL/USDT", "GOLD", "ETH/USDT", "GBP/USD"]
    confs = [0.82, 0.61, 0.55, 0.74, 0.78, 0.58, 0.86, 0.52]
    for i in range(8):
        entries.append({
            "timestamp": (now - timedelta(minutes=i * 15)).strftime("%H:%M:%S"),
            "asset": assets[i],
            "action": actions[i],
            "confidence": confs[i],
            "red_team": verdicts[i],
        })
    return entries


def _demo_regime() -> Dict[str, Any]:
    return {
        "regime": "BULL_TRENDING",
        "confidence": 0.78,
        "volatility": 0.022,
        "momentum": 0.031,
        "transition_score": 0.18,
    }


def _demo_thermometer() -> int:
    return random.Random(int(time.time()) // 30).randint(62, 88)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de visualização
# ─────────────────────────────────────────────────────────────────────────────

def _gauge(value: float, title: str, max_val: float = 1.0) -> go.Figure:
    color = "#ff4b4b" if value < 0.4 else ("#ffa500" if value < 0.7 else "#00d4aa")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100 if max_val == 1.0 else value,
        number={"suffix": "%", "font": {"size": 28, "color": "white"}},
        title={"text": title, "font": {"size": 14, "color": "#aaaaaa"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#555"},
            "bar": {"color": color},
            "bgcolor": "#1e2130",
            "bordercolor": "#333",
            "steps": [
                {"range": [0, 40], "color": "#2a1a1a"},
                {"range": [40, 70], "color": "#2a2a1a"},
                {"range": [70, 100], "color": "#1a2a1a"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=200,
        margin=dict(t=40, b=10, l=20, r=20),
    )
    return fig


def _vote_bar(votes: List[Dict], tally: Dict[str, float]) -> go.Figure:
    agents = [v["agent_id"] for v in votes]
    options = [v["option"] for v in votes]
    confs = [v["confidence"] for v in votes]
    colors = {"BUY": "#00d4aa", "SELL": "#ff4b4b", "HOLD": "#ffa500"}
    bar_colors = [colors.get(o, "#888") for o in options]
    fig = go.Figure(go.Bar(
        x=agents, y=confs,
        marker_color=bar_colors,
        text=[f"{o}<br>{c:.0%}" for o, c in zip(options, confs)],
        textposition="outside",
        textfont={"color": "white", "size": 11},
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1e2130",
        font_color="white",
        height=250,
        margin=dict(t=20, b=40, l=20, r=20),
        yaxis=dict(range=[0, 1.1], tickformat=".0%", gridcolor="#333"),
        xaxis=dict(tickfont={"size": 10}),
        showlegend=False,
    )
    return fig


def _opportunity_bar(router_data: List[Dict]) -> go.Figure:
    top = router_data[:10]
    colors = ["#00d4aa" if d["allocated"] else "#555" for d in top]
    fig = go.Figure(go.Bar(
        x=[d["asset"] for d in top],
        y=[d["opportunity_score"] for d in top],
        marker_color=colors,
        text=[f"{d['opportunity_score']:.3f}" for d in top],
        textposition="outside",
        textfont={"color": "white", "size": 10},
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1e2130",
        font_color="white",
        height=260,
        margin=dict(t=20, b=40, l=20, r=20),
        yaxis=dict(range=[0, 1.0], gridcolor="#333"),
        showlegend=False,
    )
    return fig


def _thermometer_gauge(value: int) -> go.Figure:
    color = "#ff4b4b" if value < 40 else ("#ffa500" if value < 65 else "#00d4aa")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={"reference": 60, "increasing": {"color": "#00d4aa"}, "decreasing": {"color": "#ff4b4b"}},
        number={"font": {"size": 42, "color": color}},
        title={"text": "Termômetro Global", "font": {"size": 15, "color": "#aaaaaa"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#555"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#1e2130",
            "bordercolor": "#333",
            "steps": [
                {"range": [0, 40], "color": "#1a0a0a"},
                {"range": [40, 65], "color": "#1a1a0a"},
                {"range": [65, 100], "color": "#0a1a0a"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 3},
                "thickness": 0.8,
                "value": 60,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117",
        height=280,
        margin=dict(t=50, b=10, l=20, r=20),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Layout principal
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/brain.png", width=60)
        st.title("DOUG.AI")
        st.caption("Intelligence Council v1.0")
        st.divider()

        auto_refresh = st.toggle("Auto-refresh (30s)", value=True)
        if auto_refresh:
            st.caption("🟢 Live — atualiza a cada 30s")
        else:
            st.caption("⏸ Pausado")

        st.divider()
        st.markdown("**Status dos módulos**")
        if _DOUG_AVAILABLE:
            st.success("✅ Módulos DOUG.AI conectados")
        else:
            st.warning("⚠️ Modo demo (dados simulados)")

        st.divider()
        asset_filter = st.selectbox(
            "Ativo foco",
            ["Todos", "BTC/USDT", "ETH/USDT", "EUR/USD", "GOLD", "SOL/USDT"],
        )
        show_rejected = st.checkbox("Mostrar rejeitados no Router", value=False)

        st.divider()
        st.caption("Missões 334–335 + Dashboard")
        st.caption("© 2026 DOUG.AI Project")

    # Header
    col_title, col_time = st.columns([4, 1])
    with col_title:
        st.markdown("## 🧠 DOUG.AI — Intelligence Council Dashboard")
    with col_time:
        st.markdown(f"<div style='text-align:right;color:#888;margin-top:12px'>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>", unsafe_allow_html=True)

    st.divider()

    # ── Coleta dados ─────────────────────────────────────────────────────────
    council   = _demo_council_state()
    red_team  = _demo_red_team(council)
    router    = _demo_capital_router()
    rep       = _demo_reputation()
    audit     = _demo_audit_log()
    regime    = _demo_regime()
    thermo    = _demo_thermometer()

    # ── Row 1: Termômetro + Decisão do Council + Regime ──────────────────────
    r1c1, r1c2, r1c3 = st.columns([2, 2, 2])

    with r1c1:
        st.plotly_chart(_thermometer_gauge(thermo), use_container_width=True)

    with r1c2:
        decision = council["decision"]
        conf = council["confidence"]
        badge_class = f"{decision.lower()}-badge"

        st.markdown("<p class='section-title'>⚖️ Decisão do Council</p>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:3em;font-weight:bold;text-align:center;color:{'#00d4aa' if decision=='BUY' else '#ff4b4b' if decision=='SELL' else '#ffa500'}'>{decision}</div>", unsafe_allow_html=True)
        st.plotly_chart(_gauge(conf, "Confiança do Council"), use_container_width=True)

    with r1c3:
        st.markdown("<p class='section-title'>📊 Regime de Mercado</p>", unsafe_allow_html=True)
        reg_color = "#00d4aa" if "BULL" in regime["regime"] else ("#ff4b4b" if "BEAR" in regime["regime"] else "#ffa500")
        st.markdown(f"<div style='font-size:1.8em;font-weight:bold;color:{reg_color}'>{regime['regime'].replace('_', ' ')}</div>", unsafe_allow_html=True)
        st.metric("Confiança regime", f"{regime['confidence']:.0%}")
        st.metric("Volatilidade", f"{regime['volatility']:.4f}")
        st.metric("Momentum", f"{regime['momentum']:+.4f}")
        st.metric("Transição", f"{regime['transition_score']:.2f}")

    st.divider()

    # ── Row 2: Votos do Council + Red Team ──────────────────────────────────
    r2c1, r2c2 = st.columns([3, 2])

    with r2c1:
        st.markdown("<p class='section-title'>🗳️ Votos dos Agentes</p>", unsafe_allow_html=True)
        st.plotly_chart(_vote_bar(council["votes"], council["tally"]), use_container_width=True)

        # tabela de votos
        vote_rows = ""
        for v in council["votes"]:
            opt_color = "#00d4aa" if v["option"] == "BUY" else ("#ff4b4b" if v["option"] == "SELL" else "#ffa500")
            vote_rows += f"<tr><td>{v['agent_id']}</td><td style='color:{opt_color};font-weight:bold'>{v['option']}</td><td>{v['confidence']:.0%}</td><td>{v['expertise_weight']:.2f}</td></tr>"

        st.markdown(f"""
        <table style='width:100%;color:white;font-size:0.9em;'>
        <tr style='color:#888;border-bottom:1px solid #333'><th>Agente</th><th>Voto</th><th>Confiança</th><th>Peso</th></tr>
        {vote_rows}
        </table>
        """, unsafe_allow_html=True)

    with r2c2:
        st.markdown("<p class='section-title'>🔴 Red Team Adversarial</p>", unsafe_allow_html=True)

        rt_verdict = red_team.get("verdict", "INACTIVE")
        rt_score   = red_team.get("adversarial_score", 0.0)

        if rt_verdict == "INACTIVE":
            st.info("Red Team inativo — Council não emitiu BUY com confiança ≥ 60%")
        else:
            vcolor = "#ff4b4b" if rt_verdict == "BLOCK" else ("#ffa500" if rt_verdict == "REDUCE" else "#00d4aa")
            st.markdown(f"<div style='font-size:2em;font-weight:bold;color:{vcolor};text-align:center'>{rt_verdict}</div>", unsafe_allow_html=True)

            # gauge adversarial
            fig_rt = go.Figure(go.Indicator(
                mode="gauge+number",
                value=rt_score * 100,
                number={"suffix": "%", "font": {"size": 22, "color": "white"}},
                title={"text": "Adversarial Score", "font": {"size": 13, "color": "#aaa"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": vcolor},
                    "bgcolor": "#1e2130",
                    "steps": [
                        {"range": [0, 40], "color": "#0a1a0a"},
                        {"range": [40, 70], "color": "#1a1a0a"},
                        {"range": [70, 100], "color": "#1a0a0a"},
                    ],
                    "threshold": {"line": {"color": "white", "width": 2}, "value": 70, "thickness": 0.75},
                },
            ))
            fig_rt.update_layout(paper_bgcolor="#0e1117", height=190, margin=dict(t=40, b=5, l=10, r=10))
            st.plotly_chart(fig_rt, use_container_width=True)

            # sub-scores
            st.markdown(f"""
            <table style='width:100%;color:white;font-size:0.85em;'>
            <tr><td>📜 Histórico (40%)</td><td style='color:#ffa500'>{red_team.get('historical_loss_score', 0):.3f}</td></tr>
            <tr><td>🧠 Lógico (30%)</td><td style='color:#ffa500'>{red_team.get('logical_argument_score', 0):.3f}</td></tr>
            <tr><td>🌑 Shadow Div (30%)</td><td style='color:#ffa500'>{red_team.get('shadow_divergence_score', 0):.3f}</td></tr>
            <tr><td>📏 Size multiplier</td><td style='color:#00d4aa'>{red_team.get('size_multiplier', 1.0):.1f}x</td></tr>
            </table>
            """, unsafe_allow_html=True)

            if red_team.get("arguments"):
                st.markdown("**Argumentos adversariais:**")
                for arg in red_team["arguments"]:
                    st.markdown(f"⚠️ {arg}")

    st.divider()

    # ── Row 3: Capital Router ─────────────────────────────────────────────────
    st.markdown("<p class='section-title'>💰 Capital Router — Talent Show</p>", unsafe_allow_html=True)
    r3c1, r3c2 = st.columns([3, 2])

    with r3c1:
        display_data = router if show_rejected else [d for d in router]
        st.plotly_chart(_opportunity_bar(display_data), use_container_width=True)

    with r3c2:
        st.markdown("**🏆 Top 3 Alocados**")
        top3 = [d for d in router if d["allocated"]]
        for i, asset in enumerate(top3):
            cluster_emoji = {"crypto": "₿", "fx": "💱", "commodities": "🏅", "equities": "📈"}.get(asset["cluster"], "•")
            st.markdown(f"""
            <div class='metric-card'>
            <b>{i+1}. {cluster_emoji} {asset['asset']}</b> &nbsp;
            <span style='color:#888'>{asset['cluster']}</span><br>
            Score: <b style='color:#00d4aa'>{asset['opportunity_score']:.3f}</b> &nbsp;
            Fração: <b>{asset['allocated_fraction']:.0%}</b>
            </div>
            """, unsafe_allow_html=True)

        if show_rejected:
            st.markdown("**❌ Rejeitados**")
            for asset in router[3:]:
                st.markdown(f"<span style='color:#555'>• {asset['asset']} ({asset['cluster']}) — {asset['opportunity_score']:.3f}</span>", unsafe_allow_html=True)

    st.divider()

    # ── Row 4: Reputação dos Agentes + Audit Log ──────────────────────────────
    r4c1, r4c2 = st.columns([2, 3])

    with r4c1:
        st.markdown("<p class='section-title'>⭐ Reputação dos Agentes</p>", unsafe_allow_html=True)
        for agent in rep:
            trend_icon = "📈" if agent["trend"] == "improving" else ("📉" if agent["trend"] == "declining" else "➡️")
            score_color = "#00d4aa" if agent["score"] >= 0.80 else ("#ffa500" if agent["score"] >= 0.65 else "#ff4b4b")
            bar_width = int(agent["score"] * 100)
            st.markdown(f"""
            <div style='margin-bottom:8px'>
            <span style='color:white'>{trend_icon} <b>{agent['agent']}</b></span>
            <div style='background:#333;border-radius:4px;height:8px;margin-top:3px'>
              <div style='background:{score_color};width:{bar_width}%;height:8px;border-radius:4px'></div>
            </div>
            <span style='color:{score_color};font-size:0.85em'>{agent['score']:.0%} — {agent['trend']}</span>
            </div>
            """, unsafe_allow_html=True)

    with r4c2:
        st.markdown("<p class='section-title'>📋 Audit Log — Últimas Decisões</p>", unsafe_allow_html=True)

        header = "<tr style='color:#888;font-size:0.85em'><th>Hora</th><th>Ativo</th><th>Ação</th><th>Conf.</th><th>Red Team</th></tr>"
        rows = ""
        for entry in audit:
            act_color = "#00d4aa" if entry["action"] == "BUY" else ("#ff4b4b" if entry["action"] == "SELL" else "#ffa500")
            rt = entry["red_team"]
            rt_color = "#ff4b4b" if rt == "BLOCK" else ("#ffa500" if rt == "REDUCE" else ("#00d4aa" if rt == "PASS" else "#555"))
            rows += f"""<tr style='border-bottom:1px solid #222'>
                <td style='color:#888'>{entry['timestamp']}</td>
                <td style='color:white'><b>{entry['asset']}</b></td>
                <td style='color:{act_color};font-weight:bold'>{entry['action']}</td>
                <td style='color:#aaa'>{entry['confidence']:.0%}</td>
                <td style='color:{rt_color};font-weight:bold'>{rt}</td>
            </tr>"""

        st.markdown(f"""
        <table style='width:100%;color:white;font-size:0.9em;border-collapse:collapse'>
        {header}{rows}
        </table>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Row 5: BrianSupreme — Explicação Textual ──────────────────────────────
    st.markdown("<p class='section-title'>🗣️ BrianSupreme — Explicação da Decisão</p>", unsafe_allow_html=True)

    decision_text = council["decision"]
    conf_text = council["confidence"]
    rt_text = red_team.get("verdict", "INACTIVE")
    top_asset = router[0]["asset"] if router else "N/A"

    if decision_text == "BUY" and rt_text == "BLOCK":
        explanation = f"""
        ⛔ **DECISÃO BLOQUEADA pelo Red Team**

        O Council votou **BUY** com confiança de **{conf_text:.0%}**, porém o Red Team identificou
        riscos significativos (adversarial score: **{red_team.get('adversarial_score', 0):.3f}**).
        O regime **{regime['regime']}** apresentou histórico de perdas em operações similares.
        Recomendação: aguardar confirmação de reversão antes de reentrar.
        """
    elif decision_text == "BUY" and rt_text == "REDUCE":
        explanation = f"""
        ⚠️ **POSIÇÃO REDUZIDA 50%**

        O Council votou **BUY** com confiança de **{conf_text:.0%}**. O Red Team aprovou com ressalvas —
        o ativo prioritário é **{top_asset}** no regime **{regime['regime']}**.
        Capital alocado em 50% do normal devido a inconsistências nos dados de mercado.
        Volatilidade atual: **{regime['volatility']:.4f}**.
        """
    elif decision_text == "BUY":
        explanation = f"""
        ✅ **BUY APROVADO — Top 3 alocados**

        Council votou **BUY** com alta confiança (**{conf_text:.0%}**). Red Team verificou e aprovou sem restrições.
        Regime atual (**{regime['regime']}**) favorável — momentum positivo (**{regime['momentum']:+.4f}**).
        Capital alocado em **{top_asset}**, **{router[1]['asset'] if len(router) > 1 else 'N/A'}** e **{router[2]['asset'] if len(router) > 2 else 'N/A'}**
        com opportunity scores acima de **{router[2]['opportunity_score']:.3f}** cada.
        """
    elif decision_text == "SELL":
        explanation = f"""
        📉 **SELL — Sinal de saída identificado**

        O Council detectou deterioração nas condições de mercado (confiança: **{conf_text:.0%}**).
        Regime **{regime['regime']}** com transição iminente (score: **{regime['transition_score']:.2f}**).
        Momentum atual: **{regime['momentum']:+.4f}**. Red Team concorda com a saída.
        """
    else:
        explanation = f"""
        ⏸ **HOLD — Aguardando melhor oportunidade**

        O Council não identificou sinal claro de entrada ou saída (confiança: **{conf_text:.0%}**).
        Regime **{regime['regime']}** sem direção definida — aguardando confirmação.
        Capital preservado. Próxima avaliação em 15 minutos.
        """

    st.markdown(f"""
    <div style='background:#1e2130;border-radius:10px;padding:20px;border-left:4px solid #00d4aa;font-size:1.05em;line-height:1.7'>
    {explanation}
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-refresh ──────────────────────────────────────────────────────────
    if auto_refresh:
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    main()
