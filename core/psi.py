"""PageSpeed Insights v5 client with retries and an honest degrade path.

Order of attempts: PSI API (needs ``PSI_API_KEY``) -> local Lighthouse CLI (if installed)
-> honest "not measured". The result never claims a score it didn't obtain.
"""

from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass

import httpx

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


@dataclass
class PsiResult:
    strategy: str          # "mobile" | "desktop"
    inspected: bool        # did we obtain a real score?
    score: int | None      # 0-100 performance score
    detail: str
    source: str            # "psi" | "lighthouse" | "none"


def _parse_score(data: dict) -> int | None:
    score = (
        data.get("lighthouseResult", {})
        .get("categories", {})
        .get("performance", {})
        .get("score")
    )
    return round(score * 100) if isinstance(score, (int, float)) else None


def run_psi(
    url: str,
    strategy: str = "mobile",
    *,
    api_key: str | None = None,
    retries: int = 2,
    backoff: float = 0.5,
    timeout: float = 60.0,
) -> PsiResult:
    api_key = api_key if api_key is not None else os.getenv("PSI_API_KEY")

    if api_key:
        params = {"url": url, "strategy": strategy, "category": "performance", "key": api_key}
        for attempt in range(retries + 1):
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.get(PSI_ENDPOINT, params=params)
                if resp.status_code == 200:
                    score = _parse_score(resp.json())
                    if score is not None:
                        return PsiResult(
                            strategy, True, score,
                            f"PageSpeed Insights {strategy} performance score {score}.", "psi",
                        )
                    return PsiResult(strategy, False, None, "PSI response had no performance score.", "none")
            except (httpx.HTTPError, ValueError):
                pass
            if attempt < retries and backoff:
                time.sleep(backoff * (2**attempt))

    fallback = _lighthouse_fallback(url, strategy)
    if fallback is not None:
        return fallback

    reason = "no PSI API key configured" if not api_key else "PSI request failed"
    return PsiResult(
        strategy, False, None,
        f"Page speed not measured ({reason}); no local Lighthouse available.", "none",
    )


def _lighthouse_fallback(url: str, strategy: str) -> PsiResult | None:
    """Use a locally installed Lighthouse CLI if present; otherwise return None.

    Kept intentionally conservative: if anything about the local run is uncertain we return
    None so the caller degrades to an honest Warn rather than inventing a number.
    """
    if shutil.which("lighthouse") is None:
        return None
    # A full local Lighthouse run is out of scope for the offline tier; presence of the
    # binary is detected so the scale path is wired, but we do not fabricate a score here.
    return None
