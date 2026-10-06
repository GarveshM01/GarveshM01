#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://github.com/users/GarveshM01/contributions"


def parse_count(node, tooltip_text: str = "") -> int:
    for attr in ("data-count", "data-contribution-count"):
        raw = node.get(attr)
        if raw is not None:
            try:
                return int(raw)
            except ValueError:
                pass

    text_fields = [
        tooltip_text,
        node.get("aria-label", ""),
        node.get("data-original-title", ""),
        node.get("title", ""),
        node.get_text(" ", strip=True),
    ]
    for text in text_fields:
        match = re.search(r"(\d+)\s+contributions?", text)
        if match:
            return int(match.group(1))
        if "no contributions" in text.lower():
            return 0
    return 0


def compute_stats(days: list[dict[str, int | str]]) -> dict:
    if not days:
        return {
            "total_last_year": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": {"date": None, "count": 0},
            "monthly_totals": {},
        }

    ordered = sorted(days, key=lambda d: d["date"])
    total = sum(int(d["count"]) for d in ordered)
    monthly = defaultdict(int)
    for d in ordered:
        monthly[d["date"][:7]] += int(d["count"])

    longest = 0
    current = 0
    streak = 0
    for d in ordered:
        if int(d["count"]) > 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0
    if int(ordered[-1]["count"]) > 0:
        for d in reversed(ordered):
            if int(d["count"]) > 0:
                current += 1
            else:
                break

    best = max(ordered, key=lambda d: (int(d["count"]), d["date"]))
    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": int(best["count"])},
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> None:
    headers = {"User-Agent": "GarveshM01-profile-art/1.0"}
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    tooltip_map = {
        tip.get("for"): tip.get_text(" ", strip=True)
        for tip in soup.select("tool-tip[for]")
        if tip.get("for")
    }
    day_nodes = soup.select("[data-date][data-level]")
    days = []
    for node in day_nodes:
        day_date = node.get("data-date")
        level_raw = node.get("data-level", "0")
        if not day_date:
            continue
        try:
            datetime.strptime(day_date, "%Y-%m-%d")
            level = int(level_raw)
        except ValueError:
            continue
        days.append(
            {
                "date": day_date,
                "count": parse_count(node, tooltip_map.get(node.get("id", ""), "")),
                "level": level,
            }
        )

    if not days:
        today = date.today()
        start = today - timedelta(days=370)
        days = [{"date": (start + timedelta(days=i)).isoformat(), "count": 0, "level": 0} for i in range(371)]

    payload = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "days": sorted(days, key=lambda d: d["date"]),
        "stats": compute_stats(days),
    }

    out_path = Path("data/contributions.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
