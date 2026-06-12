"""Deterministic stand-in for the Anthropic client used by offline tests. Returns rubric-faithful JSON without any network calls."""

from __future__ import annotations

import json
import re


class _Block:
    def __init__(self, text: str):
        self.text = text


class _Response:
    def __init__(self, text: str):
        self.content = [_Block(text)]


class _Messages:
    def __init__(self, outer: FakeAnthropic):
        self._outer = outer

    def create(self, *, system=None, messages=None, **_kw) -> _Response:
        return self._outer._respond(system, messages)


class FakeAnthropic:
    def __init__(self):
        self.messages = _Messages(self)
        self.calls: list[str] = []

    @staticmethod
    def _flatten(value) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in value
            )
        return str(value)

    def _respond(self, system, messages) -> _Response:
        system_text = self._flatten(system)
        user_text = self._flatten(messages[-1]["content"]) if messages else ""
        blob = f"{system_text}\n{user_text}"
        self.calls.append(blob)

        dim_match = re.search(r"DIMENSION\s*=?\s*(\w+)", blob)
        dimension = dim_match.group(1) if dim_match else "groundedness"

        # raw_decode stops after the first complete object, ignoring any trailing rubric text.
        report = {}
        marker = "REPORT_JSON:\n"
        idx = system_text.find(marker)
        if idx != -1:
            try:
                report, _ = json.JSONDecoder().raw_decode(system_text[idx + len(marker):].lstrip())
            except json.JSONDecodeError:
                report = {}

        score, per_item = _heuristic(dimension, report)
        payload = {
            "score": round(score, 3),
            "rationale": f"fake {dimension} judgement",
            "per_item": per_item,
            # High confidence at 0.0 or 1.0; low (0.5) at borderline — matches escalation logic.
            "self_confidence": round(2 * abs(score - 0.5), 3),
        }
        return _Response(json.dumps(payload))


def _heuristic(dimension: str, report: dict) -> tuple[float, list[str]]:
    experiments = report.get("experiments", []) or []
    if not experiments:
        return 0.0, []

    if dimension == "groundedness":
        per, oks = [], 0
        for e in experiments:
            ev = str(e.get("evidence", "")).strip()
            grounded = bool(ev) and (
                ev.startswith("http")
                or "screenshots/" in ev
                or "content/" in ev
                or re.search(r"\.(png|jpe?g|md|json)$", ev) is not None
            )
            oks += grounded
            per.append(f"{e.get('exp_id')}: {'grounded' if grounded else 'ungrounded'}")
        return oks / len(experiments), per

    if dimension == "specificity":
        per, total = [], 0.0
        for e in experiments:
            h = str(e.get("hypothesis", ""))
            words = len(h.split())
            sentences = len([s for s in re.split(r"(?<=[.!?])\s+", h.strip()) if s.strip()])
            specific = sentences >= 2 and (words >= 25 or re.search(r"\d", h) is not None)
            total += 1.0 if specific else 0.3
            per.append(f"{e.get('exp_id')}: {'specific' if specific else 'vague'}")
        return total / len(experiments), per

    if dimension == "calibration":
        per, miscalibrated = [], 0
        for e in experiments:
            surface = f"{e.get('url', '')} {e.get('affected_surface', '')}".lower()
            conf_match = re.search(r"(\d+)", str(e.get("confidence", "0")))
            conf = int(conf_match.group(1)) if conf_match else 0
            is_new = "(new)" in surface or "new page" in surface
            if is_new and conf > 80:
                miscalibrated += 1
                per.append(f"{e.get('exp_id')}: overconfident new page ({conf}%)")
        # One overconfident new page is enough to pull the dimension score down.
        return max(0.2, 1.0 - 0.5 * miscalibrated), per

    return 1.0, []
