# geosite-surge-rules

Automated daily mirror converting selected categories from [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) into standard Surge `RULE-SET` files (`DOMAIN-SUFFIX` / `DOMAIN` / `DOMAIN-KEYWORD`), compatible with Surge, Clash Mihomo (`behavior: classical`, `format: text`), and Quantumult X (`opt-parser=true`).

## Generated Rules

- `rules/category-ai-!cn.list`
- `rules/category-scholar-!cn.list`

## Upstream & Schedule

- Upstream parser: official `v2fly/domain-list-community` `--exportlists`
- Schedule: daily at 22:30 UTC (06:30 CST) via GitHub Actions, plus manual dispatch
- `regexp:` entries are omitted to maintain strict cross-client compatibility across Surge, Quantumult X, and Clash Mihomo.
