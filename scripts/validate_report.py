"""Pre-publish gate for Snowflake HTML Report artifacts.

Fails on constructs the report sandbox blocks (so the report would render broken) and on
patterns that suggest sensitive data is about to be embedded in a snapshot that bypasses RBAC.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # local budget; the account's artifact limit may differ

RULES: list[tuple[str, str, re.Pattern[str]]] = [
    ("error", "inline-event-handler", re.compile(r"<[^>]+\son[a-z]+\s*=", re.I)),
    ("error", "external-script", re.compile(r"<script[^>]+src\s*=\s*[\"'](?!/libs/)", re.I)),
    ("error", "external-stylesheet",
     re.compile(r"<link[^>]+href\s*=\s*[\"'](?:https?:)?//", re.I)),
    ("error", "remote-image", re.compile(r"<img[^>]+src\s*=\s*[\"'](?:https?:)?//", re.I)),
    ("error", "network-call",
     re.compile(r"\b(fetch\s*\(|XMLHttpRequest|new\s+WebSocket|sendBeacon)", re.I)),
    ("error", "dynamic-code", re.compile(r"\beval\s*\(|new\s+Function\s*\(")),
    ("error", "browser-storage", re.compile(r"\b(localStorage|sessionStorage|document\.cookie)")),
    ("error", "blocked-element", re.compile(r"<(iframe|object|embed|base)\b", re.I)),
    ("error", "javascript-href", re.compile(r"href\s*=\s*[\"']\s*javascript:", re.I)),
    ("warn", "sensitive-column",
     re.compile(r"\b(email|ssn|social_security|phone|dob|date_of_birth|salary|password|"
                r"credit_card|card_number|iban)\b", re.I)),
    ("warn", "unaggregated-select", re.compile(r"select\s+\*", re.I)),
]

META_RE = re.compile(
    r'<script[^>]+type="application/json"[^>]+id="snowflake-report-metadata"[^>]*>(.*?)</script>',
    re.S | re.I,
)


@dataclass
class Finding:
    level: str
    rule: str
    line: int
    excerpt: str

    def __str__(self) -> str:
        return f"{self.level.upper():5} {self.rule:22} line {self.line}: {self.excerpt}"


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def validate(html: str, max_bytes: int = DEFAULT_MAX_BYTES) -> list[Finding]:
    findings: list[Finding] = []
    for level, rule, pattern in RULES:
        for m in pattern.finditer(html):
            excerpt = html[m.start(): m.start() + 60].replace("\n", " ")
            findings.append(Finding(level, rule, _line_of(html, m.start()), excerpt))

    size = len(html.encode("utf-8"))
    if size > max_bytes:
        findings.append(Finding("error", "file-size", 1, f"{size} bytes > {max_bytes}"))

    if 'name="viewport"' not in html:
        findings.append(Finding("warn", "missing-viewport", 1, "add a viewport meta tag"))

    meta = META_RE.search(html)
    if not meta:
        findings.append(Finding("error", "missing-metadata", 1,
                                "no snowflake-report-metadata block; report can't be refreshed"))
    else:
        try:
            data = json.loads(meta.group(1))
        except json.JSONDecodeError as exc:
            findings.append(Finding("error", "invalid-metadata", _line_of(html, meta.start()),
                                    str(exc)))
        else:
            for sec in data.get("sections", []):
                sid = sec.get("id")
                if sid and f'id="{sid}"' not in html:
                    findings.append(Finding("error", "orphan-section", 1,
                                            f"metadata section '{sid}' has no anchor"))
            if re.search(r"\{[A-Z_]+\}", meta.group(1)):
                findings.append(Finding("error", "placeholder-left", 1,
                                        "unreplaced {TOKEN} in metadata"))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args(argv)

    failed = False
    for path in args.files:
        findings = validate(path.read_text(encoding="utf-8"), args.max_bytes)
        print(f"== {path}: {len(findings)} finding(s)")
        for f in findings:
            print("  ", f)
        if any(f.level == "error" or (args.strict and f.level == "warn") for f in findings):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
