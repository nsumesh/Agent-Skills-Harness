"""CLI entry point for the self-improving loop (`make loop`). Uses a real Anthropic writer by default; pass --fake-writer for a fully offline run. Writes results to eval/loop/runs/run_*.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval import config
from eval.loop.cascade import human_queue_count
from eval.loop.optimizer import optimize
from eval.loop.state import OptimizerRun

LOW_AGREEMENT = 0.5
DEFAULT_BASE = ["cite", "pillars"]
DEFAULT_CANDIDATES = ["specific", "calibrate", "overfit"]


def _default_judge():
    from eval.judge.fake import FakeAnthropic
    from eval.judge.judge import run_judge

    client = FakeAnthropic()
    return lambda data, bundle: run_judge(data, bundle, client=client)


def _read_agreement() -> float:
    state = config.REPO_ROOT / "eval" / "calibration" / "calibration_state.json"
    if state.exists():
        return float(json.loads(state.read_text())["agreement"])
    return 0.8


def run_loop(
    train_slug: str = "gingerpeople",
    holdout_slug: str = "zenrojas",
    *,
    writer_client=None,
    judge=None,
    agreement: float | None = None,
    base_directives=None,
    candidates=None,
    out_dir: Path | None = None,
    run_id: str = "latest",
) -> tuple[OptimizerRun, Path]:
    judge = judge or _default_judge()
    agreement = agreement if agreement is not None else _read_agreement()
    base_directives = base_directives or DEFAULT_BASE
    candidates = candidates or DEFAULT_CANDIDATES

    outcome = optimize(
        train_slug, holdout_slug, writer_client=writer_client, judge=judge,
        base_directives=base_directives, candidates=candidates,
    )

    def queue(reports, a):
        return sum(human_queue_count(r, a) for r in reports)

    base_reports = [outcome.base_trained, outcome.base_holdout]
    final_reports = [outcome.final_trained, outcome.final_holdout]

    run = OptimizerRun(
        train_slug=train_slug, holdout_slug=holdout_slug, agreement=agreement,
        accepted_directives=[d for d in outcome.current if d not in base_directives],
        baseline_trained=round(outcome.base_trained.combined_score, 3),
        baseline_holdout=round(outcome.base_holdout.combined_score, 3),
        final_trained=round(outcome.best_trained, 3),
        final_holdout=round(outcome.best_holdout, 3),
        holdout_delta=round(outcome.best_holdout - outcome.base_holdout.combined_score, 3),
        trained_delta=round(outcome.best_trained - outcome.base_trained.combined_score, 3),
        stopped_early=outcome.stopped_early,
        queue_baseline=queue(base_reports, agreement),
        queue_final=queue(final_reports, agreement),
        queue_low_agreement=queue(base_reports, LOW_AGREEMENT),
        queue_high_agreement=queue(base_reports, agreement),
        iterations=outcome.records,
    )

    out_dir = Path(out_dir or (config.REPO_ROOT / "eval" / "loop" / "runs"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"run_{run_id}.json"
    out_path.write_text(run.model_dump_json(indent=2) + "\n")
    return run, out_path


def _print(run: OptimizerRun, path: Path) -> None:
    print("=" * 64)
    print(f"Self-improving loop — train={run.train_slug}  holdout={run.holdout_slug}  agreement={run.agreement}")
    print("=" * 64)
    for r in run.iterations:
        mark = "ACCEPT" if r.accepted else "reject"
        print(f"  iter {r.iteration} +{r.directive_added:<10} trained={r.trained_score:.3f} holdout={r.holdout_score:.3f}  [{mark}]")
    print("-" * 64)
    print(f"  held-out (holdout) {run.baseline_holdout:.3f} -> {run.final_holdout:.3f}  (Δ {run.holdout_delta:+.3f})")
    print(f"  trained            {run.baseline_trained:.3f} -> {run.final_trained:.3f}  (Δ {run.trained_delta:+.3f})")
    print(f"  accepted directives: {run.accepted_directives}")
    print(f"  human queue (optimization): {run.queue_baseline} -> {run.queue_final}")
    print(f"  human queue (agreement {LOW_AGREEMENT} -> {run.agreement}): {run.queue_low_agreement} -> {run.queue_high_agreement}")
    verdict = "PASS" if run.holdout_delta > 0 and run.trained_delta >= -0.001 else "FAIL"
    print(f"  HEADLINE: held-out up, trained not down -> {verdict}")
    print(f"  wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="gingerpeople")
    parser.add_argument("--holdout", default="zenrojas")
    parser.add_argument("--fake-writer", action="store_true", help="fully offline (deterministic) writer")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    writer_client = None
    if args.fake_writer:
        from eval.loop.fake_writer import FakeWriterAnthropic

        writer_client = FakeWriterAnthropic.from_samples()

    run_id = args.run_id
    if run_id is None:
        from datetime import datetime

        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    run, path = run_loop(args.train, args.holdout, writer_client=writer_client, run_id=run_id)
    _print(run, path)


if __name__ == "__main__":
    main()
