#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8"]
# ///
"""Render the dependency-events quadrant chart as a PNG.

Generates the figure used in section 1 of the
`dependency-cooldown-considered-harmful` blog post. Static PNG instead of
Mermaid because Mermaid's quadrantChart cannot place labels without
overlap for this many points.

Writes to content/imgs/dependency_events_quadrant.png and a light-theme
version at content/imgs/dependency_events_quadrant_light.png.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

# NB: emoji in labels intentionally omitted — matplotlib's default font
# stack on macOS can't load Apple Color Emoji (color TTC format), and
# shipping Noto Emoji/Symbola just for one chart isn't worth it. Labels
# use short text tags instead.

OUTPUT_LIGHT = Path("content/imgs/dependency_events_quadrant.png")

# (label, x = detection delay normalized 0..1, y = blast radius normalized 0..1)
POINTS: list[tuple[str, float, float]] = [
    ("Typosquat", 0.05, 0.22),
    ("Account compromise", 0.22, 0.55),
    ("Bug / regression", 0.45, 0.30),
    ("Breaking change", 0.40, 0.15),
    ("Post-disclosure CVE fix", 0.04, 0.78),
    ("Pre-disclosure CVE latency", 0.95, 0.78),
    ("Long-dwell backdoor (xz)", 0.92, 0.96),
]

# Label offset per point to avoid overlaps (dx, dy in data coords)
LABEL_OFFSETS: dict[str, tuple[float, float]] = {
    "Typosquat": (0.02, -0.05),
    "Account compromise": (0.02, 0.03),
    "Bug / regression": (0.02, -0.05),
    "Breaking change": (0.02, 0.03),
    "Post-disclosure CVE fix": (0.02, 0.03),
    "Pre-disclosure CVE latency": (-0.02, -0.05),
    "Long-dwell backdoor (xz)": (-0.02, -0.05),
}

QUADRANT_LABELS: list[tuple[float, float, str, str]] = [
    (0.25, 0.97, "Cooldown useful\n(fast + costly)",     "top"),
    (0.75, 0.97, "Cooldown useless\n(slow + costly)",    "top"),
    (0.25, 0.03, "Cooldown overkill\n(fast + cheap)",    "bottom"),
    (0.75, 0.03, "Cooldown helpless\n(slow + cheap)",    "bottom"),
]


def _render(outfile: Path, dark: bool) -> None:
    bg = "#1a1a1a" if dark else "#ffffff"
    fg = "#e0e0e0" if dark else "#2a2a2a"
    muted = "#666666" if dark else "#888888"
    point_color = "#ff6b6b" if dark else "#c0392b"
    quadrant_bg_colors = (
        ["#2a1f1f", "#1f2a2a", "#1f1f2a", "#2a2a1f"] if dark
        else ["#fdecea", "#eaf4fd", "#ecebfa", "#fdfaea"]
    )

    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=160)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    # Quadrant backgrounds (subtle tint)
    ax.axvspan(0, 0.5, ymin=0.5, ymax=1.0, facecolor=quadrant_bg_colors[0], zorder=0)
    ax.axvspan(0.5, 1.0, ymin=0.5, ymax=1.0, facecolor=quadrant_bg_colors[1], zorder=0)
    ax.axvspan(0, 0.5, ymin=0.0, ymax=0.5, facecolor=quadrant_bg_colors[2], zorder=0)
    ax.axvspan(0.5, 1.0, ymin=0.0, ymax=0.5, facecolor=quadrant_bg_colors[3], zorder=0)

    # Quadrant separator lines
    ax.axhline(0.5, color=muted, linewidth=0.8, linestyle="--", zorder=1)
    ax.axvline(0.5, color=muted, linewidth=0.8, linestyle="--", zorder=1)

    # Quadrant labels
    for x, y, label, va in QUADRANT_LABELS:
        ax.text(
            x, y, label,
            ha="center", va=va,
            color=muted, fontsize=9, fontstyle="italic",
            zorder=2,
        )

    # Points
    for label, x, y in POINTS:
        ax.scatter(
            x, y,
            s=140, color=point_color, edgecolors=fg, linewidths=1.2,
            zorder=4,
        )
        dx, dy = LABEL_OFFSETS.get(label, (0.02, 0.02))
        ha = "left" if dx >= 0 else "right"
        ax.annotate(
            label,
            xy=(x, y),
            xytext=(x + dx, y + dy),
            color=fg, fontsize=10.5, fontweight="bold",
            ha=ha, va="center",
            zorder=5,
        )

    # Axes styling
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ("top", "right", "bottom", "left"):
        ax.spines[spine].set_color(muted)

    # Axis labels
    ax.set_xlabel(
        "Detection speed      Fast  ─────────────────────────────▶  Slow",
        color=fg, fontsize=10, labelpad=10,
    )
    ax.set_ylabel(
        "Blast radius      Small  ─────────────────────────▶  Large",
        color=fg, fontsize=10, labelpad=10,
    )

    ax.set_title(
        "Dependency events: detection speed vs blast radius",
        color=fg, fontsize=13, fontweight="bold", pad=14,
    )

    fig.tight_layout()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outfile, facecolor=bg, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {outfile}")


def main() -> None:
    _render(OUTPUT_LIGHT, dark=False)


if __name__ == "__main__":
    main()
