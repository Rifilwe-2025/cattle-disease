"""
Rewrite hardcoded colours in the dashboard templates as design tokens.

Why
---
The three dashboards carried 643 inline ``style="..."`` attributes between
them, and roughly 900 literal hex colours across the templates. An inline style
beats any stylesheet, so a design system that only shipped CSS files would have
been overridden at every one of those call sites -- the tokens would exist and
the screens would not use them.

This script does not remove the inline styles. It rewrites the *colours inside
them* to ``rgb(var(--color-...))``, so an inline style still wins the cascade
but now wins with the right value. Removing the attributes outright is the
better end state and a much larger change; this is the step that makes the
system real without rewriting 36 templates by hand.

What it is careful about
------------------------
Colour is load-bearing in this product -- red, amber and green are the severity
scale -- so the mapping is semantic, not nearest-neighbour. ``#22c55e`` becomes
``--color-success`` because every use of it meant "resolved or healthy", and
``#3b82f6`` becomes ``--color-accent`` because every use of it meant "this is a
control", not "this is good news".

Two guards:

* ``PROPERTY_SCOPED`` entries only fire inside the property they name, because
  the same hex meant different things as a background and as text. White text
  on a dark card has to become dark text; a white *background* has to stay
  white.
* The navy rail and the hero panel are excluded entirely. Both are deliberate
  fixed-colour brand surfaces -- they are the two places in this system allowed
  not to use tokens -- so their literal values are correct and must survive.

Run ``python scripts/tokenise_colours.py`` for a dry run, which changes
nothing and prints a per-file count. Add ``--write`` to apply.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

#: Files whose literal colours are intentional brand surfaces, or which this
#: port has already rewritten by hand. Left alone.
EXCLUDE = {
    "vets/vet_base.html",
    "farmers/farmer_base.html",
    "ministry/base_ministry.html",
    "base.html",
}

#: Colours that mean the same thing wherever they appear.
GLOBAL: dict[str, str] = {
    # --- the severity scale -------------------------------------------------
    # Every one of these meant "resolved / healthy / good".
    "#22c55e": "rgb(var(--color-success))",
    "#16a34a": "rgb(var(--color-success))",
    "#4ade80": "rgb(var(--color-success))",
    "#28a745": "rgb(var(--color-success))",
    "#20c997": "rgb(var(--color-success))",
    # "severe / awaiting / caution".
    "#facc15": "rgb(var(--color-warning))",
    "#eab308": "rgb(var(--color-warning))",
    "#f59e0b": "rgb(var(--color-warning))",
    "#ffc107": "rgb(var(--color-warning))",
    # "critical".
    "#dc3545": "rgb(var(--color-danger))",
    "#ef4444": "rgb(var(--color-danger))",
    "#f87171": "rgb(var(--color-danger))",
    "#e74c3c": "rgb(var(--color-danger))",
    # --- controls and links -------------------------------------------------
    # Blue never meant a status here; it meant "you can press this".
    "#3b82f6": "rgb(var(--color-accent))",
    "#2563eb": "rgb(var(--color-accent))",
    "#1d4ed8": "rgb(var(--color-accent-hover))",
    "#60a5fa": "rgb(var(--color-accent))",
    "#93c5fd": "rgb(var(--color-accent-text))",
    "#17a2b8": "rgb(var(--color-accent))",
    "#138496": "rgb(var(--color-accent-hover))",
    # The two legacy brand gradients -- a purple on the ministry shell and an
    # orange on the public pages. Both become the identity teal.
    "#667eea": "rgb(var(--color-brand))",
    "#764ba2": "rgb(var(--color-brand-ink))",
    "#8a2be2": "rgb(var(--color-brand))",
    # --- neutrals -----------------------------------------------------------
    "#6c757d": "rgb(var(--color-text-muted))",
    "#6b7280": "rgb(var(--color-text-muted))",
    "#9ca3af": "rgb(var(--color-text-subtle))",
    "#94a3b8": "rgb(var(--color-text-muted))",
    "#64748b": "rgb(var(--color-text-muted))",
    "#495057": "rgb(var(--color-text-muted))",
    "#666": "rgb(var(--color-text-muted))",
    "#999": "rgb(var(--color-text-subtle))",
    "#555": "rgb(var(--color-text-muted))",
    "#333": "rgb(var(--color-text))",
    "#1a1a1a": "rgb(var(--color-text))",
    "#1f2937": "rgb(var(--color-text))",
    # These four are *only* safe as a global once `color:` has already claimed
    # them above -- see PROPERTY_SCOPED. As a border they are a line; as text
    # they were light-on-dark and have to invert. The first run of this script
    # had them here alone, which turned 33 labels into near-invisible grey on
    # the new light surface.
    "#e5e7eb": "rgb(var(--color-border))",
    "#e0e0e0": "rgb(var(--color-border))",
    "#dee2e6": "rgb(var(--color-border))",
    "#f8f9fa": "rgb(var(--color-surface-sunken))",
}

#: Colours whose meaning depends on the property they sit in.
#:
#: The light greys and off-whites are the ones that matter. As a background
#: they are a surface; as text they were white-on-dark and have to invert, or
#: they vanish on the light surface this port moves to.
PROPERTY_SCOPED: dict[str, dict[str, str]] = {
    "color": {
        "#fff": "rgb(var(--color-text))",
        "#ffffff": "rgb(var(--color-text))",
        "#e2e8f0": "rgb(var(--color-text))",
        "#cbd5f5": "rgb(var(--color-text-muted))",
        "#cbd5e1": "rgb(var(--color-text-muted))",
        "#f5f7fa": "rgb(var(--color-text))",
        # The light greys. These claim `color:` before the global map can turn
        # them into a border token -- they were light text on a dark card, and
        # a border grey on the new light surface is close to invisible.
        "#e5e7eb": "rgb(var(--color-text))",
        "#e0e0e0": "rgb(var(--color-text))",
        "#dee2e6": "rgb(var(--color-text))",
        "#f8f9fa": "rgb(var(--color-text))",
    },
    "background": {
        "#fff": "rgb(var(--color-surface))",
        "#ffffff": "rgb(var(--color-surface))",
        "#e2e8f0": "rgb(var(--color-surface-sunken))",
        "#f5f7fa": "rgb(var(--color-surface-sunken))",
        "#f5f2ee": "rgb(var(--color-bg))",
    },
    "background-color": {
        "#fff": "rgb(var(--color-surface))",
        "#ffffff": "rgb(var(--color-surface))",
        "#e2e8f0": "rgb(var(--color-surface-sunken))",
        "#f5f7fa": "rgb(var(--color-surface-sunken))",
    },
    "border-color": {
        "#fff": "rgb(var(--color-border))",
        "#e2e8f0": "rgb(var(--color-border))",
    },
}


def build_global_pattern() -> re.Pattern[str]:
    # Longest first, so #ffffff is not half-matched by #fff. Followed by a
    # non-hex-digit so #22c55e does not match inside a longer token.
    keys = sorted(GLOBAL, key=len, reverse=True)
    return re.compile("(" + "|".join(re.escape(k) for k in keys) + r")(?![0-9a-fA-F])", re.I)


def build_scoped_patterns() -> list[tuple[re.Pattern[str], dict[str, str]]]:
    out = []
    for prop, mapping in PROPERTY_SCOPED.items():
        keys = sorted(mapping, key=len, reverse=True)
        # Match "property : value", keeping the property and the spacing so the
        # replacement only touches the colour.
        pattern = re.compile(
            r"(\b" + re.escape(prop) + r"\s*:\s*)("
            + "|".join(re.escape(k) for k in keys)
            + r")(?![0-9a-fA-F])",
            re.I,
        )
        out.append((pattern, {k.lower(): v for k, v in mapping.items()}))
    return out


def process(text: str) -> tuple[str, int]:
    count = 0

    scoped = build_scoped_patterns()
    for pattern, mapping in scoped:
        def repl_scoped(m: re.Match[str], _map=mapping) -> str:
            nonlocal count
            count += 1
            return m.group(1) + _map[m.group(2).lower()]

        text = pattern.sub(repl_scoped, text)

    global_pattern = build_global_pattern()
    lowered = {k.lower(): v for k, v in GLOBAL.items()}

    def repl_global(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return lowered[m.group(1).lower()]

    text = global_pattern.sub(repl_global, text)
    return text, count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="apply changes")
    args = parser.parse_args()

    total = 0
    touched = 0

    for path in sorted(TEMPLATES.rglob("*.html")):
        rel = path.relative_to(TEMPLATES).as_posix()
        if rel in EXCLUDE:
            print(f"  skip    {rel}  (brand surface, rewritten by hand)")
            continue

        original = path.read_text(encoding="utf-8")
        updated, count = process(original)
        if count == 0:
            continue

        total += count
        touched += 1
        print(f"  {count:>4}   {rel}")
        if args.write:
            path.write_text(updated, encoding="utf-8")

    verb = "rewrote" if args.write else "would rewrite"
    print(f"\n{verb} {total} colour values across {touched} templates")
    if not args.write:
        print("dry run -- pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
