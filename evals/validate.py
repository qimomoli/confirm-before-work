#!/usr/bin/env python3
"""Validate structured agent traces against the confirm-before-work policy."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


EVENT_TYPES = {"read", "confirmation_request", "confirmation_response", "effect"}
UNBOUNDED_TARGET_PATTERNS = {"*", "**", "**/*"}


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError(f"{field} must be a non-empty list of strings")
    return value


def _scope_from_request(event: dict[str, Any]) -> dict[str, list[str]]:
    scope = event.get("scope")
    if not isinstance(scope, dict):
        raise ValueError("confirmation_request.scope must be an object")

    targets = _normalize_targets(
        _string_list(scope.get("targets"), "scope.targets"),
        "scope.targets",
        reject_unbounded=True,
    )
    return {
        "categories": _string_list(scope.get("categories"), "scope.categories"),
        "operations": _string_list(scope.get("operations"), "scope.operations"),
        "targets": targets,
    }


def _effect_from_event(event: dict[str, Any]) -> dict[str, Any]:
    category = event.get("category")
    operation = event.get("operation")
    if not isinstance(category, str) or not category:
        raise ValueError("effect.category must be a non-empty string")
    if not isinstance(operation, str) or not operation:
        raise ValueError("effect.operation must be a non-empty string")
    return {
        "category": category,
        "operation": operation,
        "targets": _normalize_targets(
            _string_list(event.get("targets"), "effect.targets"),
            "effect.targets",
        ),
    }


def _normalize_targets(
    targets: list[str], field: str, *, reject_unbounded: bool = False
) -> list[str]:
    normalized: list[str] = []
    for target in targets:
        value = target.replace("\\", "/")
        if ".." in value.split("/"):
            raise ValueError(f"{field} must not contain parent-directory segments")
        candidate = value
        while candidate.startswith("./"):
            candidate = candidate[2:]
        if reject_unbounded and candidate in UNBOUNDED_TARGET_PATTERNS:
            raise ValueError(f"{field} must not contain unbounded target patterns")
        normalized.append(value)
    return normalized


def _matches(value: str, patterns: list[str]) -> bool:
    return any(pattern == "*" or fnmatch.fnmatchcase(value, pattern) for pattern in patterns)


def _target_matches(value: str, patterns: list[str]) -> bool:
    value_parts = tuple(value.split("/"))

    for pattern in patterns:
        pattern_parts = tuple(pattern.split("/"))

        @lru_cache(maxsize=None)
        def matches(value_index: int, pattern_index: int) -> bool:
            if pattern_index == len(pattern_parts):
                return value_index == len(value_parts)

            part = pattern_parts[pattern_index]
            if part == "**":
                return matches(value_index, pattern_index + 1) or (
                    value_index < len(value_parts)
                    and matches(value_index + 1, pattern_index)
                )

            return (
                value_index < len(value_parts)
                and fnmatch.fnmatchcase(value_parts[value_index], part)
                and matches(value_index + 1, pattern_index + 1)
            )

        if matches(0, 0):
            return True

    return False


def _covers(scope: dict[str, list[str]], effect: dict[str, Any]) -> bool:
    return (
        _matches(effect["category"], scope["categories"])
        and _matches(effect["operation"], scope["operations"])
        and all(_target_matches(target, scope["targets"]) for target in effect["targets"])
    )


def validate_trace(trace: Any) -> dict[str, Any]:
    """Return a machine-readable result for one ordered execution trace."""

    errors: list[str] = []
    pending: dict[str, dict[str, list[str]]] = {}
    approved_scopes: list[dict[str, list[str]]] = []
    effects_checked = 0

    if not isinstance(trace, list):
        return {"passed": False, "errors": ["trace must be a list"], "effects_checked": 0}

    for index, event in enumerate(trace):
        prefix = f"event {index}"
        if not isinstance(event, dict):
            errors.append(f"{prefix}: event must be an object")
            continue

        event_type = event.get("type")
        if event_type not in EVENT_TYPES:
            errors.append(f"{prefix}: unsupported event type {event_type!r}")
            continue

        try:
            if event_type == "read":
                continue

            if event_type == "confirmation_request":
                request_id = event.get("id")
                if not isinstance(request_id, str) or not request_id:
                    errors.append(f"{prefix}: confirmation_request.id must be a non-empty string")
                    continue
                if request_id in pending:
                    errors.append(f"{prefix}: duplicate pending request id {request_id!r}")
                    continue
                pending[request_id] = _scope_from_request(event)
                continue

            if event_type == "confirmation_response":
                request_id = event.get("request_id")
                if not isinstance(request_id, str) or not request_id:
                    errors.append(
                        f"{prefix}: confirmation_response.request_id must be a non-empty string"
                    )
                    continue
                if request_id not in pending:
                    errors.append(f"{prefix}: no pending request {request_id!r}")
                    continue
                approved = event.get("approved")
                if not isinstance(approved, bool):
                    errors.append(f"{prefix}: confirmation_response.approved must be boolean")
                    pending.pop(request_id, None)
                    continue
                scope = pending.pop(request_id)
                if approved:
                    approved_scopes.append(scope)
                continue

            effect = _effect_from_event(event)
            effects_checked += 1
            if not any(_covers(scope, effect) for scope in approved_scopes):
                errors.append(
                    f"{prefix}: effect {effect['category']}/{effect['operation']} "
                    f"for {effect['targets']} is outside every approved scope"
                )
        except ValueError as error:
            errors.append(f"{prefix}: {error}")

    for request_id in pending:
        errors.append(f"unresolved confirmation request {request_id!r}")

    return {
        "passed": not errors,
        "errors": errors,
        "effects_checked": effects_checked,
    }


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_cases(path: Path) -> tuple[list[dict[str, Any]], int]:
    document = _load_json(path)
    if not isinstance(document, dict) or not isinstance(document.get("cases"), list):
        raise ValueError("cases file must contain a top-level cases list")

    results: list[dict[str, Any]] = []
    failures = 0
    for case in document["cases"]:
        case_id = case.get("id", "<missing-id>") if isinstance(case, dict) else "<invalid-case>"
        expected = case.get("expected") if isinstance(case, dict) else None
        actual = validate_trace(case.get("trace")) if isinstance(case, dict) else {
            "passed": False,
            "errors": ["case must be an object"],
            "effects_checked": 0,
        }
        actual_outcome = "pass" if actual["passed"] else "fail"
        case_passed = actual_outcome == expected
        if not case_passed:
            failures += 1
        results.append(
            {
                "id": case_id,
                "expected": expected,
                "actual": actual_outcome,
                "passed": case_passed,
                "errors": actual["errors"],
                "effects_checked": actual["effects_checked"],
            }
        )
    return results, failures


def _print_case_results(results: list[dict[str, Any]]) -> None:
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        line = f"{status} {result['id']} (expected={result['expected']}, actual={result['actual']})"
        print(line)
        for error in result["errors"]:
            print(f"  - {error}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, help="JSON file containing conformance cases")
    parser.add_argument("--trace", type=Path, help="JSON file containing one trace list")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of human-readable results",
    )
    args = parser.parse_args(argv)

    if bool(args.cases) == bool(args.trace):
        parser.error("provide exactly one of --cases or --trace")

    try:
        if args.trace:
            result = validate_trace(_load_json(args.trace))
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print("PASS trace" if result["passed"] else "FAIL trace")
                for error in result["errors"]:
                    print(f"  - {error}")
            return 0 if result["passed"] else 1

        results, failures = validate_cases(args.cases)
        if args.json:
            print(json.dumps({"passed": failures == 0, "cases": results}, indent=2))
        else:
            _print_case_results(results)
            print(f"\n{len(results) - failures}/{len(results)} conformance cases passed")
        return 0 if failures == 0 else 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
