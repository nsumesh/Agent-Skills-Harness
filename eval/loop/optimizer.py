"""Propose-evaluate-gate loop: accepts a directive only if it lifts the held-out store without regressing the trained one."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.eval_api import score_report
from eval import config
from eval.loop.state import IterationRecord
from eval.loop.writer import generate, render_prompt

EPS = 0.001


def held_out_gate(best_trained, best_holdout, cand_trained, cand_holdout, *, eps: float = EPS) -> bool:
    """Returns True only if the candidate improves held-out score and does not regress trained score."""
    return cand_holdout > best_holdout + eps and cand_trained >= best_trained - eps


@dataclass
class OptimizerOutcome:
    current: list
    base_trained: object   # ScoreReport
    base_holdout: object
    final_trained: object
    final_holdout: object
    best_trained: float
    best_holdout: float
    records: list = field(default_factory=list)
    stopped_early: bool = False


def optimize(
    train_slug: str,
    holdout_slug: str,
    *,
    writer_client,
    judge,
    base_directives,
    candidates,
    max_iters: int = 4,
    patience: int = 2,
    eps: float = EPS,
) -> OptimizerOutcome:
    def evaluate(slug: str, directives) -> object:
        report = generate(render_prompt(directives), config.bundle_dir(slug), client=writer_client)
        return score_report(report, config.bundle_dir(slug), judge=judge)

    current = list(base_directives)
    base_tr = evaluate(train_slug, current)
    base_ho = evaluate(holdout_slug, current)
    best_tr, best_ho = base_tr.combined_score, base_ho.combined_score
    final_tr, final_ho = base_tr, base_ho

    records, consecutive_rejects, stopped = [], 0, False
    for i, candidate in enumerate(candidates[:max_iters], start=1):
        trial = current + [candidate]
        tr = evaluate(train_slug, trial)
        ho = evaluate(holdout_slug, trial)
        accept = held_out_gate(best_tr, best_ho, tr.combined_score, ho.combined_score, eps=eps)
        if accept:
            reason = f"held-out {ho.combined_score:.3f} > {best_ho:.3f}, trained held"
            current, best_tr, best_ho = trial, tr.combined_score, ho.combined_score
            final_tr, final_ho = tr, ho
            consecutive_rejects = 0
        else:
            reason = "rejected: held-out did not improve or trained regressed"
            consecutive_rejects += 1
        records.append(IterationRecord(
            iteration=i, directive_added=candidate,
            trained_score=round(tr.combined_score, 3), holdout_score=round(ho.combined_score, 3),
            accepted=accept, reason=reason,
        ))
        if consecutive_rejects >= patience:
            stopped = True
            break

    return OptimizerOutcome(
        current=current, base_trained=base_tr, base_holdout=base_ho,
        final_trained=final_tr, final_holdout=final_ho,
        best_trained=best_tr, best_holdout=best_ho, records=records, stopped_early=stopped,
    )
