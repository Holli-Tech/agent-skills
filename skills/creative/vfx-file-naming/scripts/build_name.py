#!/usr/bin/env python3
"""build_name.py — programmatic builder for VFX image-sequence filenames.

Implements the ETC@USC / MovieLabs "VFX Image Sequence Naming" specification
(TR-VFX-IS v1.0, June 23 2020).

Canonical syntax (spec §3.2):

    <showid>_<vfx-sequence>_<vfx-shot>_<image-type>_<vendor-code>_<revision-code>
    {_<alternate>}{_<camera-reference>}{_<identifying-description>}{_<spec-version>}
    .<frame-number>.<file-extension>

Usage:
    from build_name import build
    name = build(
        show="un-ff25", seq="sb", shot="0100", type_="matt", instance="01",
        vendor="dd", rev=1, description="mp-v023", frame=1001, ext="exr",
    )
    # → 'un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr'

CLI:
    # Flags (recommended — unambiguous):
    python3 build_name.py --show un-ff25 --seq sb --shot 0100 --type matt \
        --instance 01 --vendor dd --rev 1 --description mp-v023 \
        --frame 1001 --ext exr

    # Positional: show seq shot type vendor rev [description] [frame] [ext]
    # Note: --instance is NOT positional — pass it via flag when you need it.
    python3 build_name.py un-ff25 sb 0100 matt dd 1 mp-v023 1001 exr
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Spec §2.5 — Image Type controlled vocabulary
# ---------------------------------------------------------------------------

# §2.5.1 Type Names for Inputs to VFX (Plates) — consistent with VES-TS
PLATE_TYPES = {
    "mp",    # Main Plate
    "bg",    # Background plate
    "fg",    # Foreground plate
    "el",    # Element plate
    "cp",    # Clean Plate
    "rg",    # Reference Plate
}

# §2.5.2 Type Names for Other Inputs to and Outputs from VFX
OTHER_TYPES = {
    "anim",   # animation version (playblast, over-green)
    "comp",   # composited VFX shots
    "cnpt",   # Concept
    "FINAL",  # Special designation for final comp
    "layo",   # Layout versions
    "ldev",   # Look dev
    "matt",   # Mattes and masks
    "prev",   # Pre vis
    "prox",   # Proxy
    "pstv",   # Post vis
    "repo",   # repositioning
    "spfx",   # effects pass
    "test",   # test shots, slap comps
    "time",   # retime approvals
    "vcam",   # virtual camera
    "other",  # other + <custom-code>
}

IMAGE_TYPES = PLATE_TYPES | OTHER_TYPES

# §2.5 — "other" is combined with a custom code: other-magic
CUSTOM_TYPE_PREFIX = "other"

# Spec §2.1 — <spec-version> = "sv" + <major> "." + <minor>
# The spec states the minor version is two digits but its own examples use one
# ('sv01.0', 'sv01.2'), so one or two digits are accepted.
SPEC_VERSION_RE = re.compile(r"^sv\d{2}\.\d{1,2}$")

# Spec §2.11 — single-frame extensions (frame token required)
SINGLE_FRAME_EXTS = {
    "exr", "dpx", "png", "tif", "tiff", "tga", "psd", "psb",
    "jpg", "jpeg",
}

# Multi-frame containers and workfiles (frame token omitted)
MULTI_FRAME_EXTS = {
    "mov", "mp4", "nk", "blend", "drp", "drt", "dra", "aep", "aepx",
    "ma", "mb", "hip", "hiplc", "hipnc", "uasset", "abc",
}

# Spec §3.1 — description: alphanumeric and dash only
DESC_RE = re.compile(r"^[a-zA-Z0-9-]*$")
NO_WS_RE = re.compile(r"\s")

# §2.2 — Show ID: optional "<studio-or-franchise>-" prefix (2 chars recommended),
# then the show. Parts are separated by dashes, which act as whitespace inside
# the field.
#   individual work : [<studio>-]<show>              e.g. ff25, un-ff25, sw-rasp
#   episodic        : [<studio>-]<series>-s<season>e<episode>
#                                                      e.g. gotr-s08e007
SHOW_RE = re.compile(r"^(?:[a-zA-Z0-9]{2,}-)?[a-zA-Z0-9]{4}$")
SHOW_EPISODIC_RE = re.compile(
    r"^(?:[a-zA-Z0-9]{2,}-)?[a-zA-Z0-9]{4}-s\d{2}e\d{3}$"
)
# §2.3 — sequence: 2-4 alphanum, or 'show', or act<n>/reel<n>/part<n>
SEQ_RE = re.compile(r"^[a-zA-Z0-9]{2,4}$")
SEQ_PORTION_RE = re.compile(r"^(act|reel|part)\d+$")
SEQ_SHOW = "show"


class BuildError(ValueError):
    """Raised on invalid input that would produce a non-spec filename."""


def _validate_token(name: str, value: str, pattern: str, max_len: Optional[int] = None) -> str:
    """Run a regex check on a token. Raise BuildError with the token name on failure."""
    if NO_WS_RE.search(value):
        raise BuildError(f"{name}='{value}' contains whitespace (spec §3.1)")
    if max_len is not None and len(value) > max_len:
        raise BuildError(f"{name}='{value}' exceeds {max_len} characters")
    if not re.fullmatch(pattern, value):
        raise BuildError(f"{name}='{value}' does not match pattern {pattern!r} (spec §2)")
    return value


def _validate_show(show: str) -> str:
    """Show ID: individual work or episodic (spec §2.2)."""
    if NO_WS_RE.search(show):
        raise BuildError(f"show='{show}' contains whitespace (spec §3.1)")
    if not (SHOW_RE.fullmatch(show) or SHOW_EPISODIC_RE.fullmatch(show)):
        raise BuildError(
            f"show='{show}' is not a valid Show ID (spec §2.2). Expected "
            f"[[<studio>-]<show>] where <show> is 4 alphanumeric characters, "
            f"or an episodic id like 'gotr-s08e007'"
        )
    return show


def _validate_seq(seq: str) -> str:
    """VFX Sequence (spec §2.3)."""
    if NO_WS_RE.search(seq):
        raise BuildError(f"seq='{seq}' contains whitespace (spec §3.1)")
    if seq == SEQ_SHOW or SEQ_RE.fullmatch(seq) or SEQ_PORTION_RE.fullmatch(seq):
        return seq
    raise BuildError(
        f"seq='{seq}' is not a valid VFX Sequence (spec §2.3). Expected 2-4 "
        f"alphanumeric characters, 'show', or 'act<n>' / 'reel<n>' / 'part<n>'"
    )


def build(
    show: str,
    seq: str,
    shot: str,
    type_: str,
    vendor: str,
    rev: int,
    instance: Optional[str] = None,
    description: Optional[str] = None,
    alternate: Optional[str] = None,
    camera: Optional[str] = None,
    spec_version: Optional[str] = None,
    frame: Optional[int] = None,
    ext: str = "exr",
    desc_sep: str = "_",
) -> str:
    """Build a spec-compliant VFX image-sequence filename.

    Required: show, seq, shot, type_, vendor, rev, ext.
    Optional: instance, description, alternate, camera, spec_version, frame.

    Padding (spec §2.4, §2.8, §2.11):
        - shot: 4 digits ('0000' means no shot applies)
        - rev: 3 digits minimum
        - frame: 4 digits minimum

    Returns the filename string (no path prefix).
    """
    # ---- Show ID (§2.2) --------------------------------------------------
    show = _validate_show(show)

    # ---- VFX Sequence (§2.3) --------------------------------------------
    seq = _validate_seq(seq)

    # ---- VFX Shot (§2.4) ------------------------------------------------
    shot = _validate_token("shot", shot, r"\d{4}")

    # ---- Image Type (§2.5) ----------------------------------------------
    if NO_WS_RE.search(type_):
        raise BuildError(f"type_='{type_}' contains whitespace (spec §3.1)")
    is_custom_type = type_.startswith(CUSTOM_TYPE_PREFIX + "-")
    if not is_custom_type and type_ != CUSTOM_TYPE_PREFIX and type_ not in IMAGE_TYPES:
        raise BuildError(
            f"type_='{type_}' not in spec vocabulary §2.5 "
            f"(or use 'other-<custom>' for a custom category)"
        )
    if instance is not None:
        instance = _validate_token("instance", instance, r"\d{2}")
        type_with_instance = f"{type_}{instance}"
    else:
        type_with_instance = type_

    # ---- Vendor Code (§2.7) ---------------------------------------------
    vendor = _validate_token("vendor", vendor, r"[a-zA-Z0-9]{2,3}")

    # ---- Revision Code (§2.8) -------------------------------------------
    if not isinstance(rev, int) or rev < 0:
        raise BuildError(f"rev={rev!r} must be a non-negative integer")
    rev_width = max(3, len(str(rev)))
    rev_token = f"v{rev:0{rev_width}d}"

    # ---- Alternate (§2.9) ------------------------------------------------
    if alternate is not None:
        alternate = _validate_token("alternate", alternate, r"[a-zA-Z0-9-]+", max_len=32)
        alt_token = f"a-{alternate}"
    else:
        alt_token = None

    # ---- Camera reference (§2.10) ---------------------------------------
    if camera is not None:
        camera = _validate_token("camera", camera, r"[LRC]|N\d+", max_len=4)
        cam_token = camera
    else:
        cam_token = None

    # ---- Identifying Description (§2.6) ---------------------------------
    if description is not None:
        if NO_WS_RE.search(description):
            raise BuildError(f"description='{description}' contains whitespace (spec §3.1)")
        if "_" in description:
            raise BuildError(
                f"description='{description}' contains underscore; "
                f"use '-' to separate words (spec §2.6)"
            )
        if not DESC_RE.fullmatch(description):
            raise BuildError(
                f"description='{description}' contains forbidden characters; "
                f"only [a-zA-Z0-9-] allowed (spec §2.6)"
            )
        desc_token = description
    else:
        desc_token = None

    # ---- Spec Version (§2.1) --------------------------------------------
    if spec_version is not None:
        spec_version = _validate_token("spec_version", spec_version, r"sv\d{2}\.\d{1,2}")
        spec_token = spec_version
    else:
        spec_token = None

    # ---- Description separator ------------------------------------------
    if desc_sep not in ("_", "-"):
        raise BuildError(f"desc_sep={desc_sep!r} must be '_' or '-'")

    # ---- Frame Number (§2.11) -------------------------------------------
    ext = ext.lstrip(".").lower()
    frame_token: Optional[str]
    if ext in SINGLE_FRAME_EXTS:
        if frame is None:
            raise BuildError(
                f"frame is required for single-frame extension '.{ext}' (spec §2.11)"
            )
        if not isinstance(frame, int) or frame < 0:
            raise BuildError(f"frame={frame!r} must be a non-negative integer")
        frame_token = f"{frame:04d}"
    elif ext in MULTI_FRAME_EXTS:
        frame_token = None
        if frame is not None:
            print(
                f"warning: frame={frame} ignored for multi-frame extension '.{ext}' (spec §2.11)",
                file=sys.stderr,
            )
    else:
        frame_token = None

    # ---- Assemble (§3.2) -------------------------------------------------
    tokens = [show, seq, shot, type_with_instance, vendor, rev_token]
    for optional in (alt_token, cam_token, spec_token):
        if optional is not None:
            tokens.append(optional)

    stem = "_".join(tokens)

    # The identifying description is the one slot where the spec disagrees
    # with itself: the §3.2 syntax block separates it with an underscore,
    # while every example in §3.2.1 joins it to the revision with a dash
    # ('v001-fire', 'v001-mp-v023') and notes "the use of dash because the
    # description is one field". 'desc_sep' chooses; the default follows the
    # normative syntax block, and the parser accepts both.
    if desc_token is not None:
        if desc_sep == "-":
            stem = f"{stem}-{desc_token}"
        else:
            stem = f"{stem}_{desc_token}"

    parts = [stem]
    if frame_token is not None:
        parts.append(frame_token)
    parts.append(ext)
    filename = ".".join(parts)

    # Spec §3.1 — max 255 characters
    if len(filename) > 255:
        raise BuildError(f"filename length {len(filename)} > 255 (spec §3.1)")

    return filename


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Build a spec-compliant VFX filename.")
    parser.add_argument("positional", nargs="*",
                        help="show seq shot type vendor rev [description] [frame] [ext]")
    parser.add_argument("--show", help="Show ID (e.g. 'un-ff25', 'got-s08e007')")
    parser.add_argument("--seq", help="VFX Sequence (2-4 alnum, or 'show'/'act1'/'reel2'/'part1')")
    parser.add_argument("--shot", help="VFX Shot (4 digits; '0000' = no shot)")
    parser.add_argument("--type", dest="type_", help="Image type (spec §2.5 vocabulary)")
    parser.add_argument("--instance", help="Optional 2-digit instance for the type")
    parser.add_argument("--vendor", help="Vendor code (2-3 alphanum)")
    parser.add_argument("--rev", type=int, help="Revision number (integer)")
    parser.add_argument("--description", help="Identifying description (alphanum + dash)")
    parser.add_argument("--alternate", help="Alternate tag (without 'a-' prefix)")
    parser.add_argument("--camera", help="Camera label (L/R/C/N<NN>)")
    parser.add_argument("--spec-version", help="Spec version, e.g. sv01.0")
    parser.add_argument("--frame", type=int, help="Frame number (required for single-frame ext)")
    parser.add_argument("--ext", default="exr", help="File extension (default: exr)")
    parser.add_argument("--desc-sep", default="_", choices=["_", "-"],
                        help="separator before the identifying description: "
                             "'_' (spec §3.2 syntax) or '-' (spec §3.2.1 examples)")
    args = parser.parse_args()

    if args.show:
        kwargs = {
            "show": args.show, "seq": args.seq, "shot": args.shot, "type_": args.type_,
            "vendor": args.vendor, "rev": args.rev, "instance": args.instance,
            "description": args.description, "alternate": args.alternate,
            "camera": args.camera, "spec_version": args.spec_version,
            "frame": args.frame, "ext": args.ext, "desc_sep": args.desc_sep,
        }
        missing = [k for k in ("show", "seq", "shot", "type_", "vendor", "rev") if not kwargs.get(k)]
        if missing:
            parser.error(f"missing required: {', '.join(missing)}")
    else:
        # Positional: show seq shot type vendor rev [tail...]
        # The tail is [description] [frame] [ext]. We read it right-to-left
        # because (a) bash drops empty "" args, breaking left-to-right parsing,
        # and (b) the ext is the most disambiguating token (known vocabulary).
        pos = args.positional
        if len(pos) < 6:
            parser.error(
                "need at least: show seq shot type vendor rev "
                "[description] [frame] [ext]"
            )
        show, seq, shot, type_, vendor, rev_str = pos[:6]
        tail = list(pos[6:])

        # Pop ext from the right if it's a known extension
        ext = args.ext
        if tail and tail[-1].lower().lstrip(".") in SINGLE_FRAME_EXTS | MULTI_FRAME_EXTS:
            ext = tail.pop().lower().lstrip(".")

        # Pop frame from the right if it's all digits and the ext needs one
        frame = args.frame
        if tail and tail[-1].isdigit() and ext in SINGLE_FRAME_EXTS:
            frame = int(tail.pop())

        # Whatever's left is the description
        description = " ".join(tail) if tail else None
        if not description:
            description = args.description

        kwargs = {
            "show": show, "seq": seq, "shot": shot, "type_": type_,
            "vendor": vendor, "rev": int(rev_str),
            "instance": args.instance, "description": description,
            "alternate": args.alternate, "camera": args.camera,
            "spec_version": args.spec_version, "frame": frame, "ext": ext,
            "desc_sep": args.desc_sep,
        }

    try:
        print(build(**kwargs))
        return 0
    except BuildError as e:
        print(f"build_name: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_cli())
