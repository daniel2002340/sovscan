import ipaddress
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from functools import cache

RIPESTAT_URL = "https://stat.ripe.net/data/{endpoint}/data.json"
SOURCE_APP = "sovereigntyscanner"
TIMEOUT = 10


@dataclass
class AsnInfo:
    asn: int
    holder: str


@dataclass
class IpAsn:
    ip: str
    prefix: str | None
    asns: list[AsnInfo]


def _ripestat(endpoint: str, resource: str) -> dict:
    query = urllib.parse.urlencode({"resource": resource, "sourceapp": SOURCE_APP})
    url = RIPESTAT_URL.format(endpoint=endpoint) + "?" + query
    with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
        return json.load(response)["data"]


@cache
def asn_holder(asn: int) -> str:
    return _ripestat("as-overview", f"AS{asn}").get("holder") or ""


def ip_to_asn(ip: str) -> IpAsn:
    ip = str(ipaddress.ip_address(ip))
    data = _ripestat("network-info", ip)
    asns = [AsnInfo(int(asn), asn_holder(int(asn))) for asn in data.get("asns", [])]
    return IpAsn(ip=ip, prefix=data.get("prefix") or None, asns=asns)

