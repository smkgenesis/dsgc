from __future__ import annotations

import argparse
import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from baselines.retrieval_only import RetrievalOnlyPolicy
from config import DSGCConfig
from benchmarking.benchmark_v2 import BUILDERS_V2, CalibrationScenario, generate_calibration_scenario
from benchmarking.evaluator import answer_accuracy, full_chain_retention, prerequisite_retention
from benchmarking.policy import MinimalDSGCPolicy


REPO_ROOT = Path(__file__).resolve().parents[2]


def create_policy(method: str, budget_tokens: int, encoder_type: str):
    config = DSGCConfig(
        l1_budget=budget_tokens,
        lambda_pi=1.0,
        gamma=0.0,
        density_exponent=0.0,
        relevance_temperature=0.25,
        encoder_type=encoder_type,
    )
    if method == "retrieval_only":
        return RetrievalOnlyPolicy(config)
    if method == "dsgc_no_graph":
        return MinimalDSGCPolicy(config, use_graph=False)
    if method == "dsgc":
        return MinimalDSGCPolicy(config, use_graph=True)
    raise ValueError(f"Unknown method: {method}")


def _find_block_text(blocks: list[dict[str, str]], block_id: str) -> str:
    for block in blocks:
        if block["id"] == block_id:
            return block["text"]
    raise KeyError(block_id)


def _retained_map(retained_blocks) -> dict[str, str]:
    return {block.block_id: block.raw_text for block in retained_blocks}


def predict_answer(retained_blocks, scenario: CalibrationScenario) -> str:
    retained_map = _retained_map(retained_blocks)
    if not set(scenario.chain).issubset(retained_map):
        return "unknown"

    task_type = scenario.metadata.get("task_type")
    if task_type == "numeric_allow":
        left = scenario.metadata.get("cost", scenario.metadata.get("observed_burst"))
        if left is None:
            return "unknown"
        if "percent" in scenario.metadata and "budget" in scenario.metadata:
            threshold = int(int(scenario.metadata["budget"]) * int(scenario.metadata["percent"]) / 100)
            return "yes" if int(left) <= threshold else "no"
        if "burst_limit" in scenario.metadata:
            return "yes" if int(left) <= int(scenario.metadata["burst_limit"]) else "no"
        return "unknown"

    if task_type == "permission":
        return "yes" if bool(scenario.metadata.get("can_delete", scenario.metadata.get("title") == "backup admin")) else "no"

    if task_type == "partner_route":
        return "yes" if bool(scenario.metadata.get("direct_allowed")) else "no"

    return "unknown"


def _extract_debug(policy, scenario: CalibrationScenario) -> dict[str, object]:
    debug = getattr(policy, "last_step_debug", {}) or {}
    rank_order = debug.get("rank_order", [])
    score_map = debug.get("scores", {})
    propagated_map = debug.get("propagated", {})
    selected_ids = set(debug.get("selected_ids", []))
    chain_block_ranks = {
        block_id: (rank_order.index(block_id) + 1 if block_id in rank_order else None)
        for block_id in scenario.chain
    }
    chain_block_scores = {
        block_id: round(float(score_map.get(block_id, 0.0)), 6)
        for block_id in scenario.chain
    }
    chain_block_propagation = {
        block_id: round(float(propagated_map.get(block_id, 0.0)), 6)
        for block_id in scenario.chain
    }
    top_non_chain_id = None
    for block_id in rank_order:
        if block_id not in set(scenario.chain):
            top_non_chain_id = block_id
            break
    displaced_chain_blocks = [block_id for block_id in scenario.chain if block_id not in selected_ids]
    return {
        "chain_block_ranks": chain_block_ranks,
        "chain_block_scores": chain_block_scores,
        "chain_block_propagation": chain_block_propagation,
        "top_non_chain_score": round(float(score_map.get(top_non_chain_id, 0.0)), 6) if top_non_chain_id else 0.0,
        "top_non_chain_id": top_non_chain_id,
        "displaced_chain_blocks": displaced_chain_blocks,
        "selected_honeypot_count": sum(1 for block_id in selected_ids if block_id.startswith("h")),
    }


def run_single(
    method: str,
    scenario: CalibrationScenario,
    budget_multiplier: float,
    encoder_type: str,
) -> dict:
    chain_token_mass = sum(max(len(_find_block_text(scenario.blocks, block_id).split()), 1) for block_id in scenario.chain)
    budget_tokens = max(chain_token_mass, math.ceil(chain_token_mass * budget_multiplier))
    total_tokens = sum(max(len(block["text"].split()), 1) for block in scenario.blocks)

    policy = create_policy(method, budget_tokens, encoder_type)
    dependency_map: dict[str, list[str]] = {}
    for dependent, prerequisite in scenario.dependencies:
        dependency_map.setdefault(dependent, []).append(prerequisite)

    for block in scenario.blocks:
        policy.ingest(
            block["text"],
            block["id"],
            dependencies=dependency_map.get(block["id"], []),
            pin=False,
        )

    retained = policy.step(scenario.query)
    retained_ids = {block.block_id for block in retained}
    predicted_answer = predict_answer(retained, scenario)
    full_chain = full_chain_retention(retained_ids, scenario.chain)
    answer_acc_value = answer_accuracy(predicted_answer, scenario.answer)
    return {
        "prereq_retention": prerequisite_retention(retained_ids, scenario.prerequisite_ids),
        "full_chain_retention": full_chain,
        "answer_acc": answer_acc_value,
        "retained_ids": sorted(retained_ids),
        "selected_block_count": len(retained),
        "budget_tokens": budget_tokens,
        "total_tokens": total_tokens,
        "chain_token_mass": chain_token_mass,
        "budget_chain_ratio": round(budget_tokens / max(chain_token_mass, 1), 4),
        "full_chain_failure": int(full_chain < 1.0),
        "answer_failure": int(answer_acc_value < 1.0),
        "answer_full_chain_disagreement": int(answer_acc_value != full_chain),
        **_extract_debug(policy, scenario),
    }


def _mean_std(values: list[float]) -> dict[str, float]:
    return {
        "mean": round(statistics.mean(values), 4),
        "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
    }


def _aggregate_rows(rows: list[dict], group_keys: tuple[str, ...]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row[key] for key in group_keys)].append(row)

    aggregated: list[dict] = []
    for key in sorted(buckets):
        bucket = buckets[key]
        summary = {group_key: value for group_key, value in zip(group_keys, key)}
        for field in (
            "prereq_retention",
            "full_chain_retention",
            "answer_acc",
            "selected_block_count",
            "chain_token_mass",
            "budget_chain_ratio",
            "selected_honeypot_count",
        ):
            summary[field] = _mean_std([row[field] for row in bucket])
        summary["runs"] = len(bucket)
        summary["full_chain_failure_count"] = sum(row["full_chain_failure"] for row in bucket)
        summary["top_non_chain_ids"] = dict(
            sorted(
                ((block_id, sum(1 for row in bucket if row["top_non_chain_id"] == block_id))
                 for block_id in {row["top_non_chain_id"] for row in bucket if row["top_non_chain_id"]}),
                key=lambda item: (-item[1], item[0]),
            )
        )
        aggregated.append(summary)
    return aggregated


def _lookup_mean(rows: list[dict], **filters) -> float | None:
    for row in rows:
        if all(row[key] == value for key, value in filters.items()):
            return row["full_chain_retention"]["mean"]
    return None


def _pairwise_deltas(rows: list[dict], base_keys: tuple[str, ...]) -> list[dict]:
    deltas: list[dict] = []
    seen: set[tuple] = set()
    methods = ("retrieval_only", "dsgc_no_graph", "dsgc")
    for row in rows:
        key = tuple(row[field] for field in base_keys)
        if key in seen:
            continue
        seen.add(key)
        base = {field: value for field, value in zip(base_keys, key)}
        scores = {method: _lookup_mean(rows, **base, method=method) for method in methods}
        if any(score is None for score in scores.values()):
            continue
        deltas.append(
            {
                **base,
                **{f"{method}_full_chain_mean": scores[method] for method in methods},
                "dsgc_minus_retrieval_only": round(scores["dsgc"] - scores["retrieval_only"], 4),
                "dsgc_minus_no_graph": round(scores["dsgc"] - scores["dsgc_no_graph"], 4),
            }
        )
    return deltas


def _control_acceptance(summary_rows: list[dict]) -> list[dict]:
    decisions: list[dict] = []
    for row in summary_rows:
        if row["regime"] != "control" or row["method"] != "retrieval_only":
            continue
        decisions.append(
            {
                "template": row["template"],
                "encoder_type": row["encoder_type"],
                "total_blocks": row["total_blocks"],
                "chain_depth": row["chain_depth"],
                "honeypot_count": row["honeypot_count"],
                "honeypot_strength": row["honeypot_strength"],
                "budget_multiplier": row["budget_multiplier"],
                "passes_control_threshold": row["full_chain_retention"]["mean"] >= 0.9,
                "retrieval_full_chain_mean": row["full_chain_retention"]["mean"],
            }
        )
    return decisions


def _target_acceptance(summary_rows: list[dict], delta_rows: list[dict]) -> list[dict]:
    decisions: list[dict] = []
    for row in delta_rows:
        regime = row["regime"]
        if regime != "target":
            continue
        decisions.append(
            {
                "template": row["template"],
                "encoder_type": row["encoder_type"],
                "total_blocks": row["total_blocks"],
                "chain_depth": row["chain_depth"],
                "honeypot_count": row["honeypot_count"],
                "honeypot_strength": row["honeypot_strength"],
                "budget_multiplier": row["budget_multiplier"],
                "passes_graph_signal": row["dsgc_minus_no_graph"] > 0.0,
                "dsgc_minus_retrieval_only": row["dsgc_minus_retrieval_only"],
                "dsgc_minus_no_graph": row["dsgc_minus_no_graph"],
            }
        )
    return decisions


def run_grid(
    *,
    protocol_id: str,
    templates: list[str],
    methods: list[str],
    encoder_types: list[str],
    seeds: list[int],
    total_blocks_grid: list[int],
    budget_multipliers: list[float],
    chain_depths: list[int],
    honeypot_counts: list[int],
    honeypot_strength: str,
) -> list[dict]:
    results: list[dict] = []
    for method, template, encoder_type, total_blocks, budget_multiplier, chain_depth, honeypot_count, seed in itertools.product(
        methods,
        templates,
        encoder_types,
        total_blocks_grid,
        budget_multipliers,
        chain_depths,
        honeypot_counts,
        seeds,
    ):
        scenario = generate_calibration_scenario(
            template=template,
            seed=seed,
            total_blocks=total_blocks,
            chain_depth=chain_depth,
            honeypot_count=honeypot_count,
            honeypot_strength=honeypot_strength,
        )
        metrics = run_single(method, scenario, budget_multiplier, encoder_type)
        results.append(
            {
                "protocol_id": protocol_id,
                "encoder_type": encoder_type,
                "method": method,
                "template": template,
                "regime": scenario.regime,
                "seed": seed,
                "total_blocks": total_blocks,
                "budget_multiplier": budget_multiplier,
                "chain_depth": chain_depth,
                "honeypot_count": honeypot_count,
                "honeypot_strength": honeypot_strength,
                "query": scenario.query,
                "ground_truth_answer": scenario.answer,
                **metrics,
            }
        )
    return results


def build_summary(protocol_id: str, rows: list[dict]) -> dict:
    per_setting = _aggregate_rows(
        rows,
        (
            "encoder_type",
            "method",
            "template",
            "regime",
            "total_blocks",
            "chain_depth",
            "honeypot_count",
            "honeypot_strength",
            "budget_multiplier",
        ),
    )
    by_regime = _aggregate_rows(
        rows,
        (
            "encoder_type",
            "method",
            "regime",
            "total_blocks",
            "chain_depth",
            "honeypot_count",
            "honeypot_strength",
            "budget_multiplier",
        ),
    )
    pairwise = _pairwise_deltas(
        per_setting,
        (
            "encoder_type",
            "template",
            "regime",
            "total_blocks",
            "chain_depth",
            "honeypot_count",
            "honeypot_strength",
            "budget_multiplier",
        ),
    )
    return {
        "protocol_id": protocol_id,
        "experiment": "final_v2_calibration",
        "per_setting": per_setting,
        "by_regime": by_regime,
        "pairwise_deltas": pairwise,
        "control_acceptance": _control_acceptance(per_setting),
        "target_acceptance": _target_acceptance(per_setting, pairwise),
    }


def write_json(path: Path, payload: dict | list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol-id", default="final_v2_calibration")
    parser.add_argument("--raw-output", default="results/final_v2_calibration_raw.json")
    parser.add_argument("--summary-output", default="results/final_v2_calibration_summary.json")
    parser.add_argument("--templates", nargs="+", default=list(BUILDERS_V2.keys()))
    parser.add_argument("--methods", nargs="+", default=["retrieval_only", "dsgc_no_graph", "dsgc"])
    parser.add_argument("--encoders", nargs="+", default=["frozen", "sentence"])
    parser.add_argument("--seed-count", type=int, default=15)
    parser.add_argument("--total-blocks", nargs="+", type=int, default=[20, 32])
    parser.add_argument("--budget-multipliers", nargs="+", type=float, default=[1.0, 1.5, 2.0, 3.0, 5.0])
    parser.add_argument("--chain-depths", nargs="+", type=int, default=[2, 3])
    parser.add_argument("--honeypot-counts", nargs="+", type=int, default=[2, 4, 6])
    parser.add_argument("--honeypot-strength", default="medium", choices=["easy", "medium", "hard"])
    args = parser.parse_args()

    rows = run_grid(
        protocol_id=args.protocol_id,
        templates=args.templates,
        methods=args.methods,
        encoder_types=args.encoders,
        seeds=list(range(args.seed_count)),
        total_blocks_grid=args.total_blocks,
        budget_multipliers=args.budget_multipliers,
        chain_depths=args.chain_depths,
        honeypot_counts=args.honeypot_counts,
        honeypot_strength=args.honeypot_strength,
    )
    summary = build_summary(args.protocol_id, rows)
    write_json(REPO_ROOT / args.raw_output, rows)
    write_json(REPO_ROOT / args.summary_output, summary)


if __name__ == "__main__":
    main()
