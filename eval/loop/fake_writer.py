"""Deterministic stand-in for the Anthropic writer: degrades the base report for each missing quality directive, so a richer prompt yields a higher score. The `overfit` directive damages only the held-out store to model a non-generalizing change."""

from __future__ import annotations

import copy
import json
import re

from eval.calibration.ablations import (
    break_a_citation,
    drop_a_pillar,
    overconfident_new_page,
    vague_hypothesis,
)
from eval.loop.writer import ALL_DIRECTIVES, QUALITY_DIRECTIVES

# Damage function applied per quality directive when that directive is absent from the prompt.
_DAMAGE = {
    "cite": break_a_citation,
    "pillars": drop_a_pillar,
    "specific": vague_hypothesis,
    "calibrate": overconfident_new_page,
}
TRAINED_SLUG = "gingerpeople"  # only store the "overfit" directive is allowed to benefit


class _Block:
    def __init__(self, text: str):
        self.text = text


class _Response:
    def __init__(self, text: str):
        self.content = [_Block(text)]


class _Messages:
    def __init__(self, outer: FakeWriterAnthropic):
        self._outer = outer

    def create(self, *, system=None, messages=None, **_kw) -> _Response:
        return self._outer._respond(system)


class FakeWriterAnthropic:
    def __init__(self, base_reports: dict):
        self.base_reports = base_reports
        self.messages = _Messages(self)

    @classmethod
    def from_samples(cls) -> FakeWriterAnthropic:
        from eval import config

        bases = {
            slug: json.loads((config.SAMPLE_OUTPUT / slug / "report.json").read_text())
            for slug in ("zenrojas", "gingerpeople")
        }
        return cls(bases)

    @staticmethod
    def _flatten(value) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in value)
        return str(value)

    def _respond(self, system) -> _Response:
        text = self._flatten(system)
        slug = re.search(r"SLUG:\s*(\w+)", text)
        slug = slug.group(1) if slug else "zenrojas"
        present = {key for key, directive in ALL_DIRECTIVES.items() if directive in text}

        report = copy.deepcopy(self.base_reports[slug])
        for quality in QUALITY_DIRECTIVES:
            if quality not in present:
                report = _DAMAGE[quality](report)
        if "overfit" in present and slug != TRAINED_SLUG:
            report = break_a_citation(report)  # helps trained, breaks generalization
        return _Response(json.dumps(report))
