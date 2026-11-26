"""Prometheus Observability Exporters for Agent Latency, TTS TTFA, Tokens/Over, Questions/Min & Errors."""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest

REGISTRY = CollectorRegistry()

AGENT_LATENCY = Histogram(
    "commentary_agent_latency_seconds",
    "Latency of multi-agent ball commentary generation",
    registry=REGISTRY,
)
TTS_TTFA = Histogram(
    "tts_time_to_first_audio_seconds",
    "Time to first audio byte from TTS synthesis",
    registry=REGISTRY,
)
TOKENS_PER_OVER = Counter(
    "commentary_tokens_generated_total",
    "Cumulative commentary tokens generated across overs",
    registry=REGISTRY,
)
VIEWER_QUESTIONS = Counter(
    "viewer_questions_total",
    "Total viewer text and voice questions answered",
    ["modality"],
    registry=REGISTRY,
)
COMMENTARY_ERRORS = Counter(
    "commentary_errors_total",
    "Total agent or speech pipeline errors",
    registry=REGISTRY,
)


def record_ball_metrics(agent_latency_s: float, ttfa_s: float, tokens: int) -> None:
    AGENT_LATENCY.observe(agent_latency_s)
    TTS_TTFA.observe(ttfa_s)
    TOKENS_PER_OVER.inc(max(1, tokens))


def record_question_metric(modality: str = "text") -> None:
    VIEWER_QUESTIONS.labels(modality=modality).inc()


def render_prometheus_metrics() -> bytes:
    return generate_latest(REGISTRY)
