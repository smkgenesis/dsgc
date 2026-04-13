from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

from baselines.retrieval_only import RetrievalOnlyPolicy
from baselines.sliding_window import SlidingWindowPolicy
from config import DSGCConfig
from benchmarking.benchmark import BUILDERS, MinimalScenario, TEMPLATES, generate_minimal_scenario
from benchmarking.evaluator import answer_accuracy, full_chain_retention, prerequisite_retention
from benchmarking.policy import MinimalDSGCPolicy


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL_PATH = REPO_ROOT / "protocols" / "final_experiment_v1.json"
SUMMARY_METRIC_FIELDS = (
    "prereq_retention",
    "full_chain_retention",
    "answer_acc",
    "selected_block_count",
    "chain_token_mass",
    "budget_chain_ratio",
)


def load_protocol(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _protocol_output_path(protocol: dict, key: str) -> Path:
    return REPO_ROOT / protocol["outputs"][key]


def create_policy(method: str, budget_tokens: int, encoder_type: str):
    config = DSGCConfig(
        l1_budget=budget_tokens,
        lambda_pi=1.0,
        gamma=0.0,
        density_exponent=0.0,
        relevance_temperature=0.25,
        encoder_type=encoder_type,
    )
    if method == "sliding_window":
        return SlidingWindowPolicy(config)
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


def predict_answer(retained_blocks, scenario: MinimalScenario) -> str:
    retained_map = _retained_map(retained_blocks)
    if not set(scenario.chain).issubset(retained_map):
        return "unknown"

    c1 = retained_map["c1"]
    c2 = retained_map["c2"]
    query = scenario.query

    if scenario.template == "budget_control":
        budget_match = re.search(r"backup budget of (\d+) credits", c1.lower())
        percent_match = re.search(r"within (\d+) percent", c2.lower())
        cost_match = re.search(r"costs (\d+) credits", query.lower())
        if not budget_match or not percent_match or not cost_match:
            return "unknown"
        budget = int(budget_match.group(1))
        percent = int(percent_match.group(1))
        cost = int(cost_match.group(1))
        return "yes" if cost <= int(budget * percent / 100) else "no"

    if scenario.template in {"permission_control", "opaque_role_target"}:
        if "may delete production backups" in c2.lower():
            return "yes"
        if "may not delete" in c2.lower():
            return "no"
        return "unknown"

    if scenario.template == "opaque_profile_target":
        if "may send telemetry directly to partner endpoints without the relay path" in c2.lower():
            return "yes"
        if "may not send telemetry directly to partner endpoints" in c2.lower():
            return "no"
        return "unknown"

    return "unknown"


def run_single(
    method: str,
    scenario: MinimalScenario,
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
        for field in SUMMARY_METRIC_FIELDS:
            summary[field] = _mean_std([row[field] for row in bucket])
        summary["runs"] = len(bucket)
        summary["full_chain_failure_count"] = sum(row["full_chain_failure"] for row in bucket)
        summary["answer_failure_count"] = sum(row["answer_failure"] for row in bucket)
        summary["answer_full_chain_disagreement_count"] = sum(
            row["answer_full_chain_disagreement"] for row in bucket
        )
        summary["full_chain_saturation_rate"] = round(
            sum(1 for row in bucket if row["full_chain_retention"] == 1.0) / len(bucket),
            4,
        )
        aggregated.append(summary)
    return aggregated


def _lookup_mean(rows: list[dict], **filters: str) -> float | None:
    for row in rows:
        if all(row[key] == value for key, value in filters.items()):
            return row["full_chain_retention"]["mean"]
    return None


def _pairwise_deltas(
    rows: list[dict],
    base_keys: tuple[str, ...],
    methods: tuple[str, ...],
) -> list[dict]:
    deltas: list[dict] = []
    seen: set[tuple] = set()
    for row in rows:
        key = tuple(row[field] for field in base_keys)
        if key in seen:
            continue
        seen.add(key)
        base = {field: value for field, value in zip(base_keys, key)}
        scores = {}
        for method in methods:
            mean = _lookup_mean(rows, **base, method=method)
            if mean is not None:
                scores[method] = mean
        if len(scores) != len(methods):
            continue
        deltas.append(
            {
                **base,
                **{f"{method}_full_chain_mean": score for method, score in scores.items()},
                "dsgc_minus_retrieval_only": round(scores["dsgc"] - scores["retrieval_only"], 4),
                "dsgc_minus_no_graph": round(scores["dsgc"] - scores["dsgc_no_graph"], 4),
                "dsgc_minus_sliding_window": round(scores["dsgc"] - scores["sliding_window"], 4)
                if "sliding_window" in scores
                else None,
            }
        )
    return deltas


def _answer_diagnostic(rows: list[dict]) -> dict:
    disagreements = sum(row["answer_full_chain_disagreement"] for row in rows)
    return {
        "runs": len(rows),
        "answer_full_chain_disagreement_count": disagreements,
        "answer_full_chain_equivalence": disagreements == 0,
    }


def run_grid(
    *,
    protocol_id: str,
    templates: list[str],
    methods: list[str],
    seeds: list[int],
    total_blocks_grid: list[int],
    budget_multipliers: list[float],
    encoder_type: str,
) -> list[dict]:
    results: list[dict] = []
    for method, template, total_blocks, budget_multiplier, seed in itertools.product(
        methods,
        templates,
        total_blocks_grid,
        budget_multipliers,
        seeds,
    ):
        scenario = generate_minimal_scenario(template=template, seed=seed, total_blocks=total_blocks)
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
                "query": scenario.query,
                "ground_truth_answer": scenario.answer,
                **metrics,
            }
        )
    return results


def build_template_stratified_summary(protocol: dict, rows: list[dict]) -> dict:
    per_template = _aggregate_rows(rows, ("method", "template", "regime"))
    by_regime = _aggregate_rows(rows, ("method", "regime"))
    pooled_overall = _aggregate_rows(rows, ("method",))
    return {
        "protocol_id": protocol["protocol_id"],
        "experiment": "template_stratified",
        "predictions": {
            "control": protocol["predictions"]["control"],
            "target": protocol["predictions"]["target"],
        },
        "per_template": per_template,
        "by_regime": by_regime,
        "pooled_overall": pooled_overall,
        "regime_pairwise_deltas": _pairwise_deltas(
            by_regime,
            ("regime",),
            ("sliding_window", "retrieval_only", "dsgc_no_graph", "dsgc"),
        ),
        "template_pairwise_deltas": _pairwise_deltas(
            per_template,
            ("template", "regime"),
            ("sliding_window", "retrieval_only", "dsgc_no_graph", "dsgc"),
        ),
        "answer_accuracy_diagnostic": _answer_diagnostic(rows),
    }


def build_graph_ablation_summary(protocol: dict, rows: list[dict]) -> dict:
    target_rows = [row for row in rows if row["regime"] == "target" and row["method"] != "sliding_window"]
    per_template = _aggregate_rows(target_rows, ("method", "template", "regime"))
    by_regime = _aggregate_rows(target_rows, ("method", "regime"))
    return {
        "protocol_id": protocol["protocol_id"],
        "experiment": "graph_ablation",
        "prediction": protocol["predictions"]["graph_ablation"],
        "target_per_template": per_template,
        "target_regime_summary": by_regime,
        "template_pairwise_deltas": _pairwise_deltas(
            per_template,
            ("template", "regime"),
            ("retrieval_only", "dsgc_no_graph", "dsgc"),
        ),
        "regime_pairwise_deltas": _pairwise_deltas(
            by_regime,
            ("regime",),
            ("retrieval_only", "dsgc_no_graph", "dsgc"),
        ),
    }


def build_encoder_sensitivity_summary(protocol: dict, rows: list[dict]) -> dict:
    per_template = _aggregate_rows(rows, ("encoder_type", "method", "template", "regime"))
    by_regime = _aggregate_rows(rows, ("encoder_type", "method", "regime"))

    template_method_shift: list[dict] = []
    for template in BUILDERS:
        regime = TEMPLATES[template]
        for method in protocol["encoder_sensitivity_methods"]:
            frozen = _lookup_mean(
                per_template,
                encoder_type="frozen",
                method=method,
                template=template,
                regime=regime,
            )
            sentence = _lookup_mean(
                per_template,
                encoder_type="sentence",
                method=method,
                template=template,
                regime=regime,
            )
            if frozen is None or sentence is None:
                continue
            template_method_shift.append(
                {
                    "template": template,
                    "regime": regime,
                    "method": method,
                    "frozen_full_chain_mean": frozen,
                    "sentence_full_chain_mean": sentence,
                    "sentence_minus_frozen": round(sentence - frozen, 4),
                }
            )

    template_encoder_deltas: list[dict] = []
    for template in BUILDERS:
        regime = TEMPLATES[template]
        for encoder_type in protocol["grid"]["encoders"]:
            retrieval_mean = _lookup_mean(
                per_template,
                encoder_type=encoder_type,
                method="retrieval_only",
                template=template,
                regime=regime,
            )
            no_graph_mean = _lookup_mean(
                per_template,
                encoder_type=encoder_type,
                method="dsgc_no_graph",
                template=template,
                regime=regime,
            )
            dsgc_mean = _lookup_mean(
                per_template,
                encoder_type=encoder_type,
                method="dsgc",
                template=template,
                regime=regime,
            )
            if retrieval_mean is None or no_graph_mean is None or dsgc_mean is None:
                continue
            template_encoder_deltas.append(
                {
                    "template": template,
                    "regime": regime,
                    "encoder_type": encoder_type,
                    "retrieval_only_full_chain_mean": retrieval_mean,
                    "dsgc_no_graph_full_chain_mean": no_graph_mean,
                    "dsgc_full_chain_mean": dsgc_mean,
                    "dsgc_minus_retrieval_only": round(dsgc_mean - retrieval_mean, 4),
                    "dsgc_minus_no_graph": round(dsgc_mean - no_graph_mean, 4),
                }
            )

    return {
        "protocol_id": protocol["protocol_id"],
        "experiment": "encoder_sensitivity",
        "prediction": protocol["predictions"]["encoder_sensitivity"],
        "per_template": per_template,
        "by_regime": by_regime,
        "template_method_shift": template_method_shift,
        "template_encoder_deltas": template_encoder_deltas,
        "answer_accuracy_diagnostic": _answer_diagnostic(rows),
    }


def _render_metric(value: dict[str, float]) -> str:
    return f"{value['mean']:.4f} +- {value['std']:.4f}"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def build_report(
    protocol: dict,
    template_summary: dict,
    graph_summary: dict,
    encoder_summary: dict,
) -> str:
    lines: list[str] = []
    lines.append(f"# {protocol['protocol_id']} Report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report covers the preregistered four-view suite:")
    lines.append("")
    lines.append("1. Template-stratified comparison")
    lines.append("2. Graph ablation")
    lines.append("3. Pooled comparison")
    lines.append("4. Encoder sensitivity")
    lines.append("")
    lines.append("## Experiment 1: Template-Stratified")
    lines.append("")
    lines.append(
        _table(
            ["template", "regime", "method", "prereq_retention", "full_chain_retention", "answer_acc", "failures"],
            [
                [
                    row["template"],
                    row["regime"],
                    row["method"],
                    _render_metric(row["prereq_retention"]),
                    _render_metric(row["full_chain_retention"]),
                    _render_metric(row["answer_acc"]),
                    str(row["full_chain_failure_count"]),
                ]
                for row in template_summary["per_template"]
            ],
        )
    )
    lines.append("")
    lines.append("## Experiment 2: Graph Ablation")
    lines.append("")
    lines.append(
        _table(
            ["template", "retrieval_only", "dsgc_no_graph", "dsgc", "dsgc-retrieval", "dsgc-no_graph"],
            [
                [
                    row["template"],
                    f"{row['retrieval_only_full_chain_mean']:.4f}",
                    f"{row['dsgc_no_graph_full_chain_mean']:.4f}",
                    f"{row['dsgc_full_chain_mean']:.4f}",
                    f"{row['dsgc_minus_retrieval_only']:.4f}",
                    f"{row['dsgc_minus_no_graph']:.4f}",
                ]
                for row in graph_summary["template_pairwise_deltas"]
            ],
        )
    )
    lines.append("")
    lines.append("## Experiment 3: Pooled Comparison")
    lines.append("")
    lines.append("### Overall")
    lines.append("")
    lines.append(
        _table(
            ["method", "prereq_retention", "full_chain_retention", "answer_acc"],
            [
                [
                    row["method"],
                    _render_metric(row["prereq_retention"]),
                    _render_metric(row["full_chain_retention"]),
                    _render_metric(row["answer_acc"]),
                ]
                for row in template_summary["pooled_overall"]
            ],
        )
    )
    lines.append("")
    lines.append("### By Regime")
    lines.append("")
    lines.append(
        _table(
            ["regime", "method", "prereq_retention", "full_chain_retention", "answer_acc"],
            [
                [
                    row["regime"],
                    row["method"],
                    _render_metric(row["prereq_retention"]),
                    _render_metric(row["full_chain_retention"]),
                    _render_metric(row["answer_acc"]),
                ]
                for row in template_summary["by_regime"]
            ],
        )
    )
    lines.append("")
    lines.append("## Experiment 4: Encoder Sensitivity")
    lines.append("")
    lines.append(
        _table(
            ["template", "regime", "encoder", "method", "full_chain_retention", "answer_acc"],
            [
                [
                    row["template"],
                    row["regime"],
                    row["encoder_type"],
                    row["method"],
                    _render_metric(row["full_chain_retention"]),
                    _render_metric(row["answer_acc"]),
                ]
                for row in encoder_summary["per_template"]
            ],
        )
    )
    lines.append("")
    lines.append("## Prediction vs Outcome")
    lines.append("")
    lines.append(f"- Control prediction: {template_summary['predictions']['control']}")
    for row in template_summary["regime_pairwise_deltas"]:
        if row["regime"] != "control":
            continue
        lines.append(
            f"  outcome: dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}, "
            f"dsgc-no_graph={row['dsgc_minus_no_graph']:.4f}, "
            f"dsgc-sliding_window={row['dsgc_minus_sliding_window']:.4f}"
        )
    lines.append(f"- Target prediction: {template_summary['predictions']['target']}")
    for row in template_summary["regime_pairwise_deltas"]:
        if row["regime"] != "target":
            continue
        lines.append(
            f"  outcome: dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}, "
            f"dsgc-no_graph={row['dsgc_minus_no_graph']:.4f}, "
            f"dsgc-sliding_window={row['dsgc_minus_sliding_window']:.4f}"
        )
    lines.append(f"- Graph ablation prediction: {graph_summary['prediction']}")
    for row in graph_summary["template_pairwise_deltas"]:
        lines.append(
            f"  {row['template']}: dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}, "
            f"dsgc-no_graph={row['dsgc_minus_no_graph']:.4f}"
        )
    lines.append(f"- Encoder sensitivity prediction: {encoder_summary['prediction']}")
    for row in encoder_summary["template_encoder_deltas"]:
        if row["regime"] != "target":
            continue
        lines.append(
            f"  {row['template']} ({row['encoder_type']}): "
            f"dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}, "
            f"dsgc-no_graph={row['dsgc_minus_no_graph']:.4f}"
        )
    lines.append("")
    lines.append("## Answer Accuracy Diagnostic")
    lines.append("")
    template_diag = template_summary["answer_accuracy_diagnostic"]
    encoder_diag = encoder_summary["answer_accuracy_diagnostic"]
    lines.append(
        f"- Frozen runs answer/full-chain disagreement count: {template_diag['answer_full_chain_disagreement_count']} "
        f"over {template_diag['runs']} runs."
    )
    lines.append(
        f"- Encoder-sensitivity runs answer/full-chain disagreement count: "
        f"{encoder_diag['answer_full_chain_disagreement_count']} over {encoder_diag['runs']} runs."
    )
    lines.append(
        f"- Frozen equivalence flag: {template_diag['answer_full_chain_equivalence']}"
    )
    lines.append(
        f"- Encoder-sensitivity equivalence flag: {encoder_diag['answer_full_chain_equivalence']}"
    )
    lines.append("")
    lines.append("## Failure Analysis")
    lines.append("")
    sentence_failures = [
        row
        for row in encoder_summary["template_encoder_deltas"]
        if row["regime"] == "target"
        and row["encoder_type"] == "sentence"
        and row["dsgc_minus_retrieval_only"] <= 0.0
    ]
    if sentence_failures:
        lines.append(
            "- The encoder-sensitivity prediction is only partially supported. "
            "The following target templates lose the DSGC advantage under the stronger encoder:"
        )
        for row in sentence_failures:
            lines.append(
                f"  - {row['template']}: retrieval_only={row['retrieval_only_full_chain_mean']:.4f}, "
                f"dsgc={row['dsgc_full_chain_mean']:.4f}, "
                f"dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}"
            )
        lines.append(
            "- This means the current target family is not uniformly structural under the "
            "stronger encoder and should be discussed template-by-template in the paper."
        )
    else:
        lines.append("- No explicit prediction violations were detected in the final_v1 summaries.")
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    for key, relative_path in protocol["outputs"].items():
        lines.append(f"- `{relative_path}`")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, payload: dict | list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", default=str(DEFAULT_PROTOCOL_PATH))
    args = parser.parse_args()

    protocol = load_protocol(Path(args.protocol))
    protocol_id = protocol["protocol_id"]
    templates = protocol["templates"]["control"] + protocol["templates"]["target"]
    frozen_rows = run_grid(
        protocol_id=protocol_id,
        templates=templates,
        methods=protocol["methods"],
        seeds=protocol["grid"]["seeds"],
        total_blocks_grid=protocol["grid"]["total_blocks"],
        budget_multipliers=protocol["grid"]["budget_multipliers"],
        encoder_type="frozen",
    )
    template_summary = build_template_stratified_summary(protocol, frozen_rows)
    graph_rows = [
        row
        for row in frozen_rows
        if row["regime"] == "target" and row["method"] in {"retrieval_only", "dsgc_no_graph", "dsgc"}
    ]
    graph_summary = build_graph_ablation_summary(protocol, frozen_rows)

    encoder_rows: list[dict] = []
    for encoder_type in protocol["grid"]["encoders"]:
        encoder_rows.extend(
            run_grid(
                protocol_id=protocol_id,
                templates=templates,
                methods=protocol["encoder_sensitivity_methods"],
                seeds=protocol["grid"]["seeds"],
                total_blocks_grid=protocol["grid"]["total_blocks"],
                budget_multipliers=protocol["grid"]["budget_multipliers"],
                encoder_type=encoder_type,
            )
        )
    encoder_summary = build_encoder_sensitivity_summary(protocol, encoder_rows)
    report = build_report(protocol, template_summary, graph_summary, encoder_summary)

    write_json(_protocol_output_path(protocol, "template_stratified_raw"), frozen_rows)
    write_json(_protocol_output_path(protocol, "template_stratified_summary"), template_summary)
    write_json(_protocol_output_path(protocol, "graph_ablation_raw"), graph_rows)
    write_json(_protocol_output_path(protocol, "graph_ablation_summary"), graph_summary)
    write_json(_protocol_output_path(protocol, "encoder_sensitivity_raw"), encoder_rows)
    write_json(_protocol_output_path(protocol, "encoder_sensitivity_summary"), encoder_summary)
    report_path = _protocol_output_path(protocol, "suite_report")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
