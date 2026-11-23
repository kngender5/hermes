"""Endpoint contracts and field allowlists for the Norwegian registry workflow."""

import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.parse import urlencode

JSON = dict[str, Any]
FORMS = frozenset({"AS", "ASA", "IKS", "KF", "SF"})
IDN_LETTERS = "áàäčçđéèêïŋńñóòôöšŧüžæøå"


class IdentityConflict(ValueError):
    """The provider returned a record for a different identifier."""


class RestrictedRecord(ValueError):
    """The provider response falls outside the permitted output scope."""


def clean_text(value: object) -> str | None:
    if not isinstance(value, str) or any(
        unicodedata.category(char).startswith("C") for char in value
    ):
        return None
    normalized = unicodedata.normalize("NFC", value).strip()
    return normalized if 0 < len(normalized) <= 256 else None


def domain_name(value: str) -> str:
    """Return a lowercase Norid A-label, retaining Norwegian and Sami letters."""
    name = unicodedata.normalize("NFC", value.lower()).removesuffix(".")
    labels = name.split(".")
    if len(labels) < 2 or labels[-1] != "no":
        raise ValueError("invalid_domain")
    canonical = []
    for index, label in enumerate(labels):
        if not label or len(label) > 63:
            raise ValueError("invalid_domain")
        try:
            decoded = label.encode("ascii").decode("idna") if label.startswith("xn--") else label
            if index == len(labels) - 2 and len(decoded) < 2:
                raise ValueError("invalid_domain")
            if not re.fullmatch(f"[a-z0-9{IDN_LETTERS}-]+", decoded):
                raise ValueError("invalid_domain")
            ascii_label = decoded.encode("idna").decode("ascii")
        except UnicodeError:
            raise ValueError("invalid_domain") from None
        if ascii_label.startswith("-") or ascii_label.endswith("-"):
            raise ValueError("invalid_domain")
        canonical.append(ascii_label)
    result = ".".join(canonical)
    if len(result) > 253:
        raise ValueError("invalid_domain")
    return result


def org_number(value: str) -> str:
    if not re.fullmatch(r"[0-9]{9}", value) or value == "000000000":
        raise ValueError("invalid_organisation_number")
    weighted = sum(int(digit) * weight for digit, weight in zip(value[:8], (3, 2, 7, 6, 5, 4, 3, 2)))
    if (11 - weighted % 11) % 11 != int(value[-1]):
        raise ValueError("invalid_organisation_number")
    return value


def municipality_code(value: str) -> str:
    if not re.fullmatch(r"[0-9]{4}", value) or value == "0000":
        raise ValueError("invalid_municipality_code")
    return value


def matched(row: JSON, key: str, identifier: str) -> None:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError("missing_identifier")
    if value != identifier:
        raise IdentityConflict("source_identifier_mismatch")


def brreg(body: JSON, identifier: str) -> list[JSON]:
    matched(body, "organisasjonsnummer", identifier)
    form = body.get("organisasjonsform")
    code = form.get("kode") if isinstance(form, dict) else None
    if not isinstance(code, str) or code not in FORMS:
        raise RestrictedRecord("organisation_form_out_of_scope")
    return [{
        "name": clean_text(body.get("navn")),
        "organisation_form": code,
        "bankrupt": body["konkurs"] if type(body.get("konkurs")) is bool else None,
    }]


def kartverket(body: JSON, identifier: str) -> list[JSON]:
    matched(body, "kommunenummer", identifier)
    county = clean_text(body.get("fylkesnummer"))
    return [{
        "name": clean_text(body.get("kommunenavn")),
        "norwegian_name": clean_text(body.get("kommunenavnNorsk")),
        "county_code": county if county and re.fullmatch(r"[0-9]{2}", county) else None,
    }]


def norid(body: JSON, identifier: str) -> list[JSON]:
    if body.get("objectClassName") != "domain":
        raise ValueError("unexpected_rdap_object")
    name = clean_text(body.get("ldhName"))
    if name is None:
        raise ValueError("missing_identifier")
    if domain_name(name) != identifier:
        raise IdentityConflict("source_identifier_mismatch")
    statuses = body.get("status")
    allowed = {"active", "inactive", "pending create", "pending delete", "pending renewal",
               "pending transfer", "pending update", "locked", "validated", "renew prohibited",
               "transfer prohibited", "update prohibited", "delete prohibited"}
    return [{"name": identifier, "registration_status": sorted({
        item for item in statuses if isinstance(item, str) and item in allowed
    }) if isinstance(statuses, list) else None}]


def ssb(body: JSON, identifier: str) -> list[JSON]:
    rows = body.get("codes")
    if not isinstance(rows, list) or len(rows) > 20 or any(not isinstance(row, dict) for row in rows):
        raise ValueError("invalid_codes_collection")
    records = []
    for row in rows:
        matched(row, "code", identifier)
        records.append({"name": clean_text(row.get("name"))})
    return records


@dataclass(frozen=True)
class Adapter:
    publisher: str
    documentation: str
    endpoint: str
    entity_type: str
    identifier: Callable[[str], str]
    parse: Callable[[JSON, str], list[JSON]]
    accept: str = "application/json"

    def url(self, identifier: str, effective_date: str | None) -> str:
        if effective_date is not None:
            return self.endpoint + "?" + urlencode({"date": effective_date, "selectCodes": identifier})
        return self.endpoint.format(identifier=identifier)


ADAPTERS = {
    "brreg": Adapter(
        "Brønnøysundregistrene",
        "https://data.brreg.no/enhetsregisteret/api/dokumentasjon/no/",
        "https://data.brreg.no/enhetsregisteret/api/enheter/{identifier}", "no_organisation",
        org_number, brreg, "application/vnd.brreg.enhetsregisteret.enhet.v2+json",
    ),
    "kartverket": Adapter(
        "Kartverket", "https://ws.geonorge.no/kommuneinfo/v1/static/openapi_doc.json",
        "https://api.kartverket.no/kommuneinfo/v1/kommuner/{identifier}?filtrer=kommunenummer,kommunenavn,kommunenavnNorsk,fylkesnummer", "no_municipality",
        municipality_code, kartverket,
    ),
    "norid": Adapter(
        "Norid", "https://teknisk.norid.no/en/integrere-mot-norid/rdap-tjenesten/",
        "https://rdap.norid.no/domain/{identifier}", "no_domain",
        domain_name, norid, "application/rdap+json",
    ),
    "ssb": Adapter(
        "Statistisk sentralbyrå", "https://data.ssb.no/api/klass/v1/api-guide.html",
        "https://data.ssb.no/api/klass/v1/classifications/131/codesAt", "no_municipality",
        municipality_code, ssb,
    ),
}


def effective_date(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("invalid_effective_date")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValueError("invalid_effective_date") from None
