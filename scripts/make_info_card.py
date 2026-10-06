#!/usr/bin/env python3
from __future__ import annotations

import os
import textwrap
from pathlib import Path


def wrap_value(text: str, width: int = 47) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [text]


def build_lines() -> list[tuple[str, str]]:
    fields = [
        ("Now", "B.Tech CSE student | learning web dev | doing DSA alongside frontend | open to internships"),
        (
            "Edu",
            "3rd year B.Tech CSE at OIST Bhopal; doing Web Development and Java DSA courses at Coding Thinker, Bhopal; core subjects covered: OS, SE, DBMS, TOC, IWT",
        ),
        ("Stack", "HTML, CSS, JavaScript, Java, C++, SQL, Supabase"),
        ("Learning", "MERN (MongoDB, Express, React, Node.js), DSA in Java"),
        (
            "Highlights",
            '200+ problems solved on CodeChef; built "Ration Setu" for SIH and was selected to represent my college; participant at TIT Srijan; organized 3 college events (debate competition, coding competition, mock placement drive)',
        ),
    ]
    lines: list[tuple[str, str]] = []
    for key, value in fields:
        wrapped = wrap_value(value)
        lines.append((f"{key}:", wrapped[0]))
        for extra in wrapped[1:]:
            lines.append(("", extra))
    return lines


def render(static: bool, output_path: Path) -> None:
    width, height = 490, 393
    lines = build_lines()

    y0 = 88
    line_h = 18
    key_x = 26
    value_x = 116

    css = ""
    if not static:
        css = """
<style>
@keyframes lineIn {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}
.line {
  opacity: 0;
  animation: lineIn 420ms ease forwards;
}
</style>
"""

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="garve profile terminal card">',
        css.strip(),
        '<rect x="0" y="0" width="100%" height="100%" fill="#0d1117"/>',
        '<rect x="10" y="10" width="470" height="373" rx="12" fill="#161b22" stroke="#30363d"/>',
        '<rect x="10" y="10" width="470" height="36" rx="12" fill="#21262d"/>',
        '<rect x="10" y="34" width="470" height="2" fill="#161b22"/>',
        '<circle cx="28" cy="28" r="5" fill="#ff5f56"/>',
        '<circle cx="46" cy="28" r="5" fill="#ffbd2e"/>',
        '<circle cx="64" cy="28" r="5" fill="#27c93f"/>',
        '<text x="245" y="31" text-anchor="middle" fill="#8b949e" font-size="13" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">garve@github</text>',
        '<text x="26" y="64" fill="#58a6ff" font-size="13" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">$ neofetch --profile garve</text>',
    ]

    for i, (key, value) in enumerate(lines):
        y = y0 + i * line_h
        delay = i * 0.08
        group_open = "<g>"
        if not static:
            group_open = f'<g class="line" style="animation-delay:{delay:.2f}s">'
        parts.append(group_open)
        if key:
            parts.append(
                f'<text x="{key_x}" y="{y}" fill="#7ee787" font-size="13" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">{key}</text>'
            )
        parts.append(
            f'<text x="{value_x}" y="{y}" fill="#c9d1d9" font-size="13" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">{value}</text>'
        )
        parts.append("</g>")

    parts.append("</svg>")
    output_path.write_text("\n".join(p for p in parts if p), encoding="utf-8")


if __name__ == "__main__":
    static = os.getenv("STATIC") == "1"
    render(static=static, output_path=Path("info-card.svg"))
    print("Wrote info-card.svg")
