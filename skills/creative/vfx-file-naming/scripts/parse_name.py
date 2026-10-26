#!/usr/bin/env python3
"""parse_name.py — parse a VFX filename back into a structured dict.

Inverse of build_name.py. Implements the ETC@USC / MovieLabs TR-VFX-IS v1.0
specification.

Usage:
    from parse_name import parse
    d = parse("un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr")
    # d = {
    #   'show': 'un-ff25', 'seq': 'sb', 'shot': '0100',
    #   'type': 'matt', 'instance': '01',
    #   'vendor': 'dd', 'rev': 1,
    #   'alternate': None, 'camera': None,
    #   'description': 'mp-v023', 'spec_version': None,
    #   'frame': 1001, 'ext': 'exr',
    # }

CLI:
    python3 parse_name.py un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr
    python3 parse_name.py --json un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Optional

from build_name import (
    IMAGE_TYPES,
    PLATE_TYPES,
    SEQ_PORTION_RE,
    SEQ_RE,
    SEQ_SHOW,
    SHOW_EPISODIC_RE,
    SHOW_RE,
    SPEC_VERSION_RE,
)

# Spec §3.1 — description: alphanumeric and dash only
DESC_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")

# Spec §2.1 — <spec-version> = "sv" + <major> "." + <minor>
# The spec states the minor version is two digits but its own examples use one
# ('sv01.0', 'sv01.2'), so one or two digits are accepted.
SPEC_VERSION_RE = re.compile(r"^sv\d{2}\.\d{1,2}$")

# §2.5 — type name may carry a 2-digit instance: matt01, bg02 …
# §2.5 also allows "other" + "<custom-code>" as a single token: other-magic
TYPE_RE = re.compile(r"^([a-zA-Z]+)(\d{2})?$")
TYPE_CUSTOM_RE = re.compile(r"^(other)-([a-zA-Z0-9-]+)$")

# §2.4 — 4-digit shot
SHOT_RE = re.compile(r"^\d{4}$")

# §2.8 — v + 3 or more digits
REV_RE = re.compile(r"^v(\d{3,})$")

# §2.7 — 2-3 alphanumeric vendor
VENDOR_RE = re.compile(r"^[a-zA-Z0-9]{2,3}$")

# §2.9 — a-<alternate>
ALTERNATE_RE = re.compile(r"^a-([a-zA-Z0-9-]+)$")

# §2.10 — L / R / C / N<n>
CAMERA_RE = re.compile(r"^(?:[LRC]|N\d+)$")


class ParseError(ValueError):
    """Raised when the filename does not parse cleanly into the spec's tokens."""


def _split_extension_and_frame(filename: str):
    """Split a filename into (stem, frame, ext).

    Handles the optional <spec-version> slot, whose encoding contains a dot
    ('sv01.0'), so a naive split on '.' is not enough.
    """
    parts = filename.split(".")
    if len(parts) < 2:
        raise ParseError("missing file extension")
    ext = parts[-1].lower()
    if not ext or not ext.isalnum():
        raise ParseError(f"extension '{ext}' is not alphanumeric")

    frame: Optional[int] = None
    rest = parts[:-1]

    # A frame is the last dot-part when it is all digits and at least 4 long.
    if rest and rest[-1].isdigit() and len(rest[-1]) >= 4:
        frame = int(rest[-1])
        rest = rest[:-1]

    # Rebuild the stem, re-joining a possible 'sv01.0' spec-version.
    stem = ".".join(rest)
    return stem, frame, ext


def parse(filename: str) -> dict:
    """Parse a VFX filename into a dict of structured tokens.

    Returns:
        dict with keys: show, seq, shot, type, instance, vendor, rev,
                        alternate, camera, description, spec_version,
                        frame, ext.

    Raises:
        ParseError on any structural problem.
    """
    if not filename:
        raise ParseError("empty filename")
    if any(c.isspace() for c in filename):
        raise ParseError("whitespace in filename (spec §3.1)")
    if len(filename) > 255:
        raise ParseError("filename > 255 chars (spec §3.1)")

    stem, frame, ext = _split_extension_and_frame(filename)
    tokens = stem.split("_")
    if len(tokens) < 6:
        raise ParseError(
            f"need at least 6 underscore-separated tokens, got {len(tokens)}: {tokens}"
        )

    # The spec's own examples are inconsistent about where the identifying
    # description sits. §3.2's syntax block puts it after the revision:
    #     <show>_<seq>_<shot>_<type>_<vendor>_v<rev>_<description>
    # but three of the §3.2.1 examples put it before the vendor:
    #     <show>_<seq>_<shot>_<type>_<description>_<vendor>_v<rev>
    # (e.g. 'un-ff25_show_0000_ldev_dom-old-age_dd_v001.1000.exr').
    # The normative form is what the builder emits; both are accepted here so
    # names copied from the specification parse correctly.
    description_before_vendor: Optional[str] = None
    if (
        len(tokens) >= 7
        and not VENDOR_RE.fullmatch(tokens[4])
        and VENDOR_RE.fullmatch(tokens[5])
        and REV_RE.fullmatch(tokens[6])
    ):
        description_before_vendor = tokens[4]
        tokens = tokens[:4] + tokens[5:7] + tokens[7:]

    # --- Required tokens (positions 0..5) -----------------------------
    show, seq, shot, type_with_instance, vendor, rev_token = tokens[:6]

    # The revision token may carry the identifying description joined by a
    # dash, as the spec's own examples do ('v001-fire', 'v001-mp-v023').
    # §3.2's syntax block says the description is separated by an underscore;
    # the examples use a dash. Both are accepted on input.
    inline_description: Optional[str] = description_before_vendor
    rev_dash = re.fullmatch(r"^(v\d{3,})-(.+)$", rev_token)
    if rev_dash:
        rev_token, inline_description = rev_dash.group(1), rev_dash.group(2)
    # §2.2 — Show ID
    if not (SHOW_RE.fullmatch(show) or SHOW_EPISODIC_RE.fullmatch(show)):
        raise ParseError(
            f"show='{show}' is not a valid Show ID (spec §2.2): expected "
            f"[[<studio>-]<show>] with a 4-character show, or 'gotr-s08e007'"
        )

    # §2.3 — VFX Sequence
    if not (
        seq == SEQ_SHOW or SEQ_RE.fullmatch(seq) or SEQ_PORTION_RE.fullmatch(seq)
    ):
        raise ParseError(
            f"seq='{seq}' invalid (spec §2.3): must be 2-4 alphanum, 'show', "
            f"or 'act<n>' / 'reel<n>' / 'part<n>'"
        )

    # §2.4 — VFX Shot
    if not SHOT_RE.fullmatch(shot):
        raise ParseError(f"shot='{shot}' not 4 digits (spec §2.4)")

    # §2.5 — Image Type + optional instance
    type_match = TYPE_RE.fullmatch(type_with_instance)
    type_custom = None if type_match else TYPE_CUSTOM_RE.fullmatch(type_with_instance)
    if type_match:
        type_ = type_match.group(1)
        instance = type_match.group(2)
    elif type_custom:
        type_ = type_custom.group(1)
        instance = type_custom.group(2)
    else:
        raise ParseError(
            f"type_with_instance='{type_with_instance}' not a type name "
            f"plus optional 2-digit instance (spec §2.5)"
        )
    if type_ != "other" and type_ not in IMAGE_TYPES:
        raise ParseError(
            f"type='{type_}' not in spec vocabulary §2.5 "
            f"(use 'other-<custom>' for a custom category)"
        )

    # §2.7 — Vendor Code
    if not VENDOR_RE.fullmatch(vendor):
        raise ParseError(f"vendor='{vendor}' not 2-3 alphanum (spec §2.7)")

    # §2.8 — Revision Code
    rev_match = REV_RE.fullmatch(rev_token)
    if not rev_match:
        raise ParseError(f"revision='{rev_token}' not 'v' + >=3 digits (spec §2.8)")
    rev = int(rev_match.group(1))

    # --- Optional tokens (positions 6+) -------------------------------
    # Order per spec §3.2: alternate, camera, description, spec-version.
    optional = tokens[6:]
    alternate: Optional[str] = None
    camera: Optional[str] = None
    description: Optional[str] = None
    spec_version: Optional[str] = None

    idx = 0

    # Alternate: 'a-<tag>'
    if idx < len(optional):
        alt_match = ALTERNATE_RE.fullmatch(optional[idx])
        if alt_match:
            alternate = alt_match.group(1)
            idx += 1

    # Camera: L / R / C / N<n>
    if idx < len(optional) and CAMERA_RE.fullmatch(optional[idx]):
        camera = optional[idx]
        idx += 1

    # Spec version: 'sv01.0' — a distinct slot, comes after the description.
    # It is the only optional token that can contain a dot, so it is detected
    # by pattern on the last remaining token.
    if idx < len(optional) and SPEC_VERSION_RE.fullmatch(optional[-1]):
        spec_version = optional[-1]
        optional = optional[:-1]
        idx = len(optional)

    # Description: everything remaining. The description uses '-' as the
    # internal word separator (spec §2.6); a hand-written filename may have
    # split it across several underscore-separated tokens, so re-join with '-'.
    if idx < len(optional):
        desc_parts = optional[idx:]
        for part in desc_parts:
            if not all(c in DESC_CHARS for c in part):
                raise ParseError(
                    f"description token '{part}' contains forbidden characters "
                    f"(spec §2.6: only [a-zA-Z0-9-])"
                )
        description = "-".join(desc_parts)

    if inline_description is not None:
        if description is not None:
            raise ParseError(
                "filename carries two identifying descriptions "
                f"('{inline_description}' and '{description}'); spec §3.2 "
                f"allows only one"
            )
        description = inline_description

    return {
        "show": show,
        "seq": seq,
        "shot": shot,
        "type": type_,
        "instance": instance,
        "vendor": vendor,
        "rev": rev,
        "alternate": alternate,
        "camera": camera,
        "description": description,
        "spec_version": spec_version,
        "frame": frame,
        "ext": ext,
    }


def is_plate(type_: str) -> bool:
    """True when the image type is a plate (spec §2.5.1)."""
    return type_ in PLATE_TYPES


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Parse a VFX filename into structured tokens.")
    parser.add_argument("filename", help="VFX filename to parse")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    try:
        result = parse(args.filename)
    except ParseError as e:
        print(f"parse_name: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        width = max(len(k) for k in result)
        for k, v in result.items():
            print(f"{k:<{width}} : {v}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
