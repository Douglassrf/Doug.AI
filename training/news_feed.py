"""Radar de noticias reais — alimenta o News Intelligence Servo (M33) e o
cerebro de decisao com manchetes de verdade, sem precisar de chave de API.

Fontes: RSS publicos (Google News por topico + CoinDesk). O texto das
manchetes NAO e armazenado alem do titulo/fonte/data (uso informativo).

Pontuacao por lexico (deterministica, auditavel, offline nos testes):
  sentiment_score  -1..+1  — palavras de alta vs. baixa
  impact_score      0..1   — termos de evento relevante (Fed, ETF, hack...)
  source_confidence 0..1   — confianca fixa por fonte

O snapshot vai para data/news_snapshot.json com resumo por topico:
  bias  — sentimento medio ponderado por impacto (-1..+1)
  risk  — maior impacto entre manchetes recentes (0..1)

Filosofia anti-manipulacao: noticia de alto impacto = janela de movimento
erratico/manipulavel. Nessas horas o Doug NAO opera — ele observa.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
NEWS_SNAPSHOT_PATH = DATA / "news_snapshot.json"

# Snapshot vale por este periodo; depois disso o cerebro ignora (dados velhos)
SNAPSHOT_TTL_HOURS = 6
# Manchete conta como "recente" para o risco por este periodo
RECENT_HOURS = 12

FEEDS: tuple[tuple[str, str, str, float], ...] = (
    # (topico, nome_fonte, url, confianca_da_fonte)
    ("crypto", "GoogleNews", "https://news.google.com/rss/search?q=bitcoin+OR+crypto+market&hl=en-US&gl=US&ceid=US:en", 0.6),
    ("crypto", "CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", 0.8),
    ("macro", "GoogleNews", "https://news.google.com/rss/search?q=federal+reserve+OR+inflation+OR+interest+rates&hl=en-US&gl=US&ceid=US:en", 0.6),
    ("forex", "GoogleNews", "https://news.google.com/rss/search?q=forex+market+OR+dollar+euro&hl=en-US&gl=US&ceid=US:en", 0.6),
)

# Lexico simples e auditavel (ingles — fontes internacionais)
BULLISH_WORDS = (
    "surge", "rally", "soar", "record high", "all-time high", "jump", "gain",
    "bullish", "approval", "approve", "adoption", "breakout", "recovery",
    "rebound", "rate cut", "cuts rates", "easing", "optimism", "buy",
)
BEARISH_WORDS = (
    "crash", "plunge", "tumble", "slump", "drop", "fall", "sink", "bearish",
    "selloff", "sell-off", "fear", "panic", "liquidation", "hack", "exploit",
    "fraud", "lawsuit", "ban", "rate hike", "hikes rates", "recession",
    "inflation rises", "default", "collapse", "warning",
)
HIGH_IMPACT_TERMS = (
    "fed", "federal reserve", "fomc", "rate decision", "interest rate",
    "cpi", "inflation", "payroll", "nonfarm", "etf", "sec", "regulation",
    "hack", "exploit", "bankrupt", "collapse", "war", "sanctions",
    "halving", "crash", "emergency", "intervention",
)


def _score_sentiment(title: str) -> float:
    t = title.lower()
    bull = sum(1 for w in BULLISH_WORDS if w in t)
    bear = sum(1 for w in BEARISH_WORDS if w in t)
    if bull == bear == 0:
        return 0.0
    return max(-1.0, min(1.0, (bull - bear) / max(bull + bear, 1)))


def _score_impact(title: str) -> float:
    t = title.lower()
    hits = sum(1 for w in HIGH_IMPACT_TERMS if w in t)
    return min(1.0, hits * 0.35)


def _parse_rss(xml_text: str, source: str, confidence: float, limit: int = 15) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        pub_raw = (item.findtext("pubDate") or "").strip()
        published = None
        if pub_raw:
            try:
                published = parsedate_to_datetime(pub_raw).astimezone(timezone.utc).isoformat()
            except (TypeError, ValueError):
                published = None
        # Google News costuma anexar " - Fonte" ao titulo
        clean = re.sub(r"\s+-\s+[^-]{2,40}$", "", title)
        out.append(
            {
                "title": clean[:220],
                "source": source,
                "published": published,
                "sentiment_score": _score_sentiment(clean),
                "impact_score": _score_impact(clean),
                "source_confidence": confidence,
            }
        )
        if len(out) >= limit:
            break
    return out


def _fetch_url(url: str, timeout: int = 15) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": "DougAI-NewsRadar/1.0 (research; paper trading)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _is_recent(published: str | None, hours: int = RECENT_HOURS) -> bool:
    if not published:
        return True  # sem data: trata como recente por prudencia
    try:
        dt = datetime.fromisoformat(published)
    except ValueError:
        return True
    age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0
    return 0 <= age_h <= hours


def summarize_topic(headlines: list[dict[str, Any]]) -> dict[str, Any]:
    """Resumo por topico: bias (sentimento medio ponderado) e risk (pico de impacto)."""
    recent = [h for h in headlines if _is_recent(h.get("published"))]
    if not recent:
        return {"bias": 0.0, "risk": 0.0, "recent_count": 0, "top_headline": None}
    weights = [max(0.1, h["impact_score"]) * h["source_confidence"] for h in recent]
    total_w = sum(weights) or 1.0
    bias = sum(h["sentiment_score"] * w for h, w in zip(recent, weights)) / total_w
    risk = max(h["impact_score"] for h in recent)
    top = max(recent, key=lambda h: h["impact_score"])
    return {
        "bias": round(bias, 3),
        "risk": round(risk, 3),
        "recent_count": len(recent),
        "top_headline": top["title"],
    }


def fetch_news_snapshot(save: bool = True) -> dict[str, Any]:
    """Busca todas as fontes e monta o snapshot por topico."""
    topics: dict[str, list[dict[str, Any]]] = {}
    fetched_sources = failed_sources = 0
    for topic, source, url, conf in FEEDS:
        xml_text = _fetch_url(url)
        if not xml_text:
            failed_sources += 1
            continue
        items = _parse_rss(xml_text, source, conf)
        if items:
            fetched_sources += 1
            topics.setdefault(topic, []).extend(items)
        else:
            failed_sources += 1

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "sources_ok": fetched_sources,
        "sources_failed": failed_sources,
        "summary": {t: summarize_topic(hs) for t, hs in topics.items()},
        "topics": topics,
    }
    if save:
        NEWS_SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        NEWS_SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snapshot


def load_news_snapshot(max_age_hours: float = SNAPSHOT_TTL_HOURS) -> dict[str, Any] | None:
    """Snapshot salvo, ou None se inexistente/vencido."""
    if not NEWS_SNAPSHOT_PATH.exists():
        return None
    try:
        snap = json.loads(NEWS_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        fetched = datetime.fromisoformat(snap["fetched_at"])
        age_h = (datetime.now(timezone.utc) - fetched).total_seconds() / 3600.0
        if age_h > max_age_hours:
            return None
        return snap
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return None


def topic_for_pair(pair: str) -> str | None:
    """Mapeia par -> topico de noticias. Indices sinteticos (R_*) sao imunes."""
    p = pair.lower()
    if p.startswith("cry"):
        return "crypto"
    if p.startswith("frx"):
        # Pares de moeda respondem a macro (juros/inflacao) e ao proprio forex
        return "macro"
    return None
