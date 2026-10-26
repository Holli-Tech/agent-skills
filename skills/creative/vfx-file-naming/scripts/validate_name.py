#!/usr/bin/env python3
"""validate_name.py — validate a VFX filename against the ETC@USC spec.

Wraps parse_name.parse and applies additional spec checks: required slots,
padding, type vocabulary, whitespace, frame/ext coherence, length, etc.

Two levels of feedback:
  - reasons  → spec violations. The file is non-compliant (exit 1).
  - warnings → legal but suspicious (vendor code colliding with a known
    studio, deprecated slot, ...). The file is compliant (exit 0) but a
    human should look.

Usage:
    from validate_name import validate, validate_detailed
    ok, reasons = validate("un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr")
    detail = validate_detailed("...")
    detail["ok"], detail["reasons"], detail["warnings"]

CLI:
    python3 validate_name.py un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr
    # → OK (exit 0)

    python3 validate_name.py "un ff25 sb 0100 matt dd v001.1001.exr"
    # → FAIL: whitespace not allowed (spec §3.1) (exit 1)
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Tuple

from parse_name import parse, ParseError

# Spec §2.11 — single-frame extensions (frame token required)
SINGLE_FRAME_EXTS = {
    "exr", "dpx", "png", "tif", "tiff", "tga", "psd", "psb", "jpg", "jpeg",
}

# Vendor codes that collide with real studios. Legal, but worth a second look.
KNOWN_STUDIO_VENDORS = {
    "dd": "Digital Domain",
    "ilm": "Industrial Light & Magic",
    "weta": "Weta FX",
    "fr": "Framestore",
    "dneg": "DNEG",
    "sp": "Sony Pictures Imageworks",
    "rsi": "Rising Sun Pictures",
    "mpc": "MPC",
    "lp": "Luma Pictures",
    "spi": "SPI",
}


def validate_detailed(filename: str) -> dict:
    """Validate a VFX filename. Returns a dict with keys ok/reasons/warnings."""
    reasons: List[str] = []
    warnings: List[str] = []

    if not filename:
        return {"ok": False, "reasons": ["empty filename"], "warnings": []}

    if len(filename) > 255:
        reasons.append(f"filename length {len(filename)} > 255 (spec §3.1)")

    if any(c.isspace() for c in filename):
        reasons.append("whitespace not allowed (spec §3.1)")

    try:
        tokens = parse(filename)
    except ParseError as e:
        reasons.append(str(e))
        return {"ok": False, "reasons": reasons, "warnings": warnings}

    # --- Frame / extension coherence (§2.11) --------------------------
    ext = tokens["ext"]
    frame = tokens["frame"]
    if ext in SINGLE_FRAME_EXTS and frame is None:
        reasons.append(
            f"frame number required for single-frame extension '.{ext}' (spec §2.11)"
        )
    if ext not in SINGLE_FRAME_EXTS and frame is not None:
        reasons.append(
            f"frame number must be omitted for multi-frame extension '.{ext}' (spec §2.11)"
        )

    # --- Instance hygiene (§2.5) ---------------------------------------
    if tokens["instance"] == "00":
        warnings.append(
            "instance '00' is unusual; the spec's first instance is '01'"
        )

    # --- Vendor code (§2.7) -------------------------------------------
    vendor = tokens["vendor"]
    if vendor.lower() in KNOWN_STUDIO_VENDORS:
        warnings.append(
            f"vendor='{vendor}' matches a known studio "
            f"({KNOWN_STUDIO_VENDORS[vendor.lower()]}); confirm with production"
        )

    # --- Description hygiene (§2.6) -----------------------------------
    if tokens["description"] is not None and "_" in tokens["description"]:
        reasons.append(
            f"description='{tokens['description']}' contains underscore; "
            f"use '-' for word separation (spec §2.6)"
        )

    # --- Case consistency (§3.1) --------------------------------------
    # The spec prefers lower case, but 'FINAL' is the one vocabulary entry
    # that is upper case. Flag mixed case across the structured tokens.
    structured = [tokens["show"], tokens["seq"], tokens["type"], tokens["vendor"]]
    if any(t != t.lower() for t in structured) and tokens["type"] != "FINAL":
        warnings.append(
            "lower case is preferred for structured tokens (spec §3.1); "
            "only the 'FINAL' image type is upper case in the vocabulary"
        )

    return {
        "ok": len(reasons) == 0,
        "reasons": reasons,
        "warnings": warnings,
    }


def validate(filename: str) -> Tuple[bool, List[str]]:
    """Validate a VFX filename. Returns (ok, reasons).

    reasons lists spec violations only; warnings are available through
    validate_detailed().
    """
    detail = validate_detailed(filename)
    return detail["ok"], detail["reasons"]


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Validate a VFX filename against the spec.")
    parser.add_argument("filename", help="VFX filename to validate")
    parser.add_argument("--quiet", "-q", action="store_true", help="Print only OK/FAIL")
    args = parser.parse_args()

    detail = validate_detailed(args.filename)
    if detail["ok"]:
        if not args.quiet:
            print("OK")
        for w in detail["warnings"]:
            print(f"warning: {w}", file=sys.stderr)
        return 0

    print("FAIL", file=sys.stderr)
    for r in detail["reasons"]:
        print(f"  - {r}", file=sys.stderr)
    for w in detail["warnings"]:
        print(f"  ! {w}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
