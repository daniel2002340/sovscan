# sovereigntyscanner

Looks up the DNS records of a domain and shows which network (ASN) hosts its IP addresses,
and under which jurisdiction that network falls.

ASN data comes from [RIPEstat](https://stat.ripe.net). Jurisdiction and laws come from
`registry.json`, a small hand-maintained list of known ASNs.

## Install

```sh
uv sync
```

## Usage

```sh
uv run sovscan nlnet.nl
```

Output (shortened):

```json
{
  "domain": "nlnet.nl",
  "records": {
    "A": [
      {
        "value": "5.255.103.93",
        "prefix": "5.255.103.0/24",
        "asns": [
          {
            "asn": 60404,
            "holder": "Liteserver The Infrastructure Group B.V.",
            "registry": {
              "organization": "The Infrastructure Group B.V.",
              "country": "NL",
              "jurisdiction": "NL",
              "laws": ["GDPR", "Wiv 2017"],
              "eu_based": true
            }
          }
        ]
      }
    ],
    "NS": [{ "value": "ns1.sidn.nl." }],
    "MX": [{ "value": "20 open.nlnet.nl." }]
  },
  "errors": {}
}
```

`registry` is `null` when an ASN is not in `registry.json` yet.