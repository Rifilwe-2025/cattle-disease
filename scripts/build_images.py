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
    #: Width-to-height ratio of the crop. Defaults to the 2:1 banner the
    #: dashboard panels use. The landing hero is a full-viewport panel rather
    #: than a banner, so it overrides this.
    aspect: float = ASPECT
    #: The 1x and 2x widths to emit. The dashboard banners are capped by the
    #: 1440px content column; a full-bleed hero is not, and on a portrait
    #: phone at 2x it is the image's *height* that has to stretch furthest --
    #: which is why the landing hero asks for more pixels than a banner does.
    widths: tuple[int, int] = (WIDTH_1X, WIDTH_2X)


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
    Hero(
        slug="hero-landing",
        source="golden-hour-brahman-herd.png",
        focus_y=0.5,
        # 1672x941, and a far better fit than the dusk shot it replaces: mean
        # luminance 113.6 against 77.6, median 113 against 66. The old hero was
        # a dusk photograph, so no amount of overlay tuning made it read -- the
        # detail was not in the file.
        #
        # Native width is 1672, so 1x is emitted at 1600 (a slight downscale,
        # which the unsharp pass likes) and 2x is skipped rather than upscaled.
        aspect=16 / 9,
        widths=(1600, 2880),
        note="golden-hour Brahman herd, 1672px source -- 1x only",
    ),
]


# Full-page backgrounds, as distinct from the dashboard hero banners above.
#
# These are the images behind the login, registration, password-reset and
# public content pages, declared in CSS as `center/cover` over the whole
# viewport. Every one of them was still being served as its original file, and
# four of the six are PNGs - `ChatGPT Image Feb 10...png` is 1536x1024 and
# 2.7MB, because PNG stores a photograph losslessly and a photograph has no
# use for that. The same pixels as WebP are about a twentieth of the bytes,
# with nothing visible given up.
#
# 16:9 rather than the banners' 2:1, because these fill a browser window
# rather than a panel.
#
# None of them emit a 2x, deliberately. Unlike a dashboard hero, a page
# background sits under a 35-70% dark gradient with text over it, so the extra
# resolution is spent on detail no one can see - and the no-upscale rule had
# already ruled a 2x out for four of the six sources anyway. Asking for the
# same width twice is how a Hero says "one density is enough" - build()
# recognises that and skips the 2x pass.
PAGE_BACKGROUNDS = [
    Hero(
        slug="bg-auth",
        source="ChatGPT Image Feb 10, 2026, 02_04_18 PM.png",
        focus_y=0.5,
        aspect=16 / 9,
        widths=(1536, 3072),
        # 2.7MB of PNG for a 1536px photograph, on all five password-reset
        # pages plus logout. The single worst byte-per-pixel file in the set.
        note="auth/password-reset backdrop, 1536px PNG source -- 1x only",
    ),
    Hero(
        slug="bg-login",
        source="RedBrahmanPic-scaled.jpg",
        focus_y=0.42,
        aspect=16 / 9,
        widths=(1920, 3840),
        # Portrait, 1920x2560, used as a landscape background: cover was
        # throwing away most of its height anyway. focus_y 0.42 keeps the
        # animal rather than the ground.
        note="login backdrop, portrait 1920px source -- 1x only",
    ),
    Hero(
        slug="bg-register",
        source="pexels-sippakorn-yamkasikorn-1745809-3421999 - Copy.jpg",
        focus_y=0.52,
        aspect=16 / 9,
        # 1x only, like the rest of PAGE_BACKGROUNDS: a 2x of this source came
        # out at 976KB, and behind the page's dark overlay not one of those
        # bytes is visible. See the list's own comment.
        widths=(1920, 1920),
        note="farmer registration backdrop, 5184px source -- 1x only",
    ),
    Hero(
        slug="bg-landing",
        source="sylvester-sabo-vVdpZEspAGs-unsplash.jpg",
        focus_y=0.58,
        aspect=16 / 9,
        widths=(1920, 1920),
        # Carries about/services/how-it-works/privacy/terms, and each of those
        # pages references it three times in one stylesheet.
        note="public content pages backdrop, 5374px source -- 1x only",
    ),
    Hero(
        slug="bg-vet",
        source="AdobeStock_570288267_Preview.jpeg",
        focus_y=0.45,
        aspect=16 / 9,
        widths=(1000, 2000),
        note="vet apply/track backdrop, 1000px source -- 1x only",
    ),
    Hero(
        slug="bg-vet-register",
        source="AdobeStock_440276915_Preview.jpeg",
        focus_y=0.45,
        aspect=16 / 9,
        widths=(1000, 2000),
        note="vet registration backdrop, 1000px source -- 1x only",
    ),
]


# The two photographs in the landing page's "For Farmers" / "For Vets"
# sections. Unlike everything above these are real <img> elements, not CSS
# backgrounds, and they sit in a col-lg-6 that tops out around 540 CSS px with
# `min-height: 500px; object-fit: cover`. So the slot is a ~540x600 portrait
# panel, and it was being handed a 1920x2560 photograph - the browser was
# downloading 886KB and throwing away three quarters of it.
#
# 0.9 is width/height, matching that panel. Here a 2x is worth having: these
# are foreground images with no overlay, viewed at close to their own size.
CONTENT_IMAGES = [
    Hero(
        slug="audience-farmer",
        source="RedBrahmanPic-scaled.jpg",
        focus_y=0.42,
        aspect=0.9,
        widths=(540, 1080),
        note="landing 'For Farmers' panel, portrait 1920px source",
    ),
    Hero(
        slug="audience-vet",
        source="AdobeStock_570288267_Preview.jpeg",
        focus_y=0.4,
        aspect=0.9,
        widths=(540, 1080),
        # 1000x658 landscape cropped to a portrait panel leaves only 592px of
        # width, so the 2x is an upscale and gets skipped. 1x it is.
        note="landing 'For Vets' panel, 1000px source -- 1x only",
    ),
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

    for hero in [*HEROES, *PAGE_BACKGROUNDS, *CONTENT_IMAGES]:
        path = SRC / hero.source
        if not path.exists():
            print(f"  MISSING  {hero.source}")
            problems += 1
            continue

        with Image.open(path) as raw:
            im = raw.convert("RGB")
            native_w = im.width
            banner = crop_to_aspect(im, hero.aspect, hero.focus_y)

            print(f"\n{hero.slug}  <-  {hero.source}")
            print(f"  source {native_w}x{raw.height}  |  {hero.note}")

            for label, width in zip(("1x", "2x"), hero.widths):
                if label == "2x" and width <= hero.widths[0]:
                    # A Hero that asks for the same width twice is saying one
                    # density is enough (see PAGE_BACKGROUNDS). Without this
                    # the 2x pass wrote a byte-identical duplicate file.
                    print("  2x skipped: this image is declared 1x-only")
                    continue
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
