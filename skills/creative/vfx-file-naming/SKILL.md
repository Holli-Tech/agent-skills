---
name: vfx-file-naming
description: Use when generating, parsing, validating or auditing VFX image-sequence file names (plates, mattes, comps, render passes, workfiles) for creative/DCC apps (Photoshop, Nuke, Blender, DaVinci Resolve, After Effects, Houdini). Anchored in the ETC@USC/MovieLabs "VFX Image Sequence Naming" specification (TR-VFX-IS v1.0, June 2020) and the VES Transfer Specification vocabulary. Covers the token grammar (show / sequence / shot / image-type / vendor / revision / description / frame), the full controlled vocabulary, and matte-specific conventions (garbage, hard, soft, key, core, edge, roto, cryptomatte, premultiplied vs straight alpha). Use this skill when an artist needs to name a save, a script needs to construct or parse a filename, or a supervisor needs to audit a folder.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vfx, file-naming, dcc, comp, matte, movie-labs, etc, image-sequence]
    related_skills: [writing-great-skills, requesting-code-review, reliable-file-editing]
---

# VFX File Naming

## Overview

A pragmatic file-naming grammar for VFX image sequences, anchored in the **ETC@USC / MovieLabs "VFX Image Sequence Naming"** specification (TR-VFX-IS v1.0, June 23 2020) and aligned with the **VES Transfer Specification** controlled vocabulary. The skill is **app-agnostic**: the grammar is the same whether the file is written by Nuke's Write node, Photoshop's Export Layers, Blender's File Output, DaVinci Resolve's render, or an After Effects render queue. Each app has a small adapter section; the core rules do not change.

Two layers:

1. **Core grammar** (this SKILL.md) — the token set that most work needs. Show, VFX sequence, VFX shot, image type, vendor, revision, description, frame, extension.
2. **Full ETC profile** (`references/etc-image-sequence-spec.md`) — the complete metadata model including alternate versions, multi-camera reference, spec-version, and every controlled vocabulary entry. Use when delivering to a studio, pipeline or vendor.

The skill ships with a Python toolkit (`scripts/`) that builds, parses and validates filenames against the spec, so the rules are executable rather than advisory. The test fixtures are the specification's own worked examples, so the suite doubles as a conformance check against the primary source.

## When to Use

Use this skill when the task involves any of:

- **Naming** a new file: "save this matte for shot 0100", "what should I call this comp output?", "render this to a sequence — what pattern?"
- **Generating** names programmatically: a Nuke Write-node path builder, a Photoshop Export-Layers-to-Files action, a Blender compositor output template, a render-farm upload script.
- **Parsing** existing names: extracting the shot number from a path, batching Read-nodes by image type, validating a vendor delivery.
- **Auditing** a folder: renaming a legacy library to comply, finding files that break the spec, mapping between house naming and the ETC spec.
- **Migrating** between apps: a Nuke comp exported as a multilayer EXR to be read by Blender, a Resolve render ingested by editorial — the filename must round-trip.

**Do not use** for:

- Generic software file naming (Python modules, config files) — no domain value here.
- Asset-only naming (CHR / ENV / PRO tokens for reusable assets) — a different convention (VES-TS asset class). The shot-level naming overlaps but the asset-namespace grammar is different.
- Single-frame still-image naming outside a VFX or post context (Instagram, stock photos) — the frame-padded grammar and the `matt` type make no sense there.

## The Core Grammar

A VFX image-sequence filename is one line, no spaces, tokens separated by underscores, the frame number and extension separated by dots.

```
<show>_<seq>_<shot>_<type>_<vendor>_v<rev>{_<description>}.<frame>.<ext>
```

**Required** (every file has these):

| Position | Token | Format | Example | Meaning |
|---|---|---|---|---|
| 1 | `<show>` | 4 alphanum, optionally `<studio>-` prefixed | `un-ff25`, `gotr-s08e007` | Show / episode ID, unique across the studio's catalogue |
| 2 | `<seq>` | 2–4 alphanum, or `show` / `act<n>` / `reel<n>` / `part<n>` | `ib`, `act3` | VFX sequence (a logical group of shots) |
| 3 | `<shot>` | 4 digits, padded | `0100`, `0000` | VFX shot number. `0000` = no shot applies (model, whole sequence, whole show) |
| 4 | `<type>` | Vocabulary code, optionally + 2-digit instance | `matt01`, `bg` | Image type — see the vocabulary below |
| 5 | `<vendor>` | 2–3 alphanum | `dd`, `ilm` | Vendor code, assigned by production |
| 6 | `v<rev>` | `v` + ≥3 digits, padded | `v001`, `v023` | Revision — bumps when the same file iterates |

**Conditional**:

| Position | Token | Format | When |
|---|---|---|---|
| 7 | `a-<alt>` | `a-` + free string | When this is **not** the primary version (4K when 6K is primary) |
| 8 | `<camera>` | `L`, `R`, `C`, or `N<NN>` | Multi-camera or stereo shots only |
| 9 | `<description>` | alphanum + `-` | Extra context: the matte type, the parent plate's revision, the subject |
| 10 | `<spec-version>` | `sv01.0` | Rarely used; declares the spec version the name was encoded against |
| 11 | `<frame>` | ≥4 digits, padded, dot separator | Single-frame files (EXR, DPX). Omitted for MOV |
| — | `<ext>` | conventional extension | `.exr`, `.dpx`, `.mov`, `.png`, `.psd` |

**Separator rules (non-negotiable):**

- `_` between tokens. **If a parameter is missing the underscore is still there** — that is what makes the name parseable.
- `.` before the frame number and before the extension.
- **No whitespace.** Never.
- **Lower case preferred**, and case must never be used to distinguish terms. (`FINAL` is the one vocabulary entry that is upper case.)

### A real example

```
un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr
```

*Show `un-ff25` (Universal's Fast and Furious 25), sequence `ib`, shot `0100`, matte #01, made by `dd` (Digital Domain), revision 3, a hard premultiplied matte, frame 1001, OpenEXR.*

### The description — a spec quirk

The spec's §3.2 syntax block puts the **underscore** before the identifying description, but several of its own worked examples join it to the revision with a **dash** (`v001-fire`, `v001-mp-v023`), annotated "the use of dash because the description is one field". And three examples place the description *before* the vendor instead of after the revision:

```
un-ff25_show_0000_ldev_dom-old-age_dd_v001.1000.exr
```

The spec does not agree with itself here. This skill's tooling resolves it:

- The **builder emits the normative form** (description last, underscore-separated); `--desc-sep -` produces the dash variant.
- The **parser accepts all of it** — underscore or dash, description before or after the vendor — so names copied from the specification parse correctly.

### Image Type Vocabulary

From spec §2.5, aligned with VES-TS. Full table in `references/controlled-vocabulary.md`.

**Plates — inputs to VFX:**

| Code | Meaning |
|---|---|
| `mp` | Main plate (the single plate a shot needs) |
| `bg` | Background plate (`bg01`, `bg02`…) |
| `fg` | Foreground plate (`fg12`…) |
| `el` | Element plate — isolated element, partial comp, roto or CG element |
| `cp` | Clean plate, for cleanup work |
| `rg` | Reference plate — lighting reference and similar |

**Other inputs and outputs:**

| Code | Meaning |
|---|---|
| `matt` | **Mattes and masks** — see the matte conventions below |
| `anim` | Animation for review (playblast, over-green) |
| `comp` | The composited shot (intermediate / WIP) |
| `FINAL` | The delivered comp |
| `cnpt` | Concept |
| `layo` | Layout (environment approval) |
| `ldev` | Look dev |
| `prev` / `pstv` | Pre-vis / post-vis |
| `prox` | Proxy |
| `repo` | Repositioning |
| `spfx` | Effects pass — smoke, fire, fluid |
| `test` | Test shots, slap comps |
| `time` | Retime approvals |
| `vcam` | Virtual camera |
| `other-<custom>` | Any category the spec does not cover, e.g. `other-magic` |

The **2-digit instance** distinguishes multiple sequences of the same type on one shot. **A different instance is a distinct plate, not a new version.** A second background plate is `bg02`, not `bg01` at a higher revision.

## Matte Conventions

Mattes are where naming usually goes wrong: there are a dozen kinds, they look alike, and a hard matte and a soft matte are not interchangeable downstream. The spec gives them one type code (`matt`) and lets the **identifying description** carry the type. This skill fixes the vocabulary so it does not drift per show.

| Matte type | Description token | Notes |
|---|---|---|
| Hard matte (binary alpha) | `hard` | Silhouette only, no soft edge |
| Soft matte / alpha | `soft` | Grayscale alpha with anti-aliasing |
| Roto matte | `roto-<subject>` | Frame-by-frame roto; name the subject: `roto-subject`, `roto-hair` |
| Garbage matte | `garbage` | Cuts out unwanted elements (mics, booms, crew) |
| Key matte | `key` | Colour-key output (Primatte, Keylight…) |
| Core matte | `core` | Inner key — preserves hair and fine detail |
| Edge matte | `edge` | Holds the transition zone only |
| Clean plate matte | `clean` | Repaint / paint-fix plate |
| Cryptomatte | `crypto-object` / `crypto-material` / `crypto-asset` | ID mattes from Cycles, Arnold, VRay |
| Power window / qualifier | `pw-<n>` / `qualifier-<n>` | DaVinci Resolve exports |

**Premultiplication** is explicit, because a beauty and its matte that disagree on the flag get unpremultiplied twice:

- `-premult` — RGB includes the alpha (multiply RGB by alpha to unpremultiply)
- `-unpremult` — RGB is straight, full colour regardless of alpha
- `-premulrsa` — premultiplied, RGB pre-divided by alpha (rare, Resolve-centric)

**Parenting** is recorded in the description, exactly as the spec does it:

```
un-ff25_ib_0100_mp_dd_v023.1001.exr            # the parent plate, revision 23
un-ff25_ib_0100_matt_dd_v001_mp-v023.1001.exr   # the matte that belongs to it
```

The matte's own revision is independent — bump it to `v002` when the matte itself is revised. Deep-dive in `references/matte-types.md`.

## App-Specific Anchors

The grammar is the same everywhere. Only the mechanics differ — the padding
syntax, the extension slot, and one or two gotchas per app.

| App | Frame padding | Where the name lives | Watch out for |
|---|---|---|---|
| **Nuke** | `####` | Write node → `file` knob | Use a literal `.exr`, not the protocol prefix `exr://` — other apps cannot resolve it |
| **Photoshop** | n/a (still) | Export > Layers to Files uses the layer name | Clean the layer names first; for PNG alpha use **Matte: None** |
| **Blender** | `###` | File Output node, or Output Properties | `//` is relative to the `.blend` file; Cryptomatte layer names use a dot, filenames a dash |
| **DaVinci Resolve** | `$Token` | Deliver page → custom render name | Projects live in a **Project Library** (a database), not loose files — the naming applies to the rendered sequence |
| **After Effects** | `[####]` | Output Module → Name Template | Same template syntax as Nuke |
| **Houdini** | `$F4` | COP / Render Output | — |

`scripts/app_presets.py` ships a ready-to-paste template for each, and
`references/app-integration.md` has the per-app gotchas in full.

## Building a Filename

```python
from build_name import build

name = build(
    show="un-ff25", seq="ib", shot="0100",
    type_="matt", instance="01",      # → matt01
    vendor="dd", rev=3,               # → v003
    description="hard-premult",
    frame=1001, ext="exr",
)
# → 'un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr'
```

The builder applies the spec rules automatically: pads revisions and frames, validates the type code, rejects whitespace and forbidden characters, and omits the frame for multi-frame extensions.

## Parsing & Validating

```python
from parse_name import parse
from validate_name import validate, validate_detailed

parse("un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr")
# → {'show': 'un-ff25', 'seq': 'ib', 'shot': '0100', 'type': 'matt',
#    'instance': '01', 'vendor': 'dd', 'rev': 3, 'alternate': None,
#    'camera': None, 'description': 'hard-premult', 'spec_version': None,
#    'frame': 1001, 'ext': 'exr'}

ok, reasons = validate("un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr")
detail = validate_detailed("...")
detail["ok"], detail["reasons"], detail["warnings"]
```

`validate` returns **reasons** (spec violations — the file is non-compliant) and `validate_detailed` also returns **warnings** (legal but suspicious, e.g. a vendor code that collides with a real studio). A warning does not fail the file.

On the command line:

```bash
$ python3 scripts/validate_name.py un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr
OK

$ python3 scripts/validate_name.py "un-ff25 ib 0100 matt dd v001.1001.exr"
FAIL
  - whitespace not allowed (spec §3.1)
```

## One-Shot Recipes

### Recipe 1 — Naming a matte output in Nuke for shot 0100, revision 3

```
un-ff25_ib_0100_matt01_dd_v003_hard-premult.####.exr
```

In the Write node: paste the pattern with `####` for frame padding, set the extension to `.exr`, and set `file type` to `exr` (not the protocol prefix) when shipping outside Nuke.

### Recipe 2 — Generating names for a folder of mattes

```python
from build_name import build
from pathlib import Path

types = ["hard", "soft", "garbage", "key", "core", "edge", "roto-subject"]
for t in types:
    fname = build(
        show="un-ff25", seq="ib", shot="0100", type_="matt", instance="01",
        vendor="dd", rev=3, description=f"{t}-premult",
        frame=1001, ext="exr",
    )
    Path(f"./{fname}").touch()   # placeholder for testing
```

### Recipe 3 — Auditing a folder

```bash
$ python3 scripts/audit_folder.py /path/to/shots
```

Iterates the files, classifies each as plate / matte / comp / render / other, reports breakage and warnings. Exit code is the number of broken files, so it drops straight into CI.

### Recipe 4 — Photoshop and Blender

Both are covered in `references/app-integration.md`, which has the exact menu
paths, the layer-naming rules, and the alpha gotchas. The short version:

- **Photoshop** — rename the layers to their matte type (`hard-premult`,
  `soft-premult`, `garbage`), then export. For review PNGs use **Save for Web
  (Legacy)** with **PNG-24, Transparency on, Matte: None**; any other matte
  colour premultiplies the alpha permanently.
- **Blender** — enable the Cryptomatte passes in `View Layer > Passes`, write
  OpenEXR Multilayer 32-bit ZIP, and set the File Output path to
  `//un-ff25_ib_0100_matt01_dd_v003_crypto-asset.####.exr`. The Cryptomatte
  token goes in the description; the layer naming inside the EXR is Blender's,
  and uses a dot where the filename uses a dash.

## Common Pitfalls

1. **Using underscores inside the description.** The description is a single field: `hard-premult`, not `hard_premult`. Underscore is the token separator — a description containing one breaks the parse. The spec's own prose is explicit that the dash is "effectively white space inside the field".
2. **Padding inconsistencies.** `v3` next to `v003` next to `v0003` sort differently. **Pick the widest padding you will need for the whole show and stick to it.** Same for the frame number.
3. **Spaces in filenames.** They break parsers and break shells. Replace with `-` inside a field, `_` between fields. Never with a literal space.
4. **Frame number on a `.mov`.** MOVs contain many frames; the frame token does not apply. Omit it. `0042.mov` makes every tool angry.
5. **Instance collision.** `matt01` should mean "the first matte of this type" for the entire production, not per artist. Two artists both writing `matt01` leave the ingest tool unable to tell them apart.
6. **Fabricating vendor codes.** The vendor code identifies who made the file *for delivery*. Inventing a code that collides with a real studio (`dd`, `ilm`, `fr`) is a known foot-gun; the validator flags it as a warning for exactly this reason.
7. **Premult flag omission.** When shipping a matte plus a beauty, the premult state must be flagged in the description of **both** files. A beauty `beauty-premult` with an unflagged matte is ambiguous and gets unpremultiplied twice downstream.
8. **Description drift.** `fog` on Monday, `foggy` on Friday, `smoke` on the next show. Pick one and freeze it. Most pipeline bugs come from description drift, not from the structured tokens.
9. **Trusting the spec's examples for the grammar.** They disagree with the spec's own syntax block on the description's separator *and* its position. The normative form is in §3.2; see §The description above for what the tooling accepts.

Per-app gotchas — Nuke's protocol prefixes, Photoshop's matte colour, Blender's Cryptomatte layer names, Resolve's project library — are in `references/app-integration.md`.

## Verification Checklist

Before you call a filename done:

- [ ] All six required tokens present, in order, with the right padding (4-character show, 4-digit shot, 3-digit revision minimum)
- [ ] Type code is in the controlled vocabulary (`scripts/validate_name.py` checks this)
- [ ] No whitespace anywhere
- [ ] Underscores between every token, present even when a token is empty
- [ ] Dots only before the frame number and the extension
- [ ] Frame number present iff the file is a single-frame format; absent for `.mov` and other workfiles
- [ ] Frame padding matches the project convention (≥4 digits)
- [ ] Description uses dashes, not underscores, and matches what the rest of the show calls the same thing
- [ ] Vendor code is real if shipping externally; omitted or neutral if internal
- [ ] Matte files carry the premult flag when shipped with a paired beauty

## Reference Files & Sources

**Primary source** — *VFX Image Sequence Naming*, TR-VFX-IS v1.0, June 23 2020, ETC@USC / MovieLabs (chair Horst Sarubin, Universal; co-chair Erik Weaver, ETC; executive editor Craig Seidel, MovieLabs). Digested in `references/etc-image-sequence-spec.md`, original PDF in `references/etc-image-sequence-spec-v1.0.pdf`. Online: <https://movielabs.com/prodtech/sdw/vfx/ETC-ImageSequenceNaming-v1.0-063020-FINAL.pdf>

**References**

- `references/etc-image-sequence-spec.md` — a structured digest of the full TR-VFX-IS spec: every parameter definition, the controlled vocabulary, and the worked examples transcribed from the PDF.
- `references/etc-image-sequence-spec-v1.0.pdf` — the original specification, for offline reference.
- `references/controlled-vocabulary.md` — the exhaustive image-type table, vendor codes, show/sequence/shot conventions, and the file-extension list.
- `references/matte-types.md` — the matte deep-dive: every type, the premult rules, cryptomatte specifics, and per-app delivery notes.
- `references/app-integration.md` — the per-app mechanics: padding syntax, extension slot, and the gotchas for Nuke, Photoshop, Blender, Resolve, After Effects and Houdini.

**Tooling**

- `scripts/build_name.py` — programmatic builder (`build(...)` → str).
- `scripts/parse_name.py` — programmatic parser (`parse(str)` → dict).
- `scripts/validate_name.py` — spec validator, with reasons and warnings.
- `scripts/audit_folder.py` — folder auditor (CLI; exit code = broken file count).
- `scripts/app_presets.py` — output templates per app.
- `scripts/test_smoke.sh` — the smoke suite; its fixtures are the spec's own examples.
- `scripts/check_examples.sh` — re-validates every filename printed in the docs.

**Elsewhere**

- [VES Transfer Specification](https://vestransferspec.org/) — the controlled vocabulary for image types.
- [MovieLabs Common Metadata](https://movielabs.com/md/md/) — the broader metadata model this naming sits inside.
- [Digital Cinema Naming Conventions (ISDCF)](https://isdcf.com/dcnc/) — the delivery convention it descends from.
- [Nuke Write-node reference](https://learn.foundry.com/nuke/current/content/comp_environment/rendering/output_write_nodes.html) — frame-padding conventions.
- [Blender File Output node](https://docs.blender.org/manual/en/latest/compositing/types/output/file_output.html) — `###` syntax, multilayer EXR.
- [Netflix VFX Plate Naming Best Practices](https://partnerhelp.netflixstudios.com/hc/en-us/articles/360055781274) — a terrain reference for `PL##` / `BG##` / `FG##` instance tokens, compatible with the spec.
