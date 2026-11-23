# Norwegian registry workflow

The bundled Python 3.12 CLI accepts one UTF-8 JSON object on stdin and prints one versioned JSON result on stdout. It has two offline modes, `plan` for an operator review item and `fixture` for normalization of a supplied offline response. Each mode processes one source and one exact identifier. No packages, credentials or network access are required.

| Source value | Purpose value | Identifier | Source fields retained |
| --- | --- | --- | --- |
| `brreg` | `organisation_verification` | Nine-digit organisation number, with checksum | Registered name, legal form, bankruptcy flag. Legal form must be AS, ASA, IKS, KF or SF in this initial scope. |
| `kartverket` | `geographic_reference` | Four-digit municipality code as a string | Official name, Norwegian name, county code. The query requests only these fields and the municipality identifier. |
| `norid` | `domain_registration` | Exact .no domain, Unicode or A-label | Canonical domain and recognized RDAP statuses. Discards contacts, registrant details, nameservers and links. |
| `ssb` | `geographic_reference` | Four-digit municipality code and an `effective_date` in YYYY-MM-DD | Classification 131 name for the supplied date. Retain that date beside the claim. |

## Command contract

From the repository root, use synthetic case data to try the interface.

```sh
printf '%s\n' '{"schema_version":1,"source":"brreg","purpose":"organisation_verification","identifier":"123456785"}' |
  python3 skills/osint-recon/scripts/norway_registry.py plan

printf '%s\n' '{"schema_version":1,"source":"brreg","purpose":"organisation_verification","identifier":"123456785"}' |
  python3 skills/osint-recon/scripts/norway_registry.py fixture --fixture skills/osint-recon/tests/fixtures/brreg-as.json
```

The fixture envelope is `{"source":"brreg","http_status":200,"body":{...}}` for provider responses or `{"source":"brreg","error":"timeout"}` with `timeout` or `unavailable` for transport failures. Both input files are bounded at 256 KiB. A fixture can be authored by anyone. The CLI marks fixture output accordingly and leaves `retrieved_at` null.

Every result includes `schema_version`, `status`, `records` and `output_sha256`. A valid plan also includes `proposed_request`, `executable:false` and the normalized identifier. Evidence output carries publisher, documentation URL, requested endpoint, effective date, and HTTP status when available. Fields outside each adapter's allowlist are discarded. Unknown values remain null. `exact_identifier` describes the join key only, and `exact_identifier_incomplete` indicates a missing name. `conflicting` leaves the alternatives visible. A mismatched identifier is quarantined with an empty record list. Do not join organisations by names or infer a person from registry, municipality or domain results.

The hash covers the normalized JSON object with `output_sha256` removed, encoded as UTF-8 with sorted keys, compact separators and unescaped Unicode. It supports change detection and conveys no source authentication, retrieval proof or signature.

| Exit | Status | Automation action |
| --- | --- | --- |
| 0 | `ok`, `partial` | Display normalized evidence with its confidence and missing fields. |
| 2 | `invalid_request` | Correct the input. |
| 3 | `approval_required` | Display a local review item. Stop. |
| 4 | `prohibited` | Stop without preserving the rejected identifier. |
| 5 | `invalid_response` | Mark the evidence unusable. |
| 6 | `not_found` | Mark no record returned by this source and query. |
| 7 | `rate_limited`, `timeout`, `unavailable`, `upstream_denied`, `upstream_error` | Mark inconclusive. Avoid automatic retries or alternate queries. |
| 8 | `conflict` | Queue local review of the evidence. |

## Termux and Tasker handoff

A future Termux wrapper can run the static Python command with a request file redirected to stdin and receive the JSON result and exit status. Keep request, fixture and result files in the app's private directory with `umask 077`. Pass values as JSON data. Keep command text, script path and any fixture path fixed by the wrapper. For Tasker, a foreground action can submit one request to the Termux wrapper after local validation. Treat exit 3 as an approval-needed UI state and exit 4 as terminal. Keep identifiers, source URLs, and raw records out of Tasker notifications, history and analytics. A timed task, incoming intent, profile action or tool invocation cannot approve or execute live collection. No Tasker project or wrapper is installed by this patch.

## Operator approval

The CLI has no network transport, live flag, credentials, or activation switch. A request containing an approval field cannot enable a lookup. Logged and sensitive sources produce a manual-review result without an identifier or URL. They include tax lists, vehicle owner records, public journals, commercial directories and Brreg roles. Unknown and prohibited lookups are denied. Any later live integration must be separately approved and have an independent operator-controlled gate binding the authorized purpose, exact identifier, provider and expiration to a single request. Keep authority separate from agent-controlled state.

For an approved future broker, use fixed hosts and validated endpoint paths, forbid redirects and arbitrary URLs, bound response size and timeout, and set per-provider request budgets. Norid documents 10 combined lookups per minute and 300 GETs per IP over a rolling 24-hour window. Include shared-egress traffic in that accounting. A provider can log a query even when it accesses a public API. Use minimal access-controlled case records and retention periods set by the controller. Keep paid, sensitive and logged workflows outside any automatic execution path.
