import dataclasses
import json
import sys
import urllib.error
from pathlib import Path

import dns.resolver

from ip_to_asn import ip_to_asn

RECORD_TYPES = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]
REGISTRY_PATH = Path(__file__).parent / "registry.json"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: sovscan <domain>", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1]
    resolver = dns.resolver.Resolver()
    registry = load_registry()
    records: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}

    for record_type in RECORD_TYPES:
        try:
            answer = resolver.resolve(domain, record_type)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
        except dns.resolver.LifetimeTimeout:
            errors[record_type] = "DNS lookup timed out"
            continue
        records[record_type] = [_record(record_type, record.to_text(), registry) for record in answer]

    result = {"domain": domain, "records": records, "errors": errors}
    print(json.dumps(result, indent=2, ensure_ascii=False))


def load_registry(path: Path = REGISTRY_PATH) -> dict[int, dict]:
    with path.open(encoding="utf-8") as file:
        entries = json.load(file)["asns"]
    return {entry["asn"]: {k: v for k, v in entry.items() if k != "asn"} for entry in entries}


def _record(record_type: str, value: str, registry: dict[int, dict]) -> dict:
    record: dict = {"value": value}
    if record_type in ("A", "AAAA"):
        try:
            asn = ip_to_asn(value)
        except (urllib.error.URLError, TimeoutError) as error:
            record["asn_error"] = f"ASN lookup failed: {error}"
        else:
            record["prefix"] = asn.prefix
            record["asns"] = [
                {**dataclasses.asdict(info), "registry": registry.get(info.asn)} for info in asn.asns
            ]
    return record


if __name__ == "__main__":
    main()
