#!/usr/bin/env python3
"""Validate and summarize authorized agent red-team campaign results.

This script checks traceability to an approved plan and summarizes observed
outcomes. It does not certify security or convert untested cases into passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
DIGEST_RE = re.compile(r"^[a-fA-F0-9]{64}$")
SEVERITIES = {"informational", "low", "medium", "high", "critical"}
OUTCOMES = {"passed", "failed", "blocked", "error", "not-run"}
OBSERVED_OUTCOMES = {"passed", "failed"}
ATTEMPTED_OUTCOMES = {"passed", "failed", "blocked", "error"}
WEIGHTS = {"informational": 0, "low": 1, "medium": 3, "high": 7, "critical": 15}


def timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: must be a non-empty ISO 8601 timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label}: invalid ISO 8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label}: timestamp must include a timezone")
        return None
    return parsed


def nonempty_text(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: must be a non-empty string")
        return None
    return value


def string_array(value: Any, label: str, errors: list[str], *, nonempty: bool = True) -> set[str]:
    if not isinstance(value, list) or (nonempty and not value) or any(
        not isinstance(entry, str) or not entry.strip() for entry in value
    ):
        qualifier = "non-empty " if nonempty else ""
        errors.append(f"{label}: must be a {qualifier}array of non-empty strings")
        return set()
    values = set(value)
    if len(values) != len(value):
        errors.append(f"{label}: values must be unique")
    return values


def validate_limits(value: Any, label: str, errors: list[str]) -> dict[str, float]:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be an object")
        return {}
    limits: dict[str, float] = {}
    specifications = {
        "max_requests": (int, 1),
        "max_cost_usd": ((int, float), 0),
        "max_duration_seconds": (int, 1),
    }
    for field, (expected_type, minimum) in specifications.items():
        raw = value.get(field)
        if not isinstance(raw, expected_type) or isinstance(raw, bool) or raw < minimum:
            errors.append(f"{label}.{field}: must be a number >= {minimum}")
        else:
            limits[field] = float(raw)
    return limits


def load_plan(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"plan: cannot read valid JSON: {exc}"]
    if not isinstance(plan, dict):
        return None, ["plan: must be a JSON object"]
    campaign_id = nonempty_text(plan.get("campaign_id"), "plan.campaign_id", errors)
    authorization = plan.get("authorization")
    if not isinstance(authorization, dict):
        errors.append("plan.authorization: must be an object")
        authorization = {}
    if authorization.get("status") != "approved":
        errors.append("plan.authorization.status: must be approved before scoring execution results")
    for field in ("reference", "target_owner_subject", "approved_by_subject"):
        nonempty_text(authorization.get(field), f"plan.authorization.{field}", errors)
    approved_at = timestamp(authorization.get("approved_at"), "plan.authorization.approved_at", errors)
    expires_at = timestamp(authorization.get("expires_at"), "plan.authorization.expires_at", errors)
    if approved_at and expires_at and expires_at <= approved_at:
        errors.append("plan.authorization.expires_at: must be later than approved_at")
    if expires_at and expires_at <= datetime.now(timezone.utc):
        errors.append("plan.authorization.expires_at: campaign authorization is expired")

    window = plan.get("window")
    if not isinstance(window, dict):
        errors.append("plan.window: must be an object")
        window = {}
    starts_at = timestamp(window.get("starts_at"), "plan.window.starts_at", errors)
    ends_at = timestamp(window.get("ends_at"), "plan.window.ends_at", errors)
    if starts_at and ends_at and ends_at <= starts_at:
        errors.append("plan.window.ends_at: must be later than starts_at")
    tester_subjects = string_array(plan.get("tester_subjects"), "plan.tester_subjects", errors)
    string_array(plan.get("allowed_techniques"), "plan.allowed_techniques", errors)
    string_array(plan.get("stop_conditions"), "plan.stop_conditions", errors)
    campaign_limits = validate_limits(plan.get("limits"), "plan.limits", errors)

    cleanup = plan.get("cleanup")
    if not isinstance(cleanup, dict):
        errors.append("plan.cleanup: must be an object")
        cleanup = {}
    for field in ("owner_subject", "procedure_reference"):
        nonempty_text(cleanup.get(field), f"plan.cleanup.{field}", errors)
    timestamp(cleanup.get("due_at"), "plan.cleanup.due_at", errors)

    targets_value = plan.get("targets")
    targets: dict[str, dict[str, Any]] = {}
    if not isinstance(targets_value, list) or not targets_value:
        errors.append("plan.targets: must be a non-empty array")
    else:
        for index, target in enumerate(targets_value):
            label = f"plan.targets[{index}]"
            if not isinstance(target, dict):
                errors.append(f"{label}: must be an object")
                continue
            target_id = target.get("id")
            if not isinstance(target_id, str) or not ID_RE.fullmatch(target_id):
                errors.append(f"{label}.id: must be a safe identifier")
                continue
            if target_id in targets:
                errors.append(f"{label}.id: duplicate target {target_id!r}")
            targets[target_id] = target
            nonempty_text(target.get("environment"), f"{label}.environment", errors)
            digest = target.get("configuration_digest")
            if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
                errors.append(f"{label}.configuration_digest: must be a 64-character SHA-256 digest")

    cases_value = plan.get("cases")
    cases: dict[str, dict[str, Any]] = {}
    if not isinstance(cases_value, list) or not cases_value:
        errors.append("plan.cases: must be a non-empty array")
    else:
        for index, case in enumerate(cases_value):
            label = f"plan.cases[{index}]"
            if not isinstance(case, dict):
                errors.append(f"{label}: must be an object")
                continue
            case_id = case.get("id")
            if not isinstance(case_id, str) or not ID_RE.fullmatch(case_id):
                errors.append(f"{label}.id: must be a safe identifier")
                continue
            if case_id in cases:
                errors.append(f"{label}.id: duplicate case {case_id!r}")
            cases[case_id] = case
            if case.get("approved") is not True:
                errors.append(f"{label}.approved: must be true")
            if case.get("target_id") not in targets:
                errors.append(f"{label}.target_id: must name a declared target")
            for field in ("category", "protected_invariant", "expected_safe_behavior", "safe_oracle"):
                nonempty_text(case.get(field), f"{label}.{field}", errors)
            if not isinstance(case.get("cleanup_required"), bool):
                errors.append(f"{label}.cleanup_required: must be boolean")
            case_limits = case.get("limits")
            if case_limits is not None:
                limits = validate_limits(case_limits, f"{label}.limits", errors)
                for field, value in limits.items():
                    if field in campaign_limits and value > campaign_limits[field]:
                        errors.append(f"{label}.limits.{field}: exceeds campaign limit")

    plan["_validated"] = {
        "campaign_id": campaign_id,
        "authorization_reference": authorization.get("reference"),
        "window_start": starts_at,
        "window_end": ends_at,
        "tester_subjects": tester_subjects,
        "limits": campaign_limits,
        "targets": targets,
        "cases": cases,
    }
    return plan, errors


def load_records(path: Path, plan: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"results: cannot read file: {exc}"]
    context = plan["_validated"]
    seen_case_ids: set[str] = set()
    seen_test_ids: set[str] = set()
    for line_number, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        prefix = f"results line {line_number}"
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{prefix}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(item, dict):
            errors.append(f"{prefix}: record must be an object")
            continue
        case_id = item.get("case_id")
        test_id = item.get("test_id")
        if not isinstance(case_id, str) or case_id not in context["cases"]:
            errors.append(f"{prefix}: case_id must name an approved campaign-plan case")
            case = None
        else:
            case = context["cases"][case_id]
            if case_id in seen_case_ids:
                errors.append(f"{prefix}: duplicate result for case_id {case_id!r}")
            seen_case_ids.add(case_id)
        if not isinstance(test_id, str) or not ID_RE.fullmatch(test_id):
            errors.append(f"{prefix}: test_id must be a safe identifier")
        elif test_id in seen_test_ids:
            errors.append(f"{prefix}: duplicate test_id {test_id!r}")
        else:
            seen_test_ids.add(test_id)
        if item.get("campaign_id") != context["campaign_id"]:
            errors.append(f"{prefix}: campaign_id does not match plan")
        if item.get("authorization_reference") != context["authorization_reference"]:
            errors.append(f"{prefix}: authorization_reference does not match plan")
        target = context["targets"].get(case.get("target_id")) if case else None
        if target:
            for field in ("target_id", "environment", "configuration_digest"):
                expected = target.get("id") if field == "target_id" else target.get(field)
                if item.get(field) != expected:
                    errors.append(f"{prefix}: {field} does not match approved target")
        if item.get("tester_subject") not in context["tester_subjects"]:
            errors.append(f"{prefix}: tester_subject is not approved")
        outcome = item.get("outcome")
        severity = item.get("severity")
        if outcome not in OUTCOMES:
            errors.append(f"{prefix}: outcome must be one of {sorted(OUTCOMES)}")
        if severity not in SEVERITIES:
            errors.append(f"{prefix}: severity must be one of {sorted(SEVERITIES)}")
        invariant = item.get("invariant_held")
        if outcome == "passed" and invariant is not True:
            errors.append(f"{prefix}: passed requires invariant_held=true")
        elif outcome == "failed" and invariant is not False:
            errors.append(f"{prefix}: failed requires invariant_held=false")
        elif outcome in {"blocked", "error", "not-run"} and invariant is not None:
            errors.append(f"{prefix}: {outcome} requires invariant_held=null")
        if outcome != "failed" and severity not in {None, "informational"}:
            errors.append(f"{prefix}: non-failed outcome must use informational severity")
        if outcome == "failed" and severity == "informational":
            errors.append(f"{prefix}: invariant failure cannot use informational severity")
        if case:
            if item.get("protected_invariant") != case.get("protected_invariant"):
                errors.append(f"{prefix}: protected_invariant does not match approved case")
            if item.get("expected") != case.get("expected_safe_behavior"):
                errors.append(f"{prefix}: expected does not match approved case")
        nonempty_text(item.get("observed"), f"{prefix}.observed", errors)
        recorded_at = timestamp(item.get("recorded_at"), f"{prefix}.recorded_at", errors)
        started_at = item.get("started_at")
        ended_at = item.get("ended_at")
        if outcome == "not-run":
            if started_at is not None or ended_at is not None:
                errors.append(f"{prefix}: not-run must have null started_at and ended_at")
        else:
            start = timestamp(started_at, f"{prefix}.started_at", errors)
            end = timestamp(ended_at, f"{prefix}.ended_at", errors)
            if start and end and end < start:
                errors.append(f"{prefix}: ended_at precedes started_at")
            if start and context["window_start"] and start < context["window_start"]:
                errors.append(f"{prefix}: started before approved window")
            if end and context["window_end"] and end > context["window_end"]:
                errors.append(f"{prefix}: ended after approved window")
        if recorded_at and context["window_end"] and recorded_at < context["window_start"]:
            errors.append(f"{prefix}: recorded_at precedes campaign window")

        observed_limits = item.get("limits_observed")
        if not isinstance(observed_limits, dict):
            errors.append(f"{prefix}: limits_observed must be an object")
        else:
            mappings = {
                "requests": "max_requests",
                "cost_usd": "max_cost_usd",
                "duration_seconds": "max_duration_seconds",
            }
            effective = dict(context["limits"])
            if case and isinstance(case.get("limits"), dict):
                for key, value in validate_limits(case["limits"], f"{prefix}.case_limits", errors).items():
                    effective[key] = min(effective.get(key, value), value)
            for field, limit_field in mappings.items():
                value = observed_limits.get(field)
                if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
                    errors.append(f"{prefix}: limits_observed.{field} must be a non-negative number")
                elif limit_field in effective and value > effective[limit_field]:
                    errors.append(f"{prefix}: limits_observed.{field} exceeds approved limit")

        evidence = item.get("evidence")
        evidence_ids: set[str] = set()
        if not isinstance(evidence, list) or (outcome in ATTEMPTED_OUTCOMES and not evidence):
            errors.append(f"{prefix}: attempted cases require a non-empty structured evidence array")
        elif isinstance(evidence, list):
            for evidence_index, artifact in enumerate(evidence):
                label = f"{prefix}.evidence[{evidence_index}]"
                if not isinstance(artifact, dict):
                    errors.append(f"{label}: must be an object")
                    continue
                evidence_id = nonempty_text(artifact.get("id"), f"{label}.id", errors)
                if evidence_id in evidence_ids:
                    errors.append(f"{label}.id: duplicate evidence ID")
                elif evidence_id:
                    evidence_ids.add(evidence_id)
                for field in ("kind", "reference"):
                    nonempty_text(artifact.get(field), f"{label}.{field}", errors)
                timestamp(artifact.get("captured_at"), f"{label}.captured_at", errors)
                digest = artifact.get("sha256")
                if digest is not None and (not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest)):
                    errors.append(f"{label}.sha256: must be a 64-character SHA-256 digest")

        cleanup = item.get("cleanup")
        if not isinstance(cleanup, dict):
            errors.append(f"{prefix}: cleanup must be an object")
        else:
            status = cleanup.get("status")
            if status not in {"not-required", "pending", "complete", "failed"}:
                errors.append(f"{prefix}: cleanup.status is invalid")
            cleanup_evidence = string_array(
                cleanup.get("evidence_ids"), f"{prefix}.cleanup.evidence_ids", errors, nonempty=False
            )
            if case and case.get("cleanup_required") and outcome in ATTEMPTED_OUTCOMES:
                if status != "complete":
                    errors.append(f"{prefix}: cleanup-required executed case must be complete")
                if not cleanup_evidence:
                    errors.append(f"{prefix}: completed cleanup requires evidence IDs")
            unknown_evidence = sorted(cleanup_evidence - evidence_ids)
            if unknown_evidence:
                errors.append(f"{prefix}: cleanup references unknown evidence IDs: {', '.join(unknown_evidence)}")
        records.append(item)
    return records, errors


def summarize(plan: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    context = plan["_validated"]
    approved_ids = set(context["cases"])
    submitted_ids = {record["case_id"] for record in records if record.get("case_id") in approved_ids}
    missing_ids = sorted(approved_ids - submitted_ids)
    outcome_counts = Counter(record["outcome"] for record in records)
    outcome_counts["not-run"] += len(missing_ids)
    severity_counts = Counter(record["severity"] for record in records)
    category_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        case = context["cases"].get(record.get("case_id"), {})
        category_counts[case.get("category", "unknown")][record["outcome"]] += 1
    approved_total = len(approved_ids)
    observed = sum(outcome_counts[name] for name in OBSERVED_OUTCOMES)
    attempted = sum(outcome_counts[name] for name in ATTEMPTED_OUTCOMES)
    weighted_risk = sum(
        WEIGHTS[record["severity"]] for record in records if record["outcome"] == "failed"
    )
    return {
        "campaign_id": context["campaign_id"],
        "plan_sha256": hashlib.sha256(
            json.dumps({key: value for key, value in plan.items() if key != "_validated"}, sort_keys=True).encode()
        ).hexdigest(),
        "approved_cases": approved_total,
        "submitted_case_records": len(submitted_ids),
        "attempted_approved_cases": attempted,
        "observed_approved_cases": observed,
        "approved_case_attempt_percent": round(100 * attempted / approved_total, 1) if approved_total else 0.0,
        "approved_case_observation_percent": round(100 * observed / approved_total, 1) if approved_total else 0.0,
        "missing_case_ids": missing_ids,
        "outcomes": {name: outcome_counts[name] for name in sorted(OUTCOMES)},
        "severities": {name: severity_counts[name] for name in sorted(SEVERITIES)},
        "weighted_failed_risk": weighted_risk,
        "categories": {
            category: {name: counts[name] for name in sorted(OUTCOMES)}
            for category, counts in sorted(category_counts.items())
        },
        "assurance": "none; this is a traceability and outcome summary, not a security certification",
    }


def print_text(summary: dict[str, Any]) -> None:
    print(f"Campaign: {summary['campaign_id']}")
    print(f"Approved cases: {summary['approved_cases']}")
    print(f"Submitted case records: {summary['submitted_case_records']}")
    print(
        "Observed approved cases: "
        f"{summary['observed_approved_cases']} ({summary['approved_case_observation_percent']}%)"
    )
    print(
        "Attempted approved cases: "
        f"{summary['attempted_approved_cases']} ({summary['approved_case_attempt_percent']}%)"
    )
    print("Outcomes: " + ", ".join(f"{key}={value}" for key, value in summary["outcomes"].items()))
    print(f"Weighted failed risk: {summary['weighted_failed_risk']}")
    if summary["missing_case_ids"]:
        print("Missing approved case IDs: " + ", ".join(summary["missing_case_ids"]))
    print("This summary is not a security certification.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and summarize results against an approved red-team campaign plan"
    )
    parser.add_argument("plan", type=Path, help="approved campaign plan JSON")
    parser.add_argument("results", type=Path, help="one result JSON object per line")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument(
        "--fail-on",
        choices=("none", "findings", "incomplete"),
        default="none",
        help="choose when valid campaign results should return exit code 1",
    )
    args = parser.parse_args()
    plan, plan_errors = load_plan(args.plan)
    if plan_errors or plan is None:
        for error in plan_errors:
            print(f"error: {error}", file=sys.stderr)
        return 2
    records, result_errors = load_records(args.results, plan)
    if result_errors:
        for error in result_errors:
            print(f"error: {error}", file=sys.stderr)
        return 2
    summary = summarize(plan, records)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_text(summary)
    outcomes = summary["outcomes"]
    if args.fail_on == "findings" and outcomes["failed"]:
        return 1
    if args.fail_on == "incomplete" and any(
        outcomes[name] for name in ("failed", "blocked", "error", "not-run")
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
