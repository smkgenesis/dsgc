from __future__ import annotations

from dataclasses import dataclass, field
import random


GENERIC_FILLERS = [
    "Weekly sync: the analytics export job was delayed until Thursday morning.",
    "Ops note: the staging cluster moved to a new maintenance window.",
    "Product memo: the dashboard navigation will be simplified next sprint.",
    "Support update: two customers reported a slow settings page this week.",
    "Design review: spacing tokens were adjusted for the mobile form layout.",
    "Engineering note: the CI pipeline now caches wheels between runs.",
    "Meeting notes: the vendor renewal discussion moved to next Tuesday.",
    "Research summary: the team compared two caching approaches for API reads.",
    "Planning note: the release checklist now includes a rollback dry run.",
    "Standup: the billing service refactor is waiting on one migration script.",
    "Incident summary: a brief packet loss event affected one internal queue.",
    "Sprint recap: three low-priority bugs were moved back to the backlog.",
    "Operations memo: the log retention period was extended to thirty days.",
    "Team update: the onboarding handbook was revised for new engineers.",
    "Customer note: the reports page will add CSV filters in the next release.",
    "Architecture review: the image pipeline will stay on the current codec.",
]


TEMPLATES_V2 = {
    "budget_control": "control",
    "numeric_threshold_control_v2": "control",
    "permission_control_v2": "control",
    "opaque_role_target_v2": "target",
    "opaque_profile_target_v2": "target",
}


@dataclass(slots=True)
class CalibrationScenario:
    blocks: list[dict[str, str]]
    chain: list[str]
    prerequisite_ids: list[str]
    dependencies: list[tuple[str, str]]
    query: str
    answer: str
    template: str
    regime: str
    metadata: dict[str, str | int | bool] = field(default_factory=dict)


def _make_chain(texts: list[str]) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
    chain = [{"id": f"c{idx + 1}", "text": text} for idx, text in enumerate(texts)]
    dependencies = [(f"c{idx + 2}", f"c{idx + 1}") for idx in range(len(texts) - 1)]
    return chain, dependencies


def _sample_honeypots(rng: random.Random, candidates: list[str], count: int) -> list[dict[str, str]]:
    if count > len(candidates):
        raise ValueError(f"Requested {count} honeypots but only {len(candidates)} candidates are available")
    chosen = rng.sample(candidates, count)
    return [{"id": f"h{idx + 1}", "text": text} for idx, text in enumerate(chosen)]


def _budget_control(
    rng: random.Random,
    *,
    chain_depth: int,
    honeypot_count: int,
    honeypot_strength: str,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    project = rng.choice(["Atlas", "Helios", "Juniper", "Cinder"])
    budget = rng.choice([480, 600, 720, 840])
    percent = rng.choice([25, 30, 40])
    threshold = int(budget * percent / 100)
    cost = rng.choice([threshold - 40, threshold - 10, threshold + 10, threshold + 40])
    answer = "yes" if cost <= threshold else "no"
    policy_tag = rng.choice(["approval_window_17", "threshold_window_24", "review_window_31"])
    other_project = rng.choice([name for name in ["Atlas", "Helios", "Juniper", "Cinder"] if name != project])

    if chain_depth == 2:
        chain_texts = [
            f"Project {project} has a backup budget of {budget} credits this quarter.",
            f"Project {project} backup approvals allow costs within {percent} percent of the backup budget.",
        ]
    elif chain_depth == 3:
        chain_texts = [
            f"Project {project} has a backup budget of {budget} credits this quarter.",
            f"Project {project} backup approvals use policy tag {policy_tag}.",
            f"Policy tag {policy_tag} allows costs within {percent} percent of the backup budget.",
        ]
    else:
        raise ValueError("budget_control supports chain_depth 2 or 3")

    query = (
        f"A backup job for Project {project} costs {cost} credits. "
        "Is it allowed under the backup approval rule? Answer yes or no."
    )

    if honeypot_strength == "easy":
        candidates = [
            f"Project {project} scheduled a vendor workshop with a budget of {budget} credits.",
            f"Project {other_project} backup drills consumed {cost} credits during a staging test.",
            f"Project {project} expanded its travel reserve by {percent} credits for conferences.",
            f"Project {project} keeps an infrastructure reserve of {budget + 80} credits for migrations.",
            f"Project {other_project} tracks incident cleanup costs in a separate ledger.",
            f"Project {project} renamed the backup dashboard during the quarterly review.",
            f"Project {project} plans a report export refresh in the next sprint.",
            f"Project {other_project} adjusted mobile layout spacing for the billing page.",
        ]
    elif honeypot_strength == "hard":
        candidates = [
            f"Project {project} backup cleanup costs stayed within {percent} percent of the infrastructure reserve.",
            f"Project {project} backup vendors quoted {cost} credits for a disaster drill package.",
            f"Project {other_project} backup approvals use policy tag {policy_tag} for archive rehearsals.",
            f"Project {project} tracks database migration costs against a backup-style operating reserve.",
            f"Project {project} backup restorations require review when vendor costs exceed {threshold} credits.",
            f"Project {other_project} has a backup budget of {budget} credits for archive rehearsals.",
            f"Project {project} audit notes mention backup approvals for staging exports.",
            f"Project {project} backup staffing plans remain within {percent} percent of the operations budget.",
        ]
    else:
        candidates = [
            f"Project {project} has a travel allowance of {budget} credits for vendor visits.",
            f"{project} database migrations may spend at most {percent} percent of the infrastructure budget.",
            f"An archive rehearsal for Project {other_project} cost {cost} credits during cleanup.",
            f"Project {project} has an infrastructure reserve of {budget + 120} credits for disaster drills.",
            f"Project {project} backup review meetings moved to next Tuesday.",
            f"Project {other_project} tracks infrastructure reserve changes for export jobs.",
            f"The {project} vendor worksheet records cleanup costs from last quarter.",
            f"Project {project} will revise the backup dashboard navigation next sprint.",
        ]

    chain, deps = _make_chain(chain_texts)
    return chain, deps, query, answer, _sample_honeypots(rng, candidates, honeypot_count), {
        "task_type": "numeric_allow",
        "project": project,
        "budget": budget,
        "percent": percent,
        "cost": cost,
        "honeypot_strength": honeypot_strength,
    }


def _numeric_threshold_control_v2(
    rng: random.Random,
    *,
    chain_depth: int,
    honeypot_count: int,
    honeypot_strength: str,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    service = rng.choice(["Nova", "Atlas", "Juniper", "Cinder"])
    burst_limit = rng.choice([8, 10, 12, 14])
    observed_burst = rng.choice([burst_limit - 3, burst_limit - 1, burst_limit + 1, burst_limit + 3])
    answer = "yes" if observed_burst <= burst_limit else "no"
    rule_tag = rng.choice(["permit_window_19", "latency_window_23", "burst_window_41"])
    other_service = rng.choice([name for name in ["Nova", "Atlas", "Juniper", "Cinder"] if name != service])

    if chain_depth == 2:
        chain_texts = [
            f"Service {service} has a burst limit of {burst_limit} requests per second.",
            f"Service {service} accepts traffic only when requests stay at or below the burst limit.",
        ]
    elif chain_depth == 3:
        chain_texts = [
            f"Service {service} has a burst limit of {burst_limit} requests per second.",
            f"Service {service} traffic checks use threshold rule {rule_tag}.",
            f"Threshold rule {rule_tag} accepts traffic at or below the burst limit.",
        ]
    else:
        raise ValueError("numeric_threshold_control_v2 supports chain_depth 2 or 3")

    query = (
        f"Service {service} received {observed_burst} requests per second. "
        "Is that traffic allowed? Answer yes or no."
    )

    if honeypot_strength == "easy":
        candidates = [
            f"Service {service} reviewed a burst dashboard during the weekly sync.",
            f"Service {other_service} has a deployment limit for canary rollouts.",
            f"Service {service} changed its report export cadence yesterday.",
            f"Service {service} caches analytics queries between API reads.",
            f"Service {other_service} renamed the mobile settings page.",
            f"Service {service} now keeps logs for thirty days.",
            f"Service {other_service} had a slow settings page last week.",
            f"Service {service} updated its release checklist for rollback drills.",
        ]
    elif honeypot_strength == "hard":
        candidates = [
            f"Service {service} burst diagnostics mention {observed_burst} requests during a staging replay.",
            f"Service {other_service} traffic checks use threshold rule {rule_tag} for canary rollouts.",
            f"Service {service} latency alerts trigger when requests exceed a burst-style staging limit.",
            f"Service {service} traffic policy review discussed burst handling for metrics exports.",
            f"Service {other_service} accepted {burst_limit} requests per second during a load test.",
            f"Service {service} stores burst logs for the partner metrics pipeline.",
            f"Service {service} reports traffic windows for staging relays every fifteen minutes.",
            f"Service {other_service} renamed a burst-monitoring dashboard in production.",
        ]
    else:
        candidates = [
            f"Service {service} traffic dashboards show burst metrics every fifteen minutes.",
            f"Service {other_service} has a rollout limit for canary releases.",
            f"Service {service} reviewed a traffic report during the weekly sync.",
            f"Service {service} caches request summaries between API reads.",
            f"Service {other_service} adjusted mobile form spacing in the new dashboard.",
            f"Service {service} expanded log retention for incident review.",
            f"Service {service} tracks release checklist items for rollback drills.",
            f"Service {other_service} uses a deployment window for report exports.",
        ]

    chain, deps = _make_chain(chain_texts)
    return chain, deps, query, answer, _sample_honeypots(rng, candidates, honeypot_count), {
        "task_type": "numeric_allow",
        "service": service,
        "burst_limit": burst_limit,
        "observed_burst": observed_burst,
        "honeypot_strength": honeypot_strength,
    }


def _permission_control_v2(
    rng: random.Random,
    *,
    chain_depth: int,
    honeypot_count: int,
    honeypot_strength: str,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    user = rng.choice(["Alice", "Bob", "Casey", "Dana"])
    title = rng.choice(["backup admin", "backup auditor"])
    answer = "yes" if title == "backup admin" else "no"
    title_tag = rng.choice(["archive_authority_18", "retention_authority_26", "review_authority_44"])
    other_user = rng.choice([name for name in ["Alice", "Bob", "Casey", "Dana"] if name != user])

    if chain_depth == 2:
        chain_texts = [
            f"{user} holds the operational title {title} for production backup approvals.",
            (
                "Backup admins may delete production backups."
                if title == "backup admin"
                else "Backup auditors may review production backups but may not delete them."
            ),
        ]
    elif chain_depth == 3:
        chain_texts = [
            f"{user} holds operational title tag {title_tag}.",
            f"Operational title tag {title_tag} corresponds to the {title} role for production backup approvals.",
            (
                "The backup admin role may delete production backups."
                if title == "backup admin"
                else "The backup auditor role may review production backups but may not delete them."
            ),
        ]
    else:
        raise ValueError("permission_control_v2 supports chain_depth 2 or 3")

    query = f"Can {user} delete the production backup? Answer yes or no."

    if honeypot_strength == "easy":
        candidates = [
            f"{user} reviewed the backup dashboard during the weekly audit.",
            f"{other_user} led a release planning session for reporting exports.",
            "Backup auditors prepare weekly review notes for incident drills.",
            f"{user} updated the archive handbook for new engineers.",
            "Production backup reports now include CSV filters.",
            f"{other_user} approved a rollback dry run for a staging service.",
            f"{user} attended a vendor renewal discussion next Tuesday.",
            "Archive staff revised the onboarding checklist this quarter.",
        ]
    elif honeypot_strength == "hard":
        candidates = [
            f"{other_user} is the backup admin for staging archive cleanup.",
            f"{user} reviewed production backup deletion notes during the weekly audit.",
            "Backup admins may delete staging backups after incident approval.",
            f"{user} handled archive approval reviews for the reporting database.",
            f"{other_user} holds operational title tag {title_tag} for staging approvals.",
            "Production backup drills require approval from incident staff.",
            f"{user} joined a backup authority review for archive rehearsals.",
            "Backup auditors may inspect production restore logs after incidents.",
        ]
    else:
        candidates = [
            f"{user} reviewed the backup dashboard during the weekly audit.",
            f"{other_user} is the release planner for the reporting database.",
            "Backup auditors prepare weekly review notes for incident drills.",
            f"{user} updated the archive handbook for new engineers.",
            "Production backup reports now include CSV filters.",
            f"{other_user} approved a rollback dry run for a staging service.",
            f"{user} attended a vendor renewal discussion next Tuesday.",
            "Archive staff revised the onboarding checklist this quarter.",
        ]

    chain, deps = _make_chain(chain_texts)
    return chain, deps, query, answer, _sample_honeypots(rng, candidates, honeypot_count), {
        "task_type": "permission",
        "user": user,
        "title": title,
        "honeypot_strength": honeypot_strength,
    }


def _opaque_role_target_v2(
    rng: random.Random,
    *,
    chain_depth: int,
    honeypot_count: int,
    honeypot_strength: str,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    user = rng.choice(["Alice", "Bob", "Casey", "Dana"])
    other_user = rng.choice([name for name in ["Alice", "Bob", "Casey", "Dana"] if name != user])
    bundle = rng.choice(["bundle_north_17", "bundle_cedar_24", "bundle_orbit_31", "bundle_quartz_42"])
    other_bundle = rng.choice([name for name in ["bundle_north_17", "bundle_cedar_24", "bundle_orbit_31", "bundle_quartz_42"] if name != bundle])
    clearance = rng.choice(["clearance_alpha_29", "clearance_delta_14", "clearance_orbit_33", "clearance_river_52"])
    other_clearance = rng.choice([name for name in ["clearance_alpha_29", "clearance_delta_14", "clearance_orbit_33", "clearance_river_52"] if name != clearance])
    can_delete = rng.choice([True, False])
    answer = "yes" if can_delete else "no"

    if chain_depth == 2:
        chain_texts = [
            f"{user} is assigned access bundle {bundle} for the production backup system.",
            (
                f"Access bundle {bundle} may delete production backups."
                if can_delete
                else f"Access bundle {bundle} may review production backups but may not delete them."
            ),
        ]
    elif chain_depth == 3:
        chain_texts = [
            f"{user} is assigned access bundle {bundle} for the production backup system.",
            f"Access bundle {bundle} maps to clearance code {clearance}.",
            (
                f"Clearance code {clearance} may delete production backups."
                if can_delete
                else f"Clearance code {clearance} may review production backups but may not delete them."
            ),
        ]
    else:
        raise ValueError("opaque_role_target_v2 supports chain_depth 2 or 3")

    query = f"Can {user} delete the production backup? Answer yes or no."

    if honeypot_strength == "easy":
        candidates = [
            f"{user} reviewed the production backup dashboard during the weekly audit.",
            f"{other_user} is assigned access bundle {other_bundle} for the production backup system.",
            f"Clearance code {other_clearance} controls archive export reviews.",
            "Operations staff updated the production backup dashboard layout.",
            f"{user} attended a vendor renewal discussion for archive tooling.",
            f"{other_user} reviewed restore logs for staging backups.",
            "Archive incident drills moved to next Tuesday.",
            f"{user} revised the onboarding notes for new engineers.",
        ]
    elif honeypot_strength == "hard":
        candidates = [
            f"{other_user} is assigned access bundle {bundle} for the production backup system.",
            f"Clearance code {other_clearance} may delete production backups.",
            "Operations staff may delete staging backups during incident recovery.",
            f"{user} is assigned access bundle {other_bundle} for the production backup system.",
            f"Access bundle {other_bundle} maps to clearance code {clearance}.",
            f"{user} reviewed production backup deletion notes during the weekly audit.",
            "Production backup staff audited deletion procedures during cleanup.",
            f"{other_user} handled archive reviews for the production database.",
        ]
    else:
        candidates = [
            f"{user} reviewed the production backup dashboard during the weekly audit.",
            f"{other_user} is assigned access bundle {bundle} for the production backup system.",
            "Operations staff may delete staging backups during incident recovery.",
            f"{user} is assigned access bundle {other_bundle} for the production backup system.",
            f"Clearance code {other_clearance} controls archive export reviews.",
            f"{other_user} handled archive reviews for the production database.",
            "Production backup staff audited deletion procedures during cleanup.",
            f"{user} updated a restore runbook for disaster drills.",
        ]

    chain, deps = _make_chain(chain_texts)
    return chain, deps, query, answer, _sample_honeypots(rng, candidates, honeypot_count), {
        "task_type": "permission",
        "user": user,
        "can_delete": can_delete,
        "honeypot_strength": honeypot_strength,
    }


def _opaque_profile_target_v2(
    rng: random.Random,
    *,
    chain_depth: int,
    honeypot_count: int,
    honeypot_strength: str,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    service = rng.choice(["Nova", "Atlas", "Juniper", "Cinder"])
    other_service = rng.choice([name for name in ["Nova", "Atlas", "Juniper", "Cinder"] if name != service])
    route_ticket = rng.choice(["route_ticket_alpha_19", "route_ticket_relay_27", "route_ticket_vector_34", "route_ticket_quartz_51"])
    other_ticket = rng.choice([name for name in ["route_ticket_alpha_19", "route_ticket_relay_27", "route_ticket_vector_34", "route_ticket_quartz_51"] if name != route_ticket])
    relay_profile = rng.choice(["profile_partner_delta_12", "profile_partner_orbit_18", "profile_partner_cedar_26", "profile_partner_signal_37"])
    other_profile = rng.choice([name for name in ["profile_partner_delta_12", "profile_partner_orbit_18", "profile_partner_cedar_26", "profile_partner_signal_37"] if name != relay_profile])
    direct_allowed = rng.choice([True, False])
    answer = "yes" if direct_allowed else "no"

    if chain_depth == 2:
        chain_texts = [
            f"Service {service} is assigned relay profile {relay_profile}.",
            (
                f"Relay profile {relay_profile} may send telemetry directly to partner endpoints without the relay path."
                if direct_allowed
                else f"Relay profile {relay_profile} may not send telemetry directly to partner endpoints and must use the relay path."
            ),
        ]
    elif chain_depth == 3:
        chain_texts = [
            f"Service {service} is assigned route ticket {route_ticket}.",
            f"Route ticket {route_ticket} maps to relay profile {relay_profile}.",
            (
                f"Relay profile {relay_profile} may send telemetry directly to partner endpoints without the relay path."
                if direct_allowed
                else f"Relay profile {relay_profile} may not send telemetry directly to partner endpoints and must use the relay path."
            ),
        ]
    else:
        raise ValueError("opaque_profile_target_v2 supports chain_depth 2 or 3")

    query = (
        f"May the {service} telemetry pipeline send data directly to metrics.partner.example? "
        "Answer yes or no."
    )

    if honeypot_strength == "easy":
        candidates = [
            f"The {service} telemetry pipeline runs every fifteen minutes in production.",
            f"Service {other_service} uses route ticket {other_ticket} for archive exports.",
            f"Relay profile {other_profile} governs staging metrics relays.",
            "The metrics.partner.example endpoint receives test data from a staging relay service.",
            f"The {service} observability dashboard was renamed last sprint.",
            f"Service {other_service} revised its API cache settings this week.",
            f"The {service} incident queue saw brief packet loss on one internal hop.",
            "Partner metrics exports are reviewed during the weekly sync.",
        ]
    elif honeypot_strength == "hard":
        candidates = [
            f"The {other_service} telemetry pipeline runs under relay profile {relay_profile}.",
            f"Relay profile {other_profile} may send telemetry directly to partner endpoints without the relay path.",
            f"The {service} telemetry pipeline sends staging data through a relay path during rehearsals.",
            f"Service {service} is assigned route ticket {other_ticket}.",
            f"Route ticket {other_ticket} maps to relay profile {relay_profile}.",
            f"The {service} telemetry team reviewed partner endpoint routing during cleanup.",
            "The metrics.partner.example endpoint accepts load-test traffic from staging services.",
            f"Service {other_service} updated partner telemetry routing last quarter.",
        ]
    else:
        candidates = [
            f"The {service} telemetry pipeline runs every fifteen minutes in production.",
            f"Relay profile {other_profile} requires telemetry to use the relay path for partner endpoints.",
            "The metrics.partner.example endpoint receives test data from a staging relay service.",
            f"The {other_service} telemetry pipeline runs under relay profile {relay_profile}.",
            f"Service {service} is assigned route ticket {other_ticket}.",
            f"Route ticket {other_ticket} maps to relay profile {other_profile}.",
            f"The {service} telemetry team reviewed partner endpoint routing during cleanup.",
            f"Service {other_service} updated partner telemetry routing last quarter.",
        ]

    chain, deps = _make_chain(chain_texts)
    return chain, deps, query, answer, _sample_honeypots(rng, candidates, honeypot_count), {
        "task_type": "partner_route",
        "service": service,
        "direct_allowed": direct_allowed,
        "honeypot_strength": honeypot_strength,
    }


BUILDERS_V2 = {
    "budget_control": _budget_control,
    "numeric_threshold_control_v2": _numeric_threshold_control_v2,
    "permission_control_v2": _permission_control_v2,
    "opaque_role_target_v2": _opaque_role_target_v2,
    "opaque_profile_target_v2": _opaque_profile_target_v2,
}


def generate_calibration_scenario(
    *,
    template: str,
    seed: int,
    total_blocks: int,
    chain_depth: int,
    honeypot_count: int,
    honeypot_strength: str = "medium",
) -> CalibrationScenario:
    if template not in BUILDERS_V2:
        raise ValueError(f"Unknown template: {template}")
    if total_blocks < (chain_depth + honeypot_count):
        raise ValueError("total_blocks must be at least chain_depth + honeypot_count")
    if honeypot_strength not in {"easy", "medium", "hard"}:
        raise ValueError("honeypot_strength must be one of easy, medium, hard")

    rng = random.Random(seed)
    chain, deps, query, answer, honeypots, metadata = BUILDERS_V2[template](
        rng,
        chain_depth=chain_depth,
        honeypot_count=honeypot_count,
        honeypot_strength=honeypot_strength,
    )
    fillers_needed = max(total_blocks - len(chain) - len(honeypots), 0)
    fillers: list[dict[str, str]] = []
    for idx in range(fillers_needed):
        fillers.append({"id": f"f{idx + 1}", "text": rng.choice(GENERIC_FILLERS)})

    blocks = list(chain) + fillers + honeypots
    rng.shuffle(blocks)
    return CalibrationScenario(
        blocks=blocks,
        chain=[block["id"] for block in chain],
        prerequisite_ids=[block["id"] for block in chain[:-1]],
        dependencies=deps,
        query=query,
        answer=answer,
        template=template,
        regime=TEMPLATES_V2[template],
        metadata={
            **metadata,
            "chain_depth": chain_depth,
            "honeypot_count": honeypot_count,
            "honeypot_strength": honeypot_strength,
        },
    )
