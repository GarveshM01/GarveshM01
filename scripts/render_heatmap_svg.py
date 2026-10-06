#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def format_int(value: int) -> str:
    return f"{value:,}"


def load_data(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render(data: dict, output_path: Path) -> None:
    days = data.get("days", [])
    stats = data.get("stats", {})
    day_map = {d["date"]: d for d in days}

    if days:
        end_date = datetime.strptime(max(day_map.keys()), "%Y-%m-%d").date()
    else:
        end_date = date.today()
    start_date = end_date - timedelta(days=370)

    cell = 12
    gap = 3
    pitch = cell + gap
    left = 70
    top = 38
    width = 860
    height = 220
    grid_w = 53 * pitch

    month_labels = {}
    for i in range(371):
        d = start_date + timedelta(days=i)
        if d.day == 1 or (d.month == start_date.month and i == 0):
            week = i // 7
            month_labels.setdefault(week, d.strftime("%b"))

    rects = []
    for i in range(371):
        d = start_date + timedelta(days=i)
        week = i // 7
        dow = (d.weekday() + 1) % 7
        x = left + week * pitch
        y = top + dow * pitch
        item = day_map.get(d.isoformat(), {"level": 0, "count": 0})
        level = max(0, min(5, int(item.get("level", 0))))
        count = int(item.get("count", 0))
        fill = PALETTE[level]
        delay = ((week + dow) * 0.012) + 0.02
        rects.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" ry="3" fill="{fill}" data-date="{d.isoformat()}" data-count="{count}" style="animation-delay:{delay:.3f}s" />'
        )

    total = int(stats.get("total_last_year", sum(int(d.get("count", 0)) for d in days)))
    current = int(stats.get("current_streak", 0))
    longest = int(stats.get("longest_streak", 0))
    best = stats.get("best_day", {"date": "-", "count": 0})
    best_date = best.get("date") or "-"
    best_count = int(best.get("count", 0))

    month_text = [
        f'<text x="{left + week * pitch}" y="24" fill="#8b949e" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">{name}</text>'
        for week, name in sorted(month_labels.items())
    ]

    weekdays = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    weekday_text = [
        f'<text x="22" y="{top + d * pitch + 10}" fill="#8b949e" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">{label}</text>'
        for label, d in weekdays
    ]

    legend_x = left + grid_w - 128
    legend = [
        f'<text x="{legend_x - 40}" y="164" fill="#8b949e" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">Less</text>'
    ]
    for i, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + i * 16}" y="154" width="12" height="12" rx="3" ry="3" fill="{color}" stroke="#30363d" />'
        )
    legend.append(
        f'<text x="{legend_x + len(PALETTE) * 16 + 8}" y="164" fill="#8b949e" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">More</text>'
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Contribution heatmap for GarveshM01">
<style>
@keyframes dropIn {{
  from {{ transform: translateY(-8px); opacity: 0; }}
  to {{ transform: translateY(0); opacity: 1; }}
}}
.cell {{
  opacity: 0;
  animation: dropIn 320ms ease forwards;
}}
</style>
<rect width="100%" height="100%" fill="#0d1117" rx="12" ry="12"/>
<rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="10" ry="10" fill="#161b22" stroke="#30363d"/>
{''.join(month_text)}
{''.join(weekday_text)}
{''.join(rects)}
{''.join(legend)}
<text x="22" y="198" fill="#c9d1d9" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">{format_int(total)} contributions in the last year</text>
<text x="460" y="198" fill="#8b949e" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">Current streak: {current}  |  Longest streak: {longest}  |  Best day: {best_date} ({best_count})</text>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")


def main() -> None:
    data_path = Path("data/contributions.json")
    data = load_data(data_path)
    output_path = Path("contrib-heatmap.svg")
    render(data, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
