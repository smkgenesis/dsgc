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


TEMPLATES = {
    "budget_control": "control",
    "permission_control": "control",
    "opaque_role_target": "target",
    "opaque_profile_target": "target",
}


@dataclass(slots=True)
class MinimalScenario:
    blocks: list[dict[str, str]]
    chain: list[str]
    prerequisite_ids: list[str]
    dependencies: list[tuple[str, str]]
    query: str
    answer: str
    template: str
    regime: str
    metadata: dict[str, str | int | bool] = field(default_factory=dict)


def _budget_control(
    rng: random.Random,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    project = rng.choice(["Atlas", "Helios", "Juniper", "Cinder"])
    budget = rng.choice([480, 600, 720, 840])
    percent = rng.choice([25, 30, 40])
    threshold = int(budget * percent / 100)
    cost = rng.choice([threshold - 40, threshold - 10, threshold + 10, threshold + 40])
    answer = "yes" if cost <= threshold else "no"
    other_project = rng.choice([name for name in ["Atlas", "Helios", "Juniper", "Cinder"] if name != project])

    chain = [
        {"id": "c1", "text": f"Project {project} has a backup budget of {budget} credits this quarter."},
        {
            "id": "c2",
            "text": f"{project} backup jobs are allowed under the backup budget only when their cost stays within {percent} percent of that backup budget.",
        },
    ]
    deps = [("c2", "c1")]
    query = (
        f"A backup job for Project {project} costs {cost} credits. "
        "Is it allowed under the backup budget? Answer yes or no."
    )
    honeypots = [
        {"id": "h1", "text": f"Project {project} has a travel allowance of {budget} credits for vendor visits."},
        {
            "id": "h2",
            "text": f"{project} database migrations may spend at most {percent} percent of the infrastructure budget.",
        },
        {
            "id": "h3",
            "text": f"An archive rehearsal for Project {other_project} cost {cost} credits during cleanup.",
        },
        {
            "id": "h4",
            "text": f"Project {project} has an infrastructure reserve of {budget + 120} credits for disaster drills.",
        },
    ]
    metadata = {
        "project": project,
        "budget": budget,
        "percent": percent,
        "cost": cost,
    }
    return chain, deps, query, answer, honeypots, metadata


def _permission_control(
    rng: random.Random,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    user = rng.choice(["Alice", "Bob", "Casey", "Dana"])
    role = rng.choice(["backup admin", "backup auditor"])
    answer = "yes" if role == "backup admin" else "no"
    other_user = rng.choice([name for name in ["Alice", "Bob", "Casey", "Dana"] if name != user])

    chain = [
        {
            "id": "c1",
            "text": (
                f"{user} is the {role} responsible for deletion policy on the production database."
                if role == "backup admin"
                else f"{user} is the {role} responsible for review policy on the production database."
            ),
        },
        {
            "id": "c2",
            "text": (
                "Backup admins may delete production backups."
                if role == "backup admin"
                else "Backup auditors may review production backups but may not delete them."
            ),
        },
    ]
    deps = [("c2", "c1")]
    query = f"Can {user} delete the production database backup? Answer yes or no."
    honeypots = [
        {"id": "h1", "text": f"{user} reviewed the production backup dashboard during the weekly audit."},
        {"id": "h2", "text": f"{other_user} is the backup admin for the production database."},
        {"id": "h3", "text": "Backup admins may delete staging backups after incident approval."},
        {"id": "h4", "text": f"{user} is the release admin for the reporting database."},
    ]
    metadata = {"user": user, "role": role}
    return chain, deps, query, answer, honeypots, metadata


def _opaque_role_target(
    rng: random.Random,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    user = rng.choice(["Alice", "Bob", "Casey", "Dana"])
    other_user = rng.choice([name for name in ["Alice", "Bob", "Casey", "Dana"] if name != user])
    role = rng.choice(["orbital_viewer", "cedar_key", "amber_lock", "quartz_scope"])
    other_role = rng.choice([name for name in ["orbital_viewer", "cedar_key", "amber_lock", "quartz_scope"] if name != role])
    can_delete = rng.choice([True, False])
    answer = "yes" if can_delete else "no"

    chain = [
        {"id": "c1", "text": f"{user} was assigned internal role '{role}' for the production backup system."},
        {
            "id": "c2",
            "text": (
                f"Internal role '{role}' may delete production backups."
                if can_delete
                else f"Internal role '{role}' may review production backups but may not delete them."
            ),
        },
    ]
    deps = [("c2", "c1")]
    query = f"Can {user} delete the production database backup? Answer yes or no."
    honeypots = [
        {"id": "h1", "text": f"{user} reviewed the production backup dashboard during the weekly audit."},
        {"id": "h2", "text": f"{other_user} was assigned internal role '{role}' for the production backup system."},
        {"id": "h3", "text": "Operations staff may delete production backups during incident recovery."},
        {"id": "h4", "text": f"{user} was assigned internal role '{other_role}' for the production backup system."},
    ]
    metadata = {"user": user, "role": role, "can_delete": can_delete}
    return chain, deps, query, answer, honeypots, metadata


def _opaque_profile_target(
    rng: random.Random,
) -> tuple[list[dict[str, str]], list[tuple[str, str]], str, str, list[dict[str, str]], dict[str, str | int | bool]]:
    service = rng.choice(["Nova", "Atlas", "Juniper", "Cinder"])
    other_service = rng.choice([name for name in ["Nova", "Atlas", "Juniper", "Cinder"] if name != service])
    profile = rng.choice(["amber-sigma", "cedar-12", "relay-rho", "quartz-7"])
    other_profile = rng.choice([name for name in ["amber-sigma", "cedar-12", "relay-rho", "quartz-7"] if name != profile])
    direct_allowed = rng.choice([True, False])
    answer = "yes" if direct_allowed else "no"

    chain = [
        {"id": "c1", "text": f"Service {service} is tagged with compliance profile '{profile}'."},
        {
            "id": "c2",
            "text": (
                f"Compliance profile '{profile}' says this service may send telemetry directly to partner endpoints without the relay path."
                if direct_allowed
                else f"Compliance profile '{profile}' says this service may not send telemetry directly to partner endpoints and must use the relay path."
            ),
        },
    ]
    deps = [("c2", "c1")]
    query = (
        f"May the {service} telemetry pipeline send data directly to metrics.partner.example? "
        "Answer yes or no."
    )
    honeypots = [
        {"id": "h1", "text": f"The {service} telemetry pipeline runs every fifteen minutes in production."},
        {
            "id": "h2",
            "text": f"Compliance profile '{other_profile}' requires the telemetry pipeline to use the relay path for partner endpoints.",
        },
        {"id": "h3", "text": "The metrics.partner.example endpoint receives test data from a staging relay service."},
        {"id": "h4", "text": f"The {other_service} telemetry pipeline runs under compliance profile '{profile}'."},
    ]
    metadata = {"service": service, "profile": profile, "direct_allowed": direct_allowed}
    return chain, deps, query, answer, honeypots, metadata


BUILDERS = {
    "budget_control": _budget_control,
    "permission_control": _permission_control,
    "opaque_role_target": _opaque_role_target,
    "opaque_profile_target": _opaque_profile_target,
}


def generate_minimal_scenario(
    template: str,
    seed: int,
    total_blocks: int,
) -> MinimalScenario:
    if template not in BUILDERS:
        raise ValueError(f"Unknown template: {template}")
    if total_blocks < 10:
        raise ValueError("total_blocks must be at least 10 for the minimal benchmark")

    rng = random.Random(seed)
    chain, deps, query, answer, honeypots, metadata = BUILDERS[template](rng)
    fillers_needed = max(total_blocks - len(chain) - len(honeypots), 0)
    fillers: list[dict[str, str]] = []
    for idx in range(fillers_needed):
        fillers.append({"id": f"f{idx + 1}", "text": rng.choice(GENERIC_FILLERS)})

    blocks = list(chain) + fillers + honeypots
    rng.shuffle(blocks)
    return MinimalScenario(
        blocks=blocks,
        chain=["c1", "c2"],
        prerequisite_ids=["c1"],
        dependencies=deps,
        query=query,
        answer=answer,
        template=template,
        regime=TEMPLATES[template],
        metadata=metadata,
    )
