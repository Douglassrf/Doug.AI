"""Painel 'Cerebro' — decisoes ao vivo do Doug.AI (paper) no dashboard."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
DECISIONS_PATH = DATA / "training" / "live_decisions.jsonl"
SCORECARD_PATH = DATA / "training" / "backtest_scorecard.json"
NEWS_PATH = DATA / "news_snapshot.json"

LEVEL_BADGE = {
    "OPERAR": "🟢 OPERAR",
    "OBSERVAR": "🟡 OBSERVAR",
    "FICAR_DE_FORA": "⚪ DE FORA",
}


def _load_recent_decisions(limit: int = 100) -> list[dict]:
    if not DECISIONS_PATH.exists():
        return []
    try:
        lines = DECISIONS_PATH.read_text(encoding="utf-8").strip().splitlines()
        out = []
        for line in lines[-limit:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return list(reversed(out))
    except OSError:
        return []


def _load_scorecard() -> dict | None:
    if not SCORECARD_PATH.exists():
        return None
    try:
        return json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def page_decisions(settings: dict) -> None:
    st.markdown('<p class="doug-header">🧠 Cérebro — Decisões ao Vivo (paper)</p>', unsafe_allow_html=True)
    st.caption(
        "Cada decisão pondera o voto das 10 estratégias pelo desempenho histórico REAL "
        "(backtest M38 + treino contínuo). O Doug só recomenda operar com vantagem comprovada — "
        "na dúvida, observa; sem vantagem, fica de fora."
    )

    # ── Pensar agora ──
    with st.expander("🤔 Pensar agora (consulta dados reais da Deriv)", expanded=False):
        c1, c2 = st.columns([3, 1])
        with c1:
            symbols_raw = st.text_input("Pares (separados por espaço)", "R_25 R_50 R_75 R_100")
        with c2:
            run = st.button("Pensar", type="primary", use_container_width=True)
        if run:
            symbols = tuple(s.strip() for s in symbols_raw.split() if s.strip())
            if symbols:
                with st.spinner(f"Doug pensando em {len(symbols)} pares..."):
                    try:
                        from training.decision_engine import decide_many

                        decisions = decide_many(symbols)
                        for d in decisions:
                            badge = LEVEL_BADGE.get(d.level, d.level)
                            conf = f"{d.confidence*100:.1f}%" if d.confidence is not None else "—"
                            stake = f" · stake {d.stake_pct}%" if d.stake_pct else ""
                            st.markdown(f"**{badge} · {d.pair}** [{d.scenario}] → `{d.direction.upper()}` · confiança {conf}{stake}")
                            for r in d.reasons:
                                st.caption(f"• {r}")
                        st.success("Decisões registradas no log auditável.")
                    except Exception as exc:
                        st.error(f"Falha ao decidir: {exc}")

    st.divider()

    # ── Historico de decisoes ──
    decisions = _load_recent_decisions(200)
    operar = sum(1 for d in decisions if d.get("level") == "OPERAR")
    observar = sum(1 for d in decisions if d.get("level") == "OBSERVAR")
    fora = sum(1 for d in decisions if d.get("level") == "FICAR_DE_FORA")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Decisões registradas", len(decisions))
    m2.metric("🟢 Operar", operar)
    m3.metric("🟡 Observar", observar)
    m4.metric("⚪ De fora", fora)

    if decisions:
        rows = []
        for d in decisions[:60]:
            rows.append(
                {
                    "Hora (UTC)": str(d.get("ts", ""))[:19].replace("T", " "),
                    "Par": d.get("pair", ""),
                    "Cenário": d.get("scenario", ""),
                    "Nível": LEVEL_BADGE.get(d.get("level", ""), d.get("level", "")),
                    "Direção": str(d.get("direction", "")).upper(),
                    "Confiança": f"{d['confidence']*100:.1f}%" if d.get("confidence") is not None else "—",
                    "Stake %": d.get("stake_pct", 0) or "—",
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info(
            "Nenhuma decisão registrada ainda. Use 'Pensar agora' acima ou rode "
            "`scripts/doug_decide.py` no terminal."
        )

    st.divider()

    # ── Radar de noticias ──
    st.subheader("📰 Radar de Notícias (filtro anti-manipulação)")
    news = None
    if NEWS_PATH.exists():
        try:
            news = json.loads(NEWS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            news = None
    if news:
        st.caption(
            f"Snapshot: {str(news.get('fetched_at', ''))[:19].replace('T', ' ')} UTC · "
            "risco ≥ 0.70 = notícia quente → Doug não opera pares sensíveis (cripto/forex). "
            "Pares R_* são sintéticos e imunes."
        )
        cols = st.columns(max(1, len(news.get("summary", {}))))
        for col, (topic, s) in zip(cols, (news.get("summary") or {}).items()):
            risk = float(s.get("risk", 0))
            icon = "🔴" if risk >= 0.7 else ("🟡" if risk >= 0.4 else "🟢")
            with col:
                st.metric(f"{icon} {topic.upper()}", f"risco {risk:.2f}", f"viés {s.get('bias', 0):+.2f}")
                if s.get("top_headline"):
                    st.caption(f"“{s['top_headline'][:110]}”")
    else:
        st.info("Sem snapshot de notícias. Rode `scripts/fetch_news.py` (o autocycle faz isso todo dia).")

    st.divider()

    # ── Conhecimento acumulado (scorecard do backtest) ──
    st.subheader("📚 Conhecimento acumulado (backtest M38)")
    scorecard = _load_scorecard()
    if scorecard:
        p = scorecard.get("params", {})
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Trades de aprendizado", scorecard.get("total_learning_trades", 0))
        k2.metric("Buckets avaliados", scorecard.get("buckets", 0))
        k3.metric("WR geral (sem filtro)", f"{scorecard.get('overall_win_rate', 0)*100:.1f}%")
        k4.metric("Aprovados no gate", len(scorecard.get("gate_approved_buckets", [])))
        st.caption(
            f"Última execução: {str(scorecard.get('ran_at', ''))[:19].replace('T', ' ')} UTC · "
            f"{p.get('candles', '?')} candles × {p.get('granularity_sec', '?')}s · "
            f"horizonte {p.get('horizon_candles', '?')} candles"
        )
        top = scorecard.get("top_buckets", [])
        if top:
            df = pd.DataFrame(top)
            df["win_rate"] = (df["win_rate"] * 100).round(1)
            st.dataframe(
                df.rename(
                    columns={
                        "strategy_id": "Estratégia",
                        "pair": "Par",
                        "scenario": "Cenário",
                        "win_rate": "WR %",
                        "expectancy_pct": "Expectancy %",
                        "trades": "Trades",
                        "wins": "Vitórias",
                        "losses": "Derrotas",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Nenhum backtest registrado. Rode `scripts/run_backtest.py --pairs 10 --candles 800`.")
