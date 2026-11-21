#!/usr/bin/env python3
"""Convert v2fly/domain-list-community plaintext exports to Surge/Mihomo/QX compatible RULE-SET files."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTS_FILE = ROOT / "lists.txt"
EXPORT_DIR = ROOT / "exported"
RULES_DIR = ROOT / "rules"

TYPE_MAP = {
    "domain": "DOMAIN-SUFFIX",
    "full": "DOMAIN",
    "keyword": "DOMAIN-KEYWORD",
}

ORDER = {"DOMAIN-SUFFIX": 0, "DOMAIN": 1, "DOMAIN-KEYWORD": 2}


def read_lists() -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw in LISTS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if "=>" in line:
            src_name, out_stem = [p.strip() for p in line.split("=>", 1)]
        else:
            src_name = line
            out_stem = line
        items.append((src_name, out_stem))
    return items


def convert_one(src_name: str, out_stem: str) -> tuple[int, int]:
    src = EXPORT_DIR / f"{src_name.lower()}.txt"
    if not src.exists():
        raise FileNotFoundError(f"Missing exported plaintext file: {src}")

    rules: set[tuple[str, str]] = set()
    skipped_regexp = 0

    for raw in src.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        first_colon = line.find(":")
        if first_colon == -1:
            raise ValueError(f"Unexpected line in {src}: {line!r}")
        rtype = line[:first_colon].strip().lower()
        rest = line[first_colon + 1 :]
        if ":@" in rest:
            value = rest.split(":@", 1)[0].strip()
        else:
            value = rest.strip()

        if rtype == "regexp":
            skipped_regexp += 1
            continue
        if rtype not in TYPE_MAP:
            raise ValueError(f"Unsupported rule type {rtype!r} in {src}: {line!r}")
        if not value:
            continue
        rules.add((TYPE_MAP[rtype], value.lower()))

    sorted_rules = sorted(rules, key=lambda item: (ORDER[item[0]], item[1]))
    if not sorted_rules:
        raise RuntimeError(f"Converted list {src_name!r} is empty; refusing to write.")

    header = [
        f"# NAME: {out_stem} (upstream: {src_name})",
        "# SOURCE: https://github.com/v2fly/domain-list-community",
        f"# TOTAL: {len(sorted_rules)} (skipped regexp: {skipped_regexp})",
        "# COMPAT: Surge RULE-SET / Clash Mihomo classical text / Quantumult X opt-parser",
    ]
    out_path = RULES_DIR / f"{out_stem}.list"
    out_path.write_text(
        "\n".join(header + [f"{t},{v}" for t, v in sorted_rules]) + "\n",
        encoding="utf-8",
    )
    return len(sorted_rules), skipped_regexp


def main() -> int:
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    items = read_lists()
    if not items:
        print("lists.txt is empty", file=sys.stderr)
        return 1
    expected_files = {f"{out_stem}.list" for _, out_stem in items}
    for old in RULES_DIR.glob("*.list"):
        if old.name not in expected_files:
            old.unlink()
    for src_name, out_stem in items:
        total, skipped = convert_one(src_name, out_stem)
        print(f"Generated rules/{out_stem}.list (from {src_name}): {total} rules (skipped regexp: {skipped})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
