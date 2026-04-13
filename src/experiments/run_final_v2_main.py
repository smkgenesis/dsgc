from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

from experiments.run_final_v2_calibration import run_single
from benchmarking.benchmark_v2 import generate_calibration_scenario


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL_PATH = REPO_ROOT / "protocols" / "final_experiment_v2_main.json"


def load_protocol(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _output_path(protocol: dict, key: str) -> Path:
    return REPO_ROOT / protocol["outputs"][key]


def _mean_std(values: list[float]) -> dict[str, float]:
    return {
        "mean": round(statistics.mean(values), 4),
        "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
    }


def run_suite(protocol: dict) -> list[dict]:
    rows: list[dict] = []
    global_settings = protocol["global_settings"]
    for template, template_cfg in protocol["templates"].items():
        for encoder_type in global_settings["encoders"]:
            for method in global_settings["methods"]:
                for seed in global_settings["seeds"]:
                    scenario = generate_calibration_scenario(
                        template=template,
                        seed=seed,
                        total_blocks=global_settings["total_blocks"],
                        chain_depth=template_cfg["chain_depth"],
                        honeypot_count=template_cfg["honeypot_count"],
                        honeypot_strength=global_settings["honeypot_strength"],
                    )
                    metrics = run_single(
                        method=method,
                        scenario=scenario,
                        budget_multiplier=template_cfg["budget_multiplier"],
                        encoder_type=encoder_type,
                    )
                    rows.append(
                        {
                            "protocol_id": protocol["protocol_id"],
                            "template": template,
                            "regime": template_cfg["regime"],
                            "encoder_type": encoder_type,
                            "method": method,
                            "seed": seed,
                            "total_blocks": global_settings["total_blocks"],
                            "chain_depth": template_cfg["chain_depth"],
                            "honeypot_count": template_cfg["honeypot_count"],
                            "honeypot_strength": global_settings["honeypot_strength"],
                            "budget_multiplier": template_cfg["budget_multiplier"],
                            "query": scenario.query,
                            "ground_truth_answer": scenario.answer,
                            **metrics,
                        }
                    )
    return rows


def _aggregate(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row[key] for key in keys)].append(row)

    aggregated: list[dict] = []
    for key in sorted(buckets):
        bucket = buckets[key]
        summary = {field: value for field, value in zip(keys, key)}
        for metric in (
            "prereq_retention",
            "full_chain_retention",
            "answer_acc",
            "selected_block_count",
            "budget_chain_ratio",
            "selected_honeypot_count",
        ):
            summary[metric] = _mean_std([row[metric] for row in bucket])
        summary["runs"] = len(bucket)
        summary["full_chain_failure_count"] = sum(row["full_chain_failure"] for row in bucket)
        aggregated.append(summary)
    return aggregated


def _lookup_mean(rows: list[dict], **filters) -> float | None:
    for row in rows:
        if all(row[key] == value for key, value in filters.items()):
            return row["full_chain_retention"]["mean"]
    return None


def _pairwise_deltas(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    seen: set[tuple] = set()
    deltas: list[dict] = []
    for row in rows:
        key = tuple(row[field] for field in keys)
        if key in seen:
            continue
        seen.add(key)
        base = {field: value for field, value in zip(keys, key)}
        retrieval = _lookup_mean(rows, **base, method="retrieval_only")
        no_graph = _lookup_mean(rows, **base, method="dsgc_no_graph")
        dsgc = _lookup_mean(rows, **base, method="dsgc")
        if retrieval is None or no_graph is None or dsgc is None:
            continue
        deltas.append(
            {
                **base,
                "retrieval_only_full_chain_mean": retrieval,
                "dsgc_no_graph_full_chain_mean": no_graph,
                "dsgc_full_chain_mean": dsgc,
                "dsgc_minus_retrieval_only": round(dsgc - retrieval, 4),
                "dsgc_minus_no_graph": round(dsgc - no_graph, 4),
            }
        )
    return deltas


def build_summary(protocol: dict, rows: list[dict]) -> dict:
    per_template = _aggregate(rows, ("encoder_type", "method", "template", "regime"))
    by_regime = _aggregate(rows, ("encoder_type", "method", "regime"))
    template_pairwise = _pairwise_deltas(per_template, ("encoder_type", "template", "regime"))
    regime_pairwise = _pairwise_deltas(by_regime, ("encoder_type", "regime"))
    return {
        "protocol_id": protocol["protocol_id"],
        "predictions": protocol["predictions"],
        "per_template": per_template,
        "by_regime": by_regime,
        "template_pairwise_deltas": template_pairwise,
        "regime_pairwise_deltas": regime_pairwise,
    }


def build_report(protocol: dict, summary: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {protocol['protocol_id']} Report")
    lines.append("")
    lines.append("## Fixed Suite")
    lines.append("")
    lines.append(f"- Controls: {', '.join([name for name, cfg in protocol['templates'].items() if cfg['regime']=='control'])}")
    lines.append(f"- Targets: {', '.join([name for name, cfg in protocol['templates'].items() if cfg['regime']=='target'])}")
    lines.append("- Methods: retrieval_only, dsgc_no_graph, dsgc")
    lines.append("- Encoders: frozen, sentence")
    lines.append(f"- Seeds: {len(protocol['global_settings']['seeds'])}")
    lines.append("")
    lines.append("## Per Template")
    lines.append("")
    lines.append("| encoder | template | regime | method | prereq_retention | full_chain_retention | answer_acc |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for row in summary["per_template"]:
        lines.append(
            f"| {row['encoder_type']} | {row['template']} | {row['regime']} | {row['method']} | "
            f"{row['prereq_retention']['mean']:.4f} +- {row['prereq_retention']['std']:.4f} | "
            f"{row['full_chain_retention']['mean']:.4f} +- {row['full_chain_retention']['std']:.4f} | "
            f"{row['answer_acc']['mean']:.4f} +- {row['answer_acc']['std']:.4f} |"
        )
    lines.append("")
    lines.append("## By Regime")
    lines.append("")
    lines.append("| encoder | regime | method | full_chain_retention |")
    lines.append("| --- | --- | --- | --- |")
    for row in summary["by_regime"]:
        lines.append(
            f"| {row['encoder_type']} | {row['regime']} | {row['method']} | "
            f"{row['full_chain_retention']['mean']:.4f} +- {row['full_chain_retention']['std']:.4f} |"
        )
    lines.append("")
    lines.append("## Prediction vs Outcome")
    lines.append("")
    lines.append(f"- Controls prediction: {protocol['predictions']['controls']}")
    for row in summary["template_pairwise_deltas"]:
        if row["regime"] != "control":
            continue
        lines.append(
            f"  {row['encoder_type']} / {row['template']}: "
            f"dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}, "
            f"dsgc-no_graph={row['dsgc_minus_no_graph']:.4f}"
        )
    lines.append(f"- Targets prediction: {protocol['predictions']['targets']}")
    for row in summary["template_pairwise_deltas"]:
        if row["regime"] != "target":
            continue
        lines.append(
            f"  {row['encoder_type']} / {row['template']}: "
            f"dsgc-retrieval_only={row['dsgc_minus_retrieval_only']:.4f}, "
            f"dsgc-no_graph={row['dsgc_minus_no_graph']:.4f}"
        )
    lines.append(f"- Strongest target prediction: {protocol['predictions']['strongest_target']}")
    lines.append(f"- Encoder robustness prediction: {protocol['predictions']['encoder_robustness']}")
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    lines.append(f"- `{protocol['outputs']['raw']}`")
    lines.append(f"- `{protocol['outputs']['summary']}`")
    lines.append(f"- `{protocol['outputs']['report']}`")
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
    rows = run_suite(protocol)
    summary = build_summary(protocol, rows)
    report = build_report(protocol, summary)
    write_json(_output_path(protocol, "raw"), rows)
    write_json(_output_path(protocol, "summary"), summary)
    report_path = _output_path(protocol, "report")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
