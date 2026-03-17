#!/usr/bin/env python3
"""Gradio Pangram demo app for a Hugging Face Space.

Paste a Pangram API key live, paste text, and inspect:
- overall prediction
- percentage breakdown
- annotated text spans
- flagged windows

No key or text is persisted by this app.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Any
from urllib import error, request

import gradio as gr


API_URL = "https://text.api.pangram.com/v3"

COLOR_MAP = {
    "AI": "#f1b7b0",
    "AI-assisted": "#f2d99c",
    "Human": "#d9e8d1",
    "Neutral": "#ece6d9",
}


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class Window:
    start: int
    end: int
    label: str
    confidence: float | None
    word_count: int | None
    token_length: int | None


def _pretty_label(value: Any) -> str:
    if value is None:
        return "-"
    text = str(value).replace("_", " ").strip()
    return " ".join(part[:1].upper() + part[1:] for part in text.split()) or "-"


def _normalize_label(value: Any) -> str:
    text = str(value or "").lower()
    if "assist" in text:
        return "AI-assisted"
    if "human" in text:
        return "Human"
    if "ai" in text:
        return "AI"
    return "Neutral"


def _post_json(url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"error": raw or exc.reason}
        message = data.get("error") or data.get("detail") or data.get("message") or str(exc)
        raise gr.Error(f"Pangram request failed: {message}") from exc
    except Exception as exc:  # pragma: no cover - network edge cases
        raise gr.Error(f"Pangram request failed: {exc}") from exc


def _extract_windows(raw_windows: Any) -> list[Window]:
    windows: list[Window] = []
    if not isinstance(raw_windows, list):
        return windows

    for item in raw_windows:
        if not isinstance(item, dict):
            continue
        start = max(0, _coerce_int(item.get("start_index", 0), 0))
        end = max(start, _coerce_int(item.get("end_index", start), start))
        confidence = _coerce_float(item.get("confidence"))
        windows.append(
            Window(
                start=start,
                end=end,
                label=_normalize_label(item.get("label")),
                confidence=confidence,
                word_count=_coerce_int(item.get("word_count"), 0) if item.get("word_count") is not None else None,
                token_length=_coerce_int(item.get("token_length"), 0) if item.get("token_length") is not None else None,
            )
        )
    windows.sort(key=lambda w: (w.start, w.end))
    return windows


def _build_highlighted_segments(text: str, windows: list[Window]) -> list[tuple[str, str | None]]:
    if not text:
        return []

    segments: list[tuple[str, str | None]] = []
    cursor = 0

    for window in windows:
        start = min(max(window.start, cursor, 0), len(text))
        end = min(max(window.end, start), len(text))

        if start > cursor:
            segments.append((text[cursor:start], None))

        if end > start:
            segments.append((text[start:end], window.label))
            cursor = end

    if cursor < len(text):
        segments.append((text[cursor:], None))

    if not segments:
        segments.append((text, None))

    return segments


def _percentages_table(raw_percentages: Any) -> list[list[str]]:
    if not isinstance(raw_percentages, dict):
        return []

    rows: list[list[str]] = []
    sortable: list[tuple[str, float]] = []
    for label, value in raw_percentages.items():
        pct = _coerce_float(value)
        if pct is None:
            continue
        sortable.append((str(label), pct))

    for label, pct in sorted(sortable, key=lambda item: item[1], reverse=True):
        rows.append([_pretty_label(label), f"{pct:.1f}%"])
    return rows


def _flagged_windows_table(text: str, windows: list[Window]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, window in enumerate(windows, start=1):
        if window.label not in {"AI", "AI-assisted"}:
            continue
        excerpt = text[window.start:window.end].strip() or "[empty window]"
        confidence = "-" if window.confidence is None else f"{window.confidence:.3f}"
        rows.append([str(index), window.label, confidence, excerpt])
    return rows


def _all_windows_table(text: str, windows: list[Window]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, window in enumerate(windows, start=1):
        excerpt = text[window.start:window.end].strip() or "[empty window]"
        confidence = "-" if window.confidence is None else f"{window.confidence:.3f}"
        word_count = "-" if window.word_count is None else str(window.word_count)
        token_length = "-" if window.token_length is None else str(window.token_length)
        rows.append(
            [
                str(index),
                str(window.start),
                str(window.end),
                window.label,
                confidence,
                word_count,
                token_length,
                excerpt,
            ]
        )
    return rows


def _summary_markdown(result: dict[str, Any], windows: list[Window]) -> str:
    prediction = _pretty_label(result.get("prediction_short") or result.get("prediction"))
    public_link = result.get("public_dashboard_link")
    flagged = sum(1 for window in windows if window.label in {"AI", "AI-assisted"})
    counts = Counter(window.label for window in windows)
    top_label = counts.most_common(1)[0][0] if counts else "-"

    lines = [
        f"**Prediction:** {prediction}",
        f"**Flagged windows:** {flagged} / {len(windows)}",
        f"**Most frequent window label:** {top_label}",
    ]
    if public_link:
        lines.append(f"**Public dashboard:** {public_link}")
    return "\n\n".join(lines)


def analyze_text(api_key: str, text: str, public_dashboard_link: bool) -> tuple[Any, ...]:
    api_key = (api_key or "").strip()
    text = text or ""

    if not api_key:
        raise gr.Error("Paste a Pangram API key first.")
    if not text.strip():
        raise gr.Error("Paste text to analyze first.")

    payload = {
        "text": text,
        "public_dashboard_link": bool(public_dashboard_link),
    }
    result = _post_json(API_URL, api_key, payload)
    windows = _extract_windows(result.get("windows"))
    highlighted = _build_highlighted_segments(text, windows)
    percentages = _percentages_table(result.get("percentages"))
    flagged = _flagged_windows_table(text, windows)
    all_windows = _all_windows_table(text, windows)
    summary = _summary_markdown(result, windows)

    return (
        summary,
        highlighted,
        percentages,
        flagged,
        all_windows,
        result,
    )


def clear_outputs() -> tuple[Any, ...]:
    return ("", "", False, "", [], [], [], {})


with gr.Blocks(title="Pangram Live Demo") as demo:
    gr.Markdown(
        """
        # Pangram Live Demo

        Paste a Pangram API key and a text sample to inspect flagged spans live.
        The key is used only for the current request and is not stored by the app.
        Pangram controls the actual window segmentation. This app exposes all returned windows and
        their boundaries, but does not invent finer sub-windows that Pangram itself did not return.
        """
    )

    with gr.Row():
        with gr.Column(scale=4):
            api_key = gr.Textbox(
                label="Pangram API key",
                type="password",
                placeholder="Paste live API key here",
            )
            source_text = gr.Textbox(
                label="Text to analyze",
                lines=16,
                placeholder="Paste text here...",
            )
            public_link = gr.Checkbox(
                label="Request public dashboard link",
                value=False,
            )
            with gr.Row():
                analyze = gr.Button("Analyze", variant="primary")
                clear = gr.Button("Clear")

        with gr.Column(scale=5):
            summary = gr.Markdown(label="Summary")
            annotated = gr.HighlightedText(
                label="Annotated output",
                color_map=COLOR_MAP,
                combine_adjacent=True,
                show_legend=True,
                show_inline_category=False,
            )
            percentages = gr.Dataframe(
                headers=["Label", "Percentage"],
                datatype=["str", "str"],
                row_count=(0, "dynamic"),
                col_count=(2, "fixed"),
                label="Percentages",
                wrap=True,
            )
            flagged = gr.Dataframe(
                headers=["#", "Label", "Confidence", "Excerpt"],
                datatype=["str", "str", "str", "str"],
                row_count=(0, "dynamic"),
                col_count=(4, "fixed"),
                label="Flagged windows",
                wrap=True,
            )
            all_windows = gr.Dataframe(
                headers=["#", "Start", "End", "Label", "Confidence", "Words", "Tokens", "Excerpt"],
                datatype=["str", "str", "str", "str", "str", "str", "str", "str"],
                row_count=(0, "dynamic"),
                col_count=(8, "fixed"),
                label="All returned windows",
                wrap=True,
            )
            raw_json = gr.JSON(label="Raw Pangram response")

    analyze.click(
        fn=analyze_text,
        inputs=[api_key, source_text, public_link],
        outputs=[summary, annotated, percentages, flagged, all_windows, raw_json],
        api_name=False,
    )

    clear.click(
        fn=clear_outputs,
        inputs=[],
        outputs=[api_key, source_text, public_link, summary, percentages, flagged, all_windows, raw_json, annotated],
        api_name=False,
    )


if __name__ == "__main__":
    demo.launch()
