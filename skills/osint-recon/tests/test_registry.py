"""Use only synthetic records based on publisher contracts."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "norway_registry.py"
FIXTURE = HERE / "fixtures" / "brreg-as.json"
sys.path.insert(0, str(SCRIPT.parent))

from norway_registry import canonical, normalize, plan  # noqa: E402
from registry_adapters import domain_name  # noqa: E402

REQUESTS = {
    "brreg": {"purpose": "organisation_verification", "identifier": "123456785"},
    "norid": {"purpose": "domain_registration", "identifier": "Ærøå.no."},
    "kartverket": {"purpose": "geographic_reference", "identifier": "0301"},
    "ssb": {"purpose": "geographic_reference", "identifier": "0301", "effective_date": "2024-12-31"},
}


def request(source, **overrides):
    return {"schema_version": 1, "source": source, **REQUESTS.get(source, {}), **overrides}


def observation(source, body, http=200):
    return {"source": source, "http_status": http, "body": body}


class RegistryTests(unittest.TestCase):
    def test_brreg_unicode_and_minimization(self):
        out = normalize(request("brreg"), json.loads(FIXTURE.read_text(encoding="utf-8")))
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["records"][0]["fields"],
                         {"name": "Ærø Åshøg AS", "organisation_form": "AS", "bankrupt": False})
        self.assertNotIn("omit@example.invalid", str(out))
        self.assertIsNone(out["provenance"]["retrieved_at"])

    def test_exact_org_identifier_and_checksum(self):
        for invalid in ("123456789", "12345678901", "000000000", "１２３４５６７８５"):
            with self.subTest(invalid=invalid):
                self.assertEqual(plan(request("brreg", identifier=invalid))["status"], "invalid_request")

    def test_brreg_excluded_forms_are_fail_closed(self):
        for form in (None, "ENK", "FLI", []):
            data = observation("brreg", {"organisasjonsnummer": "123456785",
                                         "organisasjonsform": {"kode": form}, "navn": "redacted"})
            out = normalize(request("brreg"), data)
            self.assertEqual(out["status"], "prohibited")
            self.assertNotIn("redacted", str(out))
            self.assertNotIn("123456785", str(out))

    def test_municipality_leading_zero_and_multilingual_fields(self):
        data = observation("kartverket", {"kommunenummer": "0301", "kommunenavn": "Øy – Ŋá",
                                           "kommunenavnNorsk": "Øy", "fylkesnummer": "03"})
        out = normalize(request("kartverket"), data)
        self.assertEqual(out["records"][0]["identifier"], "0301")
        self.assertEqual(out["records"][0]["fields"]["name"], "Øy – Ŋá")
        query = urlsplit(out["provenance"]["endpoint"])
        self.assertEqual(query.hostname, "api.kartverket.no")
        self.assertIn("kommunenummer", parse_qs(query.query)["filtrer"][0])

    def test_incomplete_record(self):
        data = observation("kartverket", {"kommunenummer": "0301", "kommunenavn": None,
                                           "fylkesnummer": 3})
        out = normalize(request("kartverket"), data)
        self.assertEqual(out["status"], "partial")
        self.assertEqual(out["records"][0]["confidence"], "exact_identifier_incomplete")
        self.assertIsNone(out["records"][0]["fields"]["county_code"])

    def test_domain_idn_round_trip_and_rdap_redaction(self):
        prefix = plan(request("norid"))
        identifier = prefix["identifier"]
        self.assertTrue(identifier.startswith("xn--"))
        self.assertEqual(domain_name(identifier), domain_name("ærøå.no"))
        self.assertEqual(domain_name(domain_name("ïŋ.no")), domain_name("ïŋ.no"))
        data = observation("norid", {"objectClassName": "domain", "ldhName": identifier,
                                     "status": ["active", "arbitrary text", None, {}],
                                     "entities": [{"vcardArray": ["omit this"]}]})
        out = normalize(request("norid"), data)
        self.assertEqual(out["records"][0]["fields"]["registration_status"], ["active"])
        self.assertNotIn("omit this", str(out))

    def test_domain_rejects_urls_wildcards_and_unsupported_labels(self):
        for invalid in ("https://test.no", "*.no", "test.no.evil", "test.no/path", "xn--invalid-.no",
                        "a..no", "a.no", "test.no..", "a☃.no"):
            with self.subTest(invalid=invalid):
                self.assertEqual(plan(request("norid", identifier=invalid))["status"], "invalid_request")

    def test_ssb_filter_and_conflicting_identity_data(self):
        proposal = plan(request("ssb"))
        query = parse_qs(urlsplit(proposal["proposed_request"]["url"]).query)
        self.assertEqual(query, {"date": ["2024-12-31"], "selectCodes": ["0301"]})
        rows = [{"code": "0301", "name": "Første"}, {"code": "0301", "name": "Andre"}]
        out = normalize(request("ssb"), observation("ssb", {"codes": rows}))
        self.assertEqual(out["status"], "conflict")
        self.assertEqual([r["confidence"] for r in out["records"]], ["conflicting", "conflicting"])
        self.assertEqual(out["provenance"]["effective_date"], "2024-12-31")

    def test_duplicate_ssb_rows_do_not_create_conflict(self):
        row = {"code": "0301", "name": "Prøve"}
        out = normalize(request("ssb"), observation("ssb", {"codes": [row, row]}))
        self.assertEqual(out["status"], "ok")
        self.assertEqual(len(out["records"]), 1)

    def test_conflicting_identifier_is_quarantined(self):
        out = normalize(request("kartverket"), observation("kartverket", {"kommunenummer": "9999"}))
        self.assertEqual(out["status"], "conflict")
        self.assertEqual(out["records"], [])
        self.assertNotIn("9999", str(out))

    def test_upstream_outcomes_are_distinct_and_body_is_ignored(self):
        for code, status in {404: "not_found", 403: "upstream_denied", 429: "rate_limited",
                             503: "upstream_error", 302: "upstream_error"}.items():
            with self.subTest(code=code):
                out = normalize(request("brreg"), observation("brreg", {"error": "omit"}, code))
                self.assertEqual(out["status"], status)
                self.assertEqual(out["provenance"]["http_status"], code)
                self.assertNotIn("omit", str(out))
        for failure in ("timeout", "unavailable"):
            self.assertEqual(normalize(request("brreg"), {"source": "brreg", "error": failure})["status"],
                             failure)

    def test_malformed_upstream_and_empty_result(self):
        self.assertEqual(normalize(request("brreg"), observation("norid", {}))["status"], "invalid_response")
        self.assertEqual(normalize(request("brreg"), observation("brreg", []))["status"], "invalid_response")
        self.assertEqual(normalize(request("ssb"), observation("ssb", {"codes": []}))["status"], "not_found")

    def test_logged_lookup_is_manual_and_never_echoes_identifier(self):
        for source in ("tax_list", "vehicle_owner", "public_journal", "licensed_directory", "brreg_roles"):
            out = plan(request(source, purpose="organisation_verification", identifier="private-value"))
            self.assertEqual(out["status"], "approval_required")
            self.assertIs(out["executable"], False)
            self.assertNotIn("private-value", str(out))
            self.assertNotIn("proposed_request", out)

    def test_prohibited_lookup_and_self_approval(self):
        for source in ("email", "person", "phone", "property_owner", "national_id", "sherlock"):
            out = plan(request(source, purpose="organisation_verification", identifier="private-value"))
            self.assertEqual(out["status"], "prohibited")
            self.assertNotIn("private-value", str(out))
        self.assertEqual(plan(request("brreg", approved=True))["status"], "invalid_request")
        self.assertEqual(plan(request("brreg", purpose="private_investigation"))["status"], "prohibited")
        self.assertEqual(plan(request("brreg", purpose="domain_registration"))["status"], "prohibited")

    def test_json_contract_hash_and_exit_codes(self):
        base = [sys.executable, "-B", str(SCRIPT)]
        cmd = base + ["fixture", "--fixture", str(FIXTURE)]
        result = subprocess.run(cmd, input=canonical(request("brreg")), capture_output=True)
        out = json.loads(result.stdout)
        digest = out.pop("output_sha256")
        self.assertEqual(digest, hashlib.sha256(canonical(out)).hexdigest())
        self.assertIn("Ærø Åshøg", result.stdout.decode("utf-8"))
        self.assertEqual(result.returncode, 0)
        result = subprocess.run(base + ["plan"], input=canonical(request("brreg")), capture_output=True)
        self.assertEqual(result.returncode, 3)
        self.assertIs(json.loads(result.stdout)["executable"], False)

    def test_invalid_input_and_forbidden_request_never_reads_fixture(self):
        base = [sys.executable, "-B", str(SCRIPT)]
        denied = request("national_id", purpose="organisation_verification")
        result = subprocess.run(base + ["fixture", "--fixture", "/nonexistent"],
                                input=canonical(denied), capture_output=True)
        self.assertEqual(result.returncode, 4)
        for data in (b'{"a": 1, "a": 2}', b"[]", b"x" * (256 * 1024 + 1), b'{"invalid": NaN}'):
            with self.subTest(size=len(data)):
                result = subprocess.run(base + ["plan"], input=data, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "invalid_request")


if __name__ == "__main__":
    unittest.main()
