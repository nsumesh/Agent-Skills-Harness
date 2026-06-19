"""Thin wrapper that exposes core.checks.run_technical_checks at the MCP tool boundary."""

from __future__ import annotations

from core import checks
from core.schema import TechCheckRow


def run_technical_checks(url: str, *, enable_psi: bool = True) -> list[TechCheckRow]:
    return checks.run_technical_checks(url, enable_psi=enable_psi)
