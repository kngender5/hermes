#!/usr/bin/env python3
"""Offline Norwegian registry planning and normalization for Hermes and Termux."""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import BinaryIO

from registry_adapters import ADAPTERS, JSON, IdentityConflict, RestrictedRecord, effective_date

MANUAL = frozenset({"tax_list", "vehicle_owner", "public_journal", "licensed_directory", "brreg_roles"})
MAX_JSON_BYTES = 256 * 1024
EXIT_CODES = {
    "ok": 0, "partial": 0, "approval_required": 3, "prohibited": 4,
    "invalid_request": 2, "invalid_response": 5, "not_found": 6,
    "upstream_denied": 7, "rate_limited": 7, "upstream_error": 7,
    "timeout": 7, "unavailable": 7, "conflict": 8,
}


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def envelope(status: str, **fields: object) -> JSON:
    output = {"schema_version": 1, "status": status, "records": [], **fields}
    output["output_sha256"] = hashlib.sha256(canonical(output)).hexdigest()
    return output


def read_json(stream: BinaryIO) -> JSON:
    def unique_object(pairs: list[tuple]) -> JSON:
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("duplicate_json_key")
        return result

    def reject_constant(_: str) -> None:
        raise ValueError("invalid_json_constant")

    data = stream.read(MAX_JSON_BYTES + 1)
    if len(data) > MAX_JSON_BYTES:
        raise ValueError("json_size_limit")
    obj = json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                     parse_constant=reject_constant)
    if not isinstance(obj, dict):
        raise ValueError("expected_json_object")
    return obj


def plan(request: JSON) -> JSON:
    source = request.get("source")
    purpose = request.get("purpose")
    if not isinstance(source, str) or not isinstance(purpose, str) or request.get("schema_version") != 1:
        return envelope("invalid_request", reason="invalid_request_fields")
    if type(request["schema_version"]) is not int:
        return envelope("invalid_request", reason="invalid_request_version")
    if purpose not in {"organisation_verification", "domain_registration", "geographic_reference"}:
        return envelope("prohibited", reason="unsupported_purpose")
    if source in MANUAL:
        return envelope("approval_required", reason="manual_source_review", executable=False)
    if source not in ADAPTERS:
        return envelope("prohibited", reason="unsupported_lookup")
    expected_purpose = {
        "brreg": "organisation_verification", "norid": "domain_registration",
        "kartverket": "geographic_reference", "ssb": "geographic_reference",
    }[source]
    if purpose != expected_purpose:
        return envelope("prohibited", reason="source_purpose_mismatch")
    allowed_keys = {"schema_version", "source", "purpose", "identifier"}
    if source == "ssb":
        allowed_keys.add("effective_date")
    identifier = request.get("identifier")
    if request.keys() != allowed_keys or not isinstance(identifier, str) or len(identifier) > 254:
        return envelope("invalid_request", reason="invalid_request_fields")
    adapter = ADAPTERS[source]
    try:
        identifier = adapter.identifier(identifier)
        as_of = effective_date(request["effective_date"]) if source == "ssb" else None
    except ValueError as error:
        return envelope("invalid_request", reason=str(error))
    return envelope(
        "approval_required", mode="offline", executable=False, reason="external_collection_disabled",
        source=source, purpose=purpose, identifier=identifier, effective_date=as_of,
        proposed_request={"method": "GET", "url": adapter.url(identifier, as_of), "accept": adapter.accept},
    )


def normalize(request: JSON, fixture: JSON) -> JSON:
    proposal = plan(request)
    if proposal.get("reason") != "external_collection_disabled":
        return proposal
    source = proposal["source"]
    adapter = ADAPTERS[source]
    identifier = proposal["identifier"]
    provenance = {
        "source": source,
        "publisher": adapter.publisher,
        "documentation": adapter.documentation,
        "endpoint": proposal["proposed_request"]["url"],
        "effective_date": proposal["effective_date"],
        "retrieved_at": None,
    }
    context = {"mode": "fixture", "provenance": provenance}
    if fixture.get("source") != source:
        return envelope("invalid_response", reason="fixture_source_mismatch", **context)
    if fixture.get("error") in ("timeout", "unavailable") and set(fixture) == {"source", "error"}:
        return envelope(fixture["error"], **context)
    http = fixture.get("http_status")
    if type(http) is not int or not 100 <= http <= 599:
        return envelope("invalid_response", reason="invalid_http_status", **context)
    provenance["http_status"] = http
    if http != 200:
        status = {404: "not_found", 401: "upstream_denied", 403: "upstream_denied",
                  429: "rate_limited"}.get(http, "upstream_error")
        return envelope(status, **context)
    body = fixture.get("body")
    if not isinstance(body, dict):
        return envelope("invalid_response", reason="invalid_body", **context)
    try:
        fields = adapter.parse(body, identifier)
    except IdentityConflict:
        return envelope("conflict", reason="source_identifier_mismatch", **context)
    except RestrictedRecord:
        return envelope("prohibited", reason="record_scope_restricted", mode="fixture")
    except ValueError:
        return envelope("invalid_response", reason="invalid_registry_record", **context)
    if not fields:
        return envelope("not_found", **context)
    unique = {canonical(row): row for row in fields}
    conflict = len(unique) > 1
    records = []
    for row in unique.values():
        incomplete = row["name"] is None
        confidence = "conflicting" if conflict else "exact_identifier_incomplete" if incomplete else "exact_identifier"
        records.append({"entity_type": adapter.entity_type, "identifier": identifier,
                        "confidence": confidence, "fields": row})
    status = "ok"
    if conflict:
        status = "conflict"
    elif records[0]["confidence"] == "exact_identifier_incomplete":
        status = "partial"
    return envelope(status, records=records, **context)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["plan", "fixture"])
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args()
    if (args.mode == "fixture") != (args.fixture is not None):
        parser.error("fixture mode requires --fixture; plan mode accepts stdin only")
    try:
        request = read_json(sys.stdin.buffer)
    except (OSError, ValueError, RecursionError):
        output = envelope("invalid_request", reason="invalid_request_json")
    else:
        output = plan(request)
        if args.mode == "fixture" and output.get("reason") == "external_collection_disabled":
            try:
                with args.fixture.open("rb") as stream:
                    fixture = read_json(stream)
            except (OSError, ValueError, RecursionError):
                output = envelope("invalid_response", reason="invalid_fixture_json")
            else:
                output = normalize(request, fixture)
    sys.stdout.buffer.write(canonical(output) + b"\n")
    return EXIT_CODES[output["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
