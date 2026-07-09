"""Streamlit — DogEye tip-to-tip LIVE monitor (Douglas watches here)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard.tip_to_tip_live_state import LIVE_PATH, LOG_PATH  # noqa: E402

st.set_page_config(page_title="DogEye LIVE", page_icon="🔴", layout="wide")
st.title("🔴 DogEye — Tip-to-Tip AO VIVO")
st.caption("Atualiza a cada 2 segundos · 1000 operações · Douglas observa aqui")

placeholder = st.empty()

if st.button("Atualizar agora"):
    st.rerun()

if not LIVE_PATH.exists():
    st.warning("Aguardando teste… Peça à equipe para rodar com `--live`")
    st.code(
        'python scripts/tip_to_tip_training.py --certify --operator "NOME" --live',
        language="powershell",
    )
    st.stop()

try:
    data = json.loads(LIVE_PATH.read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError):
    st.error("Arquivo live corrompido ou em uso.")
    st.stop()

status = data.get("status", "?")
operator = data.get("operator") or "—"
done = int(data.get("done", 0))
total = int(data.get("total", 1000))
passed = int(data.get("passed", 0))
failed = int(data.get("failed", 0))
pct = float(data.get("score_pct", 0))
grade = data.get("grade", "—")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Operador", operator)
col2.metric("Progresso", f"{done}/{total}")
col3.metric("Acertos", passed, delta=f"-{failed} perdas" if failed else None, delta_color="inverse")
col4.metric("Score", f"{pct}%", delta=f"Nota {grade}" if grade != "—" else None)

st.progress(min(done / total, 1.0) if total else 0.0)
st.write(f"**Status:** `{status}` · **Missão:** `{data.get('current_mission', '—')}` · **Par:** `{data.get('current_pair', '—')}` · **Run:** {data.get('current_run', 0)}")

if status == "finished":
    st.success(f"Teste concluído — {passed} acertos, {failed} perdas ({pct}%)")

st.subheader("Últimas operações")
for item in data.get("recent", [])[:20]:
    icon = "✅" if item.get("ok") else "❌"
    st.text(f"{icon} {item.get('mission')} · {item.get('pair')} · run {item.get('run')} — {item.get('detail', '')}")

if LOG_PATH.exists():
    with st.expander("Log completo (tail)"):
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
        st.code("\n".join(lines[-80:]), language="text")

st.caption(f"Arquivo: {LIVE_PATH} · atualizado {data.get('updated_at', '?')}")

import time
time.sleep(2)
st.rerun()
