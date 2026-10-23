"""
Build the production image set for the dashboards and public pages.

Why this exists
---------------
Every photograph in this product was being served as its original file,
stretched across the whole viewport with ``background-size: cover``. Three
things were wrong with that at once, and all three read to the eye as "blurry":

1. **Upscaling.** ``farmer-dashboard-bg.png`` is 1365x768. On a 2560px-wide
   laptop it was being blown up 1.88x, and on a 3440px ultrawide 2.5x. There is
   no detail to recover in those extra pixels -- upscaling *is* blur.

2. **Wrong container.** Four of the backgrounds were PNGs, one of them 2.7MB.
   PNG is lossless and therefore excellent for the logo and useless for a
   photograph: it costs ten times the bytes of a WebP at the same resolution,
   so the pragmatic fix had always been to use a *smaller* source, which is
   exactly what made them soft.

3. **Filters over the top.** The ministry shell carried
   ``filter: brightness(1.25)`` on its background. Brightening a photograph in
   the compositor clips the highlights -- the detail in them is discarded, and
   a highlight with no detail reads as out of focus. The farmer shell's own
   comment said "keeps background sharp and visible (no blur)", which was true
   of that shell and not of the other two.

What it produces
----------------
For each role, a hero image at 1x and 2x, in WebP with a JPEG fallback,
cropped to a 2:1 banner and sharpened after the downscale.

The one rule that governs the whole script: **never upscale**. If a source
cannot reach the 2x width, the 2x variant is simply not emitted and the 1x file
serves every density. A sharp 1536px image shown at 1.5x beats a 2880px
upscale of it every time, and silently inventing pixels is the thing this
script exists to stop.

A note on naming: the files are ``<slug>-1x`` / ``<slug>-2x``, not ``@1x``.
Django's ``{% static %}`` percent-encodes an ``@`` to ``%40``, which does
resolve, but it travels badly -- some CDNs and storage backends normalise it
differently from the filesystem, and a hero that 404s only in production is not
worth the convention.

Run:  python scripts/build_images.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "static" / "images"
OUT = ROOT / "static" / "images" / "generated"

# The hero panel is capped at 1440 CSS px by .main-area, so 1440 is a true 1x
# and 2880 a true 2x. Nothing wider is worth the bytes: beyond the cap the
# panel stops growing.
WIDTH_1X = 1440
WIDTH_2X = 2880

# A 2:1 crop. The panel itself is far wider than it is tall, and
# background-size: cover scales to fill width, so width is what sets the
# effective resolution -- the extra height is headroom for a taller panel on a
# narrow screen rather than wasted pixels.
ASPECT = 2.0

WEBP_QUALITY = 82
JPEG_QUALITY = 86


@dataclass(frozen=True)
class Hero:
    """One hero image: which source, which role, and where in frame to crop."""

    slug: str
    source: str
    #: 0.0 = crop from the top edge, 0.5 = centre, 1.0 = bottom. Set per image
    #: so the crop keeps the subject rather than the sky.
    focus_y: float
    note: str


HEROES = [
    Hero(
        slug="hero-farmer",
        source="pexels-sippakorn-yamkasikorn-1745809-3421999 - Copy.jpg",
        focus_y=0.52,
        # 5184x3456. A farmer walking his cattle -- the right subject for the
        # screen a farmer opens, and large enough for a genuine 2x.
        note="farmer + herd on the road, 5184px source",
    ),
    Hero(
        slug="hero-vet",
        source="vet doc.png",
        focus_y=0.45,
        # 1536x1024, and the only vet-subject image in the project. It reaches
        # 1x comfortably and cannot reach 2x, so no 2x file is written for it.
        # Substituting a landscape that *could* reach 2x would mean the vet's
        # dashboard no longer shows a vet, which is the worse trade.
        note="vet examining a cow, 1536px source -- 1x only, see module docstring",
    ),
    Hero(
        slug="hero-ministry",
        source="sylvester-sabo-vVdpZEspAGs-unsplash.jpg",
        focus_y=0.58,
        # 5374x3023. A wide landscape with multiple herds, which is the right
        # register for a national oversight screen, and a true 2x source.
        note="herds at dusk, 5374px source",
    ),
    # No hero-landing entry. One was built for the public home page and then
    # never wired into it -- the landing page has its own hero treatment that
    # this port did not change. Generating an image nothing references just
    # puts bytes in the repository, so the entry is removed rather than left
    # here "for later". Add it back alongside the markup that uses it.
]


def crop_to_aspect(im: Image.Image, aspect: float, focus_y: float) -> Image.Image:
    """Centre-crop horizontally, focus-crop vertically, to the target aspect."""
    w, h = im.size
    target_h = int(round(w / aspect))

    if target_h <= h:
        # Source is taller than the target band: take a horizontal slice,
        # positioned by focus_y.
        top = int(round((h - target_h) * focus_y))
        return im.crop((0, top, w, top + target_h))

    # Source is wider than the target band: take a vertical slice, centred.
    target_w = int(round(h * aspect))
    left = (w - target_w) // 2
    return im.crop((left, 0, left + target_w, h))


def resize_sharp(im: Image.Image, width: int) -> Image.Image:
    """
    Downscale with Lanczos, then restore the edge contrast the downscale cost.

    Any resampling filter good enough not to alias is also slightly soft --
    that is the trade it makes. A light unsharp mask afterwards is the standard
    correction, and the values here are deliberately gentle: radius 1.0 at 55%
    sharpens the edges without the white halo that gives an over-processed
    image away.
    """
    height = int(round(im.height * width / im.width))
    out = im.resize((width, height), Image.LANCZOS)
    return out.filter(ImageFilter.UnsharpMask(radius=1.0, percent=55, threshold=3))


def write_pair(im: Image.Image, stem: Path, with_jpeg: bool) -> list[str]:
    """
    Write one image as WebP, and at 1x also as a JPEG fallback.

    Why the JPEG is 1x only
    -----------------------
    The CSS declares the hero twice: a plain ``url(...jpg)`` that every browser
    understands, then an ``image-set`` of WebP at 1x and 2x that overrides it.
    A browser therefore takes exactly one of two paths -- it either parses
    image-set, in which case it gets WebP, or it does not, in which case it
    gets the 1x JPEG. Nothing reaches a 2x JPEG.

    The first version of this script wrote one anyway, which put 1.67MB of
    files into a public repository that no browser would ever request.
    """
    written = []

    webp = stem.with_suffix(".webp")
    im.save(webp, "WEBP", quality=WEBP_QUALITY, method=6)
    written.append(f"{webp.name} ({webp.stat().st_size // 1024} KB)")

    if with_jpeg:
        jpg = stem.with_suffix(".jpg")
        im.save(
            jpg,
            "JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
            # 4:4:4. At a hero's size the bytes saved by chroma subsampling are
            # not worth the colour bleed it puts on a hard edge -- and a sunset
            # sky against a dark treeline is exactly that edge.
            subsampling=0,
        )
        written.append(f"{jpg.name} ({jpg.stat().st_size // 1024} KB)")

    return written


def build() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    problems = 0

    for hero in HEROES:
        path = SRC / hero.source
        if not path.exists():
            print(f"  MISSING  {hero.source}")
            problems += 1
            continue

        with Image.open(path) as raw:
            im = raw.convert("RGB")
            native_w = im.width
            banner = crop_to_aspect(im, ASPECT, hero.focus_y)

            print(f"\n{hero.slug}  <-  {hero.source}")
            print(f"  source {native_w}x{raw.height}  |  {hero.note}")

            for label, width in (("1x", WIDTH_1X), ("2x", WIDTH_2X)):
                if width > banner.width:
                    # The rule. No upscaling, ever.
                    print(
                        f"  {label} skipped: source is {banner.width}px after crop, "
                        f"{width}px would be an upscale"
                    )
                    continue
                stem = OUT / f"{hero.slug}-{label}"
                for line in write_pair(
                    resize_sharp(banner, width), stem, with_jpeg=(label == "1x")
                ):
                    print(f"  {label}  {line}")

    print(f"\nOutput: {OUT.relative_to(ROOT)}")
    return problems


if __name__ == "__main__":
    sys.exit(build())
