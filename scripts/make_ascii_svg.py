#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image

RAMP = " .`:-=+*cs#%@"


def to_ascii_rows(image_path: Path, cols: int = 100, rows: int = 53) -> list[str]:
    image = Image.open(image_path).convert("L")
    resized = image.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = list(resized.tobytes())
    out = []
    for y in range(rows):
        row = pixels[y * cols : (y + 1) * cols]
        chars = []
        for v in row:
            idx = int(round((v / 255.0) * (len(RAMP) - 1)))
            chars.append(RAMP[idx])
        out.append("".join(chars))
    return out


def render_svg(rows: list[str], output: Path) -> None:
    cols = len(rows[0])
    row_count = len(rows)
    svg_w = 370
    top = 14
    left = 10
    char_w = 3.5
    line_h = 7
    content_w = cols * char_w
    svg_h = top + row_count * line_h + 8

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" role="img" aria-label="ASCII portrait of garve">',
        '<rect width="100%" height="100%" fill="#0d1117"/>',
        '<g fill="#c9d1d9" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace" font-size="6">',
        "<defs>",
    ]

    for i in range(row_count):
        y = top + i * line_h
        delay = i * 0.045
        lines.extend(
            [
                f'<clipPath id="clip-{i}" clipPathUnits="userSpaceOnUse">',
                f'<rect id="wipe-{i}" x="{left}" y="{y - line_h + 1}" width="0" height="{line_h}">',
                f'<animate attributeName="width" from="0" to="{content_w}" begin="{delay:.3f}s" dur="0.62s" fill="freeze" />',
                "</rect>",
                "</clipPath>",
            ]
        )

    lines.append("</defs>")

    for i, row in enumerate(rows):
        y = top + i * line_h
        delay = i * 0.045
        escaped = html.escape(row)
        lines.extend(
            [
                f'<g clip-path="url(#clip-{i})">',
                f'<text x="{left}" y="{y}" xml:space="preserve">{escaped}</text>',
                "</g>",
                f'<rect x="{left}" y="{y - line_h + 1}" width="2" height="{line_h}" fill="#c9d1d9" opacity="1">',
                f'<animate attributeName="x" from="{left}" to="{left + content_w}" begin="{delay:.3f}s" dur="0.62s" fill="freeze" />',
                f'<animate attributeName="opacity" from="1" to="0" begin="{delay + 0.62:.3f}s" dur="0.001s" fill="freeze" />',
                "</rect>",
            ]
        )

    lines.extend(["</g>", "</svg>"])
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate animated ASCII SVG portrait")
    parser.add_argument("--input", default="source-prepped.png", help="Input grayscale photo")
    parser.add_argument("--output", default="ascii.svg", help="Output SVG path")
    args = parser.parse_args()

    rows = to_ascii_rows(Path(args.input))
    render_svg(rows, Path(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
