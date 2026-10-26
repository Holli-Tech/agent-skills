#!/usr/bin/env python3
"""audit_folder.py — audit a folder of VFX files for spec compliance.

Walks the directory, parses each filename, classifies it as
plate / matte / comp / render / unknown, and reports breakage.

Usage:
    python3 audit_folder.py /path/to/shots
    python3 audit_folder.py /path/to/shots --json
    python3 audit_folder.py /path/to/shots --recursive

Exit code = number of broken files (0 = clean).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from validate_name import validate_detailed
from parse_name import parse, ParseError

# Image type → human category (spec §2.5)
TYPE_CATEGORY = {
    # Plates (§2.5.1)
    "mp": "plate", "bg": "plate", "fg": "plate",
    "el": "plate", "cp": "plate", "rg": "plate",
    # Other inputs/outputs (§2.5.2)
    "matt": "matte",
    "comp": "comp", "FINAL": "comp",
    "cnpt": "concept", "layo": "layout", "ldev": "lookdev",
    "anim": "animation", "spfx": "fx", "prev": "previs", "pstv": "postvis",
    "prox": "proxy", "repo": "repositioning", "test": "test",
    "time": "retime", "vcam": "virtual-cam", "other": "other",
}


def audit_folder(root: str, recursive: bool = False) -> dict:
    """Audit a folder for VFX filename compliance. Returns a report dict."""
    root_path = Path(root)
    if not root_path.exists():
        return {"error": f"path does not exist: {root}"}

    pattern = "**/*" if recursive else "*"
    files = [p for p in root_path.glob(pattern) if p.is_file()]

    total = len(files)
    by_category: Counter = Counter()
    by_ext: Counter = Counter()
    broken: list = []
    warned: list = []
    ok_count = 0

    for f in files:
        name = f.name
        detail = validate_detailed(name)
        if detail["ok"]:
            ok_count += 1
            if detail["warnings"]:
                warned.append({"file": str(f), "warnings": detail["warnings"]})
            try:
                tokens = parse(name)
            except ParseError:
                tokens = None
            if tokens:
                cat = TYPE_CATEGORY.get(tokens["type"], "unknown")
                by_category[cat] += 1
                by_ext[tokens["ext"]] += 1
        else:
            broken.append({"file": str(f), "reasons": detail["reasons"]})

    return {
        "root": str(root_path),
        "total_files": total,
        "ok_files": ok_count,
        "broken_files": len(broken),
        "files_with_warnings": len(warned),
        "by_category": dict(by_category),
        "by_extension": dict(by_ext),
        "warnings": warned,
        "broken": broken,
    }


def _print_report(report: dict, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(report, indent=2))
        return

    if "error" in report:
        print(f"audit_folder: {report['error']}", file=sys.stderr)
        return

    print(f"VFX Filename Audit — {report['root']}")
    print("=" * 60)
    print(f"Total files   : {report['total_files']}")
    print(f"Compliant     : {report['ok_files']}")
    print(f"Broken        : {report['broken_files']}")
    print(f"With warnings : {report['files_with_warnings']}")

    if report["by_category"]:
        print("\nBy category:")
        for cat, n in sorted(report["by_category"].items(), key=lambda x: -x[1]):
            print(f"  {cat:<14}: {n}")

    if report["by_extension"]:
        print("\nBy extension:")
        for ext, n in sorted(report["by_extension"].items(), key=lambda x: -x[1]):
            print(f"  .{ext:<10}: {n}")

    if report["warnings"]:
        print(f"\nWarnings ({len(report['warnings'])}):")
        for entry in report["warnings"][:10]:
            print(f"  {entry['file']}")
            for w in entry["warnings"]:
                print(f"      ! {w}")
        if len(report["warnings"]) > 10:
            print(f"  ... and {len(report['warnings']) - 10} more")

    if report["broken"]:
        print(f"\nBroken files ({len(report['broken'])}):")
        for entry in report["broken"][:20]:  # cap output
            print(f"  {entry['file']}")
            for r in entry["reasons"]:
                print(f"      - {r}")
        if len(report["broken"]) > 20:
            print(f"  ... and {len(report['broken']) - 20} more")


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Audit a folder for VFX filename compliance.")
    parser.add_argument("path", help="Directory to audit")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    report = audit_folder(args.path, recursive=args.recursive)
    _print_report(report, as_json=args.json)
    return report.get("broken_files", 1)


if __name__ == "__main__":
    sys.exit(_cli())
