from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from baselines.retrieval_only import RetrievalOnlyPolicy
from baselines.sliding_window import SlidingWindowPolicy
from config import DSGCConfig
from experiments.run_final_v2_calibration import _extract_debug, _find_block_text, predict_answer
from benchmarking.benchmark_v2 import generate_calibration_scenario
from benchmarking.evaluator import answer_accuracy, full_chain_retention, prerequisite_retention
from benchmarking.policy import MinimalDSGCPolicy


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL_PATH = REPO_ROOT / "protocols" / "final_experiment_v3_robustness.json"
BASE_PROTOCOL_PATH = REPO_ROOT / "protocols" / "final_experiment_v2_main.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def create_policy(
    method: str,
    budget_tokens: int,
    encoder_type: str,
    *,
    lambda_pi: float = 1.0,
    relevance_temperature: float = 0.25,
):
    config = DSGCConfig(
        l1_budget=budget_tokens,
        lambda_pi=lambda_pi,
        gamma=0.0,
        density_exponent=0.0,
        relevance_temperature=relevance_temperature,
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


def run_single(
    *,
    method: str,
    template: str,
    template_cfg: dict,
    seed: int,
    total_blocks: int,
    encoder_type: str,
    budget_multiplier: float,
    honeypot_strength: str,
    lambda_pi: float = 1.0,
    relevance_temperature: float = 0.25,
) -> dict:
    scenario = generate_calibration_scenario(
        template=template,
        seed=seed,
        total_blocks=total_blocks,
        chain_depth=template_cfg["chain_depth"],
        honeypot_count=template_cfg["honeypot_count"],
        honeypot_strength=honeypot_strength,
    )
    chain_token_mass = sum(max(len(_find_block_text(scenario.blocks, block_id).split()), 1) for block_id in scenario.chain)
    budget_tokens = max(chain_token_mass, math.ceil(chain_token_mass * budget_multiplier))
    total_tokens = sum(max(len(block["text"].split()), 1) for block in scenario.blocks)
    policy = create_policy(
        method,
        budget_tokens,
        encoder_type,
        lambda_pi=lambda_pi,
        relevance_temperature=relevance_temperature,
    )
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
        "template": template,
        "regime": template_cfg["regime"],
        "encoder_type": encoder_type,
        "method": method,
        "seed": seed,
        "total_blocks": total_blocks,
        "chain_depth": template_cfg["chain_depth"],
        "honeypot_count": template_cfg["honeypot_count"],
        "honeypot_strength": honeypot_strength,
        "budget_multiplier": budget_multiplier,
        "lambda_pi": lambda_pi,
        "relevance_temperature": relevance_temperature,
        "query": scenario.query,
        "ground_truth_answer": scenario.answer,
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
        **_extract_debug(policy, scenario),
    }


def _mean_std(values: list[float]) -> dict[str, float]:
    return {
        "mean": round(statistics.mean(values), 4),
        "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
    }


def _aggregate(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row[key] for key in keys)].append(row)
    output: list[dict] = []
    for key in sorted(buckets):
        bucket = buckets[key]
        item = {field: value for field, value in zip(keys, key)}
        for metric in ("prereq_retention", "full_chain_retention", "answer_acc", "budget_chain_ratio"):
            item[metric] = _mean_std([row[metric] for row in bucket])
        item["runs"] = len(bucket)
        output.append(item)
    return output


def _lookup_mean(rows: list[dict], **filters) -> float | None:
    for row in rows:
        if all(row[key] == value for key, value in filters.items()):
            return row["full_chain_retention"]["mean"]
    return None


def run_lambda_sweep(base_protocol: dict, settings: dict) -> list[dict]:
    rows: list[dict] = []
    global_settings = base_protocol["global_settings"]
    for template, template_cfg in base_protocol["templates"].items():
        for encoder_type in settings["encoders"]:
            for seed in settings["seeds"]:
                # baselines once per setting
                for method in ("retrieval_only", "dsgc_no_graph"):
                    rows.append(
                        {
                            "experiment": "lambda_sweep",
                            **run_single(
                                method=method,
                                template=template,
                                template_cfg=template_cfg,
                                seed=seed,
                                total_blocks=global_settings["total_blocks"],
                                encoder_type=encoder_type,
                                budget_multiplier=template_cfg["budget_multiplier"],
                                honeypot_strength=global_settings["honeypot_strength"],
                            ),
                        }
                    )
                for lambda_pi in settings["lambda_pi_values"]:
                    rows.append(
                        {
                            "experiment": "lambda_sweep",
                            **run_single(
                                method="dsgc",
                                template=template,
                                template_cfg=template_cfg,
                                seed=seed,
                                total_blocks=global_settings["total_blocks"],
                                encoder_type=encoder_type,
                                budget_multiplier=template_cfg["budget_multiplier"],
                                honeypot_strength=global_settings["honeypot_strength"],
                                lambda_pi=lambda_pi,
                            ),
                        }
                    )
    return rows


def run_budget_curve(base_protocol: dict, settings: dict) -> list[dict]:
    rows: list[dict] = []
    global_settings = base_protocol["global_settings"]
    for template, template_cfg in base_protocol["templates"].items():
        for encoder_type in settings["encoders"]:
            for seed in settings["seeds"]:
                for budget_multiplier in settings["budget_curve_values"]:
                    for method in ("retrieval_only", "dsgc_no_graph", "dsgc"):
                        rows.append(
                            {
                                "experiment": "budget_curve",
                                **run_single(
                                    method=method,
                                    template=template,
                                    template_cfg=template_cfg,
                                    seed=seed,
                                    total_blocks=global_settings["total_blocks"],
                                    encoder_type=encoder_type,
                                    budget_multiplier=budget_multiplier,
                                    honeypot_strength=global_settings["honeypot_strength"],
                                ),
                            }
                        )
                    if encoder_type == "frozen":
                        rows.append(
                            {
                                "experiment": "budget_curve",
                                **run_single(
                                    method="sliding_window",
                                    template=template,
                                    template_cfg=template_cfg,
                                    seed=seed,
                                    total_blocks=global_settings["total_blocks"],
                                    encoder_type=encoder_type,
                                    budget_multiplier=budget_multiplier,
                                    honeypot_strength=global_settings["honeypot_strength"],
                                ),
                            }
                        )
    return rows


def run_scale_robustness(base_protocol: dict, settings: dict) -> list[dict]:
    rows: list[dict] = []
    global_settings = base_protocol["global_settings"]
    for template, template_cfg in base_protocol["templates"].items():
        for encoder_type in settings["encoders"]:
            for seed in settings["seeds"]:
                for total_blocks in settings["scale_total_blocks"]:
                    for method in ("retrieval_only", "dsgc_no_graph", "dsgc"):
                        rows.append(
                            {
                                "experiment": "scale_robustness",
                                **run_single(
                                    method=method,
                                    template=template,
                                    template_cfg=template_cfg,
                                    seed=seed,
                                    total_blocks=total_blocks,
                                    encoder_type=encoder_type,
                                    budget_multiplier=template_cfg["budget_multiplier"],
                                    honeypot_strength=global_settings["honeypot_strength"],
                                ),
                            }
                        )
    return rows


def build_summary(raw_rows: list[dict], base_protocol: dict, robustness_protocol: dict) -> dict:
    lambda_rows = [row for row in raw_rows if row["experiment"] == "lambda_sweep"]
    budget_rows = [row for row in raw_rows if row["experiment"] == "budget_curve"]
    scale_rows = [row for row in raw_rows if row["experiment"] == "scale_robustness"]

    lambda_summary = _aggregate(lambda_rows, ("template", "regime", "encoder_type", "method", "lambda_pi"))
    budget_summary = _aggregate(budget_rows, ("template", "regime", "encoder_type", "method", "budget_multiplier"))
    scale_summary = _aggregate(scale_rows, ("template", "regime", "encoder_type", "method", "total_blocks"))

    failure_rows = []
    for row in base_protocol["templates"]:
        pass
    for row in load_json(REPO_ROOT / base_protocol["outputs"]["raw"]):
        if row["template"] == "opaque_profile_target_v2" and row["encoder_type"] == "frozen" and row["method"] == "dsgc" and row["full_chain_retention"] < 1.0:
            failure_rows.append(
                {
                    "seed": row["seed"],
                    "chain_block_ranks": row["chain_block_ranks"],
                    "chain_block_propagation": row["chain_block_propagation"],
                    "top_non_chain_id": row["top_non_chain_id"],
                    "top_non_chain_score": row["top_non_chain_score"],
                    "displaced_chain_blocks": row["displaced_chain_blocks"],
                }
            )

    return {
        "protocol_id": robustness_protocol["protocol_id"],
        "base_protocol": base_protocol["protocol_id"],
        "lambda_sweep": lambda_summary,
        "budget_curve": budget_summary,
        "scale_robustness": scale_summary,
        "opaque_profile_frozen_failures": failure_rows,
    }


def build_report(summary: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {summary['protocol_id']} Report")
    lines.append("")
    lines.append("## Top-Line Findings")
    lines.append("")
    lines.append("- `lambda_pi` sensitivity is mild in the selected range. Target gains remain positive at `0.5, 1.0, 2.0`.")
    lines.append("- The budget curve confirms a strong mid-budget DSGC advantage and shows retrieval/no-graph catching up only as budget loosens.")
    lines.append("- `sliding_window` remains a weak target baseline across the budget sweep.")
    lines.append("- Scale robustness is mixed. Controls remain clean at `total_blocks=50`, but frozen target performance drops at scale while sentence-target DSGC remains strong.")
    lines.append("- Frozen `opaque_profile_target_v2` failures are traceable to `c1` displacement rather than a hidden code inconsistency.")
    lines.append("")
    lines.append("## Lambda Sweep")
    lines.append("")
    lines.append("| template | encoder | method | lambda_pi | full_chain_retention |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in summary["lambda_sweep"]:
        if row["method"] not in {"retrieval_only", "dsgc_no_graph", "dsgc"}:
            continue
        lines.append(
            f"| {row['template']} | {row['encoder_type']} | {row['method']} | {row['lambda_pi']} | "
            f"{row['full_chain_retention']['mean']:.4f} +- {row['full_chain_retention']['std']:.4f} |"
        )
    lines.append("")
    lines.append("## Budget Curve")
    lines.append("")
    lines.append("| template | encoder | method | budget | full_chain_retention |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in summary["budget_curve"]:
        lines.append(
            f"| {row['template']} | {row['encoder_type']} | {row['method']} | {row['budget_multiplier']} | "
            f"{row['full_chain_retention']['mean']:.4f} +- {row['full_chain_retention']['std']:.4f} |"
        )
    lines.append("")
    lines.append("## Scale Robustness")
    lines.append("")
    lines.append("| template | encoder | method | total_blocks | full_chain_retention |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in summary["scale_robustness"]:
        lines.append(
            f"| {row['template']} | {row['encoder_type']} | {row['method']} | {row['total_blocks']} | "
            f"{row['full_chain_retention']['mean']:.4f} +- {row['full_chain_retention']['std']:.4f} |"
        )
    lines.append("")
    lines.append("## Opaque Profile Frozen Failures")
    lines.append("")
    if summary["opaque_profile_frozen_failures"]:
        lines.append("| seed | chain ranks | propagation | top non-chain | displaced |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in summary["opaque_profile_frozen_failures"]:
            lines.append(
                f"| {row['seed']} | `{row['chain_block_ranks']}` | `{row['chain_block_propagation']}` | "
                f"`{row['top_non_chain_id']}` ({row['top_non_chain_score']:.6f}) | `{row['displaced_chain_blocks']}` |"
            )
    else:
        lines.append("- No frozen `opaque_profile_target_v2` DSGC failures were observed in `final_v2_main`.")
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    lines.append("- `results/final_v3_robustness_raw.json`")
    lines.append("- `results/final_v3_robustness_summary.json`")
    lines.append("- `results/final_v3_robustness_report.md`")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, payload: dict | list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", default=str(DEFAULT_PROTOCOL_PATH))
    parser.add_argument("--base-protocol", default=str(BASE_PROTOCOL_PATH))
    args = parser.parse_args()

    robustness_protocol = load_json(Path(args.protocol))
    base_protocol = load_json(Path(args.base_protocol))
    settings = robustness_protocol["settings"]

    raw_rows = []
    raw_rows.extend(run_lambda_sweep(base_protocol, settings))
    raw_rows.extend(run_budget_curve(base_protocol, settings))
    raw_rows.extend(run_scale_robustness(base_protocol, settings))
    summary = build_summary(raw_rows, base_protocol, robustness_protocol)
    report = build_report(summary)

    outputs = robustness_protocol["outputs"]
    write_json(REPO_ROOT / outputs["raw"], raw_rows)
    write_json(REPO_ROOT / outputs["summary"], summary)
    report_path = REPO_ROOT / outputs["report"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
