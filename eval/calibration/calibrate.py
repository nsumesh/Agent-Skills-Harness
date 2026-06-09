"""Compute judge-vs-human agreement over the calibration set and write calibration_state.json. The escalation_threshold is set equal to agreement."""

from __future__ import annotations

import json
from pathlib import Path

from core.eval_api import score_report
from eval import config
from eval.calibration.ablations import generate_ablations
from eval.judge.rubrics import RUBRIC_VERSION

DIM_FLOOR = 0.6  # any dimension below this fails the report


def verdict(score) -> bool:
    if not score.hard_gate_passed:
        return False
    if score.combined_score < config.PASS_THRESHOLD:
        return False
    return all(d.score >= DIM_FLOOR for d in score.judge)


def build_items(known_good: dict) -> dict:
    return {"known_good": known_good, **generate_ablations(known_good)}


def compute_agreement(judge, known_good: dict, bundle_dir, labels: dict):
    items = build_items(known_good)
    matches, details = 0, {}
    for label in labels["items"]:
        sr = score_report(items[label["name"]], bundle_dir, judge=judge)
        eval_good = verdict(sr)
        agree = eval_good == label["good"]
        matches += agree
        details[label["name"]] = {
            "eval_good": eval_good,
            "label_good": label["good"],
            "match": agree,
            "combined": round(sr.combined_score, 3),
        }
    agreement = matches / len(labels["items"])
    return agreement, details


def write_state(agreement: float, n_items: int, path: Path, *, judge_source: str) -> dict:
    state = {
        "agreement": round(agreement, 4),
        "escalation_threshold": round(agreement, 4),  # set equal to agreement
        "pass_threshold": config.PASS_THRESHOLD,
        "rubric_version": RUBRIC_VERSION,
        "n_items": n_items,
        "judge_source": judge_source,
    }
    Path(path).write_text(json.dumps(state, indent=2) + "\n")
    return state


def _load_labels() -> dict:
    return json.loads((config.REPO_ROOT / "eval" / "calibration" / "labels.json").read_text())


def main(*, live: bool = False) -> None:
    """Regenerate calibration_state.json; offline uses FakeAnthropic (machinery check only), --live uses the real judge."""
    labels = _load_labels()
    known_good = json.loads((config.REPORTS_DIR / "target_report.json").read_text())
    bundle = config.bundle_dir(labels["bundle"])

    if live:
        from eval.judge.judge import run_judge

        judge = lambda data, b: run_judge(data, b)  # noqa: E731
        source = "anthropic"
    else:
        from eval.judge.fake import FakeAnthropic
        from eval.judge.judge import run_judge

        client = FakeAnthropic()
        judge = lambda data, b: run_judge(data, b, client=client)  # noqa: E731
        source = "fake_offline"

    agreement, details = compute_agreement(judge, known_good, bundle, labels)
    out = config.REPO_ROOT / "eval" / "calibration" / "calibration_state.json"
    state = write_state(agreement, len(labels["items"]), out, judge_source=source)
    print(f"agreement={state['agreement']} (source={source}, n={state['n_items']}) -> {out}")
    for name, d in details.items():
        flag = "ok" if d["match"] else "MISMATCH"
        print(f"  {flag:>8}  {name}: eval_good={d['eval_good']} label_good={d['label_good']} combined={d['combined']}")


if __name__ == "__main__":
    import sys

    main(live="--live" in sys.argv)
