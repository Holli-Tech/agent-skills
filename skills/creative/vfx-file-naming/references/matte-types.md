# Matte Types — Deep Dive

Mattes are the highest-error category in VFX file naming because **several distinct types** share the same image-type code (`matt`) and the differences are easy to lose in a filename. This file is the deep-dive on each type, with per-app delivery notes (Photoshop, Nuke, Blender, DaVinci Resolve, After Effects).

The matte type goes in the **identifying description**, never in the structured slots. The convention this skill enforces is in `references/controlled-vocabulary.md`.

The spec's own example of the pairing (page 13 of TR-VFX-IS v1.0) is the canonical case:

```
un-ff25_ib_0100_mp_dd_v023.1001.exr            # the parent plate, revision 23
un-ff25_ib_0100_matt_dd_v001_mp-v023.1001.exr   # the matte that belongs to it
```

The spec annotates the second: *"The reference to the main plate (i.e., parent) is in the description field."* And when the matte is revised, its own revision bumps: `un-ff25_ib_0100_matt_dd_v002_mp-v023.1001.exr`.

## 1. Matte Taxonomy

```
                   matte
                     │
        ┌────────────┼─────────────┐
        │            │             │
   by shape      by purpose    by source
        │            │             │
   ┌────┴────┐    ┌───┴───┐    ┌────┴────┐
   │         │    │       │    │         │
 hard      soft  garbage  key  roto    cryptomatte
                     │    │
                    core  edge
```

| Type | Shape | Channel model | Common producer |
|---|---|---|---|
| Hard | Binary (0/1) | Straight alpha | Primatte, IBK, luma key |
| Soft / alpha | Grayscale | Straight or premultiplied | Keylight, roto with feather |
| Garbage | Typically hard | Straight | Manual paint, polyline shapes |
| Roto | Soft or hard | Straight | Nuke Roto, Mocha, Silhouette |
| Key | Soft | Straight | Primatte, Keylight, IBK |
| Core (inner key) | Soft | Straight | Keylight "core matte" output |
| Edge | Soft (narrow band) | Straight | Keylight "edge matte" output |
| Clean plate | RGB (no matte) | n/a | Paint-out, cleanup pass |
| Cryptomatte | ID-encoded | RGBA channel pair | Blender Cycles, Arnold, VRay, Renderman |

## 2. Hard Matte

**Definition**: binary alpha — pixels are either fully opaque or fully transparent. No anti-aliasing. Used for clean silhouettes where soft edges would be wrong (hard composites, paint fixes).

**Filename**: `un-ff25_ib_0100_matt01_dd_v001_hard-premult.1001.exr`

**Producer**: Primatte with no edge softening, IBK (Difference Key), luminance key with no feather, manual matte paint in Photoshop with no feather.

**Producer → Consumer**:
- **Nuke → Nuke**: works directly, often `ChannelMerge` or `Merge` with the `Stencil` operation.
- **Photoshop → Nuke**: read the PSD, use the layer as a matte via `Shuffle` (red → alpha).
- **Resolve → Resolve**: stays inside the project; no matte file needed.
- **After Effects → Nuke**: export as a PNG sequence with **Matte: None** (straight alpha).

**Common mistake**: shipping a "hard" matte that actually has a 1-pixel soft edge from anti-aliasing in the keyer. Document the edge in the description if it matters: `hard-aa1px`.

## 3. Soft Matte / Alpha

**Definition**: grayscale alpha with anti-aliased edges. The "normal" alpha — what you get from a properly feathered key.

**Filename**: `un-ff25_ib_0100_matt01_dd_v001_soft-premult.1001.exr`

**Producer**: any keyer with feathering enabled (Keylight default, Primatte with edge softening), roto with feather.

**Premult decision**: depends on what the downstream consumer needs. **Premult is the safer default** for VFX compositing (most comp nodes expect premultiplied input); unpremult is for re-keying or colour work.

## 4. Roto Matte

**Definition**: frame-by-frame rotoscoped silhouette, usually for a moving subject.

**Filename**: `un-ff25_ib_0100_matt01_dd_v001_roto-subject-premult.1001.exr`

The subject suffix is optional but encouraged when there are several roto mattes on one shot:
```
un-ff25_ib_0100_matt01_dd_v003_roto-subject-premult.1001.exr
un-ff25_ib_0100_matt02_dd_v003_roto-subject-hair-premult.1001.exr
```

**Producer**: Nuke Roto, Mocha Pro, Silhouette, After Effects Roto Brush.

**App-specific note**:
- **Nuke Roto**: set `output: alpha`, `premultiply: rgb`. Then a `Write` node. The premult setting in the node overrides the file's premult flag — keep them in sync.
- **Mocha → Nuke**: export as *Matte Clip* or *Shape Data*. Shape data imports as roto nodes; a matte clip imports as an image sequence (use this filename convention).
- **After Effects Roto Brush**: export the matte via `Layer > Track Matte`, then render as a PNG sequence with Matte: None.
- **Resolve**: no native roto, but a window or qualifier export can serve as a matte.

## 5. Garbage Matte

**Definition**: a matte that removes unwanted elements from a plate — microphones, booms, crew, lights, reflections. Usually applied on top of a key matte.

**Filename**: `un-ff25_ib_0100_matt01_dd_v001_garbage-premult.1001.exr`

**Producer**: hand-painted in Photoshop (one frame, propagated), painted in Nuke (RotoPaint), polyline shapes in Resolve.

**Important**: garbage mattes are usually applied via `Merge: Stencil` (Nuke) or the garbage-matte input (Resolve Delta Keyer). They rarely live as standalone alpha files in the pipeline; when they do, this convention applies.

## 6. Key Matte / Core Matte / Edge Matte

The tri-matte split from Keylight (and similar keyers):

| Matte | What it contains | Description |
|---|---|---|
| Key matte | The whole key — solid inside, transparent outside | `key` |
| Core matte | Inner key, preserves detail (hair, motion blur) | `core` |
| Edge matte | Holds the transition zone (semi-transparent pixels) | `edge` |

**Filename (paired)**:
```
un-ff25_ib_0100_matt01_dd_v003_key.1001.exr
un-ff25_ib_0100_matt02_dd_v003_core.1001.exr
un-ff25_ib_0100_matt03_dd_v003_edge.1001.exr
```

**Use**: combine the core (solid) with the edge (semi-transparent) for a high-quality composite that preserves detail without colour spill.

## 7. Clean Plate

**Definition**: a repainted version of the plate with the foreground element removed entirely. Used for paint-out and clean-up work.

**Filename** (two conventions):

1. As a **plate** (`cp` type): `un-ff25_ib_0100_cp_dd_v001.1001.exr` — when the clean plate replaces the plate in the delivery.
2. As a **matte** (`matt` type): `un-ff25_ib_0100_matt_dd_v001_clean.1001.exr` — when the clean plate ships alongside the original plate for the consumer to use as needed.

Convention 2 is more common in inter-vendor handoffs.

**Producer**: Nuke RotoPaint, Photoshop (paint-out layer), Flame/Inferno paint node.

## 8. Cryptomatte

**Definition**: an ID-based matte system where each pixel carries one or more object/material/asset IDs encoded into the RGBA channels. The downstream tool (Nuke Cryptomatte node, Fusion, After Effects plugin) lets the artist click a region and pull out a per-object matte.

**Three flavours** (Blender Cycles convention, used by most renderers):

| Flavour | Encodes | Description |
|---|---|---|
| Cryptomatte Object | Object IDs | `crypto-object` |
| Cryptomatte Material | Material IDs | `crypto-material` |
| Cryptomatte Asset | Asset IDs | `crypto-asset` |

**Filename**:
```
un-ff25_ib_0100_matt01_dd_v003_crypto-object.1001.exr
un-ff25_ib_0100_matt02_dd_v003_crypto-material.1001.exr
un-ff25_ib_0100_matt03_dd_v003_crypto-asset.1001.exr
```

**Inside the EXR** (Blender-specific, also applies to other renderers): the layer name is **dot-separated**, not underscore. Format:

```
<view-layer>.<CryptoVariant><NN>.<channel>
```

Examples:
```
ViewLayer.CryptoObject00.R
ViewLayer.CryptoAsset00.R
```

**Gotcha — Blender vs Nuke naming**:
- Blender exports the metadata key as `xxxx.CryptoObject` (with a dot).
- Nuke's Cryptomatte node expects the layer name `xxxx_CryptoObject` (with an underscore).
- **If the names do not match, the Cryptomatte node fails to load the manifest** and the artist gets a black matte.
- Workaround: the Cryptomatte node has a "Layer" knob where you can override the expected name to match what Blender exported.

The skill standardises the **filename** token (`crypto-object` / `crypto-material` / `crypto-asset`, lowercase, dash-separated). The internal EXR layer naming is renderer-specific and outside the skill's scope, but documented here so artists know what to look for.

## 9. Power Window / Qualifier Matte (Resolve)

DaVinci Resolve exports a power window (or qualifier) as a matte via "Export Matte" in the Color page. The exported image sequence has the window shape as white-on-black.

**Filename**:
```
un-ff25_ib_0100_matt01_dd_v003_pw-1.1001.exr        # power window 1
un-ff25_ib_0100_matt02_dd_v003_qualifier-1.1001.exr # qualifier 1
```

Multiple windows get distinct instance numbers (`matt01`, `matt02`, …) and live as separate `matt` instances.

## 10. Multichannel / Multilayer Mattes

When shipping several mattes in one EXR file (Nuke's standard):

**Option A — separate files** (preferred for inter-vendor delivery):
```
un-ff25_ib_0100_matt01_dd_v003_key.1001.exr
un-ff25_ib_0100_matt02_dd_v003_core.1001.exr
un-ff25_ib_0100_matt03_dd_v003_edge.1001.exr
```

**Option B — multilayer EXR** (preferred for an in-house pipeline):
- The filename uses one `matt` instance and one revision.
- Each matte is a layer in the EXR, named by type: `key`, `core`, `edge`.
- The description is the **dominant** matte type, or `multi` if there is no dominant one.

**Rule**: pick one or the other per delivery. Mixing them across deliveries breaks ingest tools.

## 11. Premultiplication — the full picture

The premult state is encoded in the description when:
- The matte ships in a file separate from the beauty, or
- The matte is the primary content of the file (not a layered extra).

For multilayer EXRs, the premult flag in the filename describes the **matte layer's** RGB, not the beauty.

| Flag | RGB state | Decode |
|---|---|---|
| `-premult` | RGB × alpha | To unpremult: divide RGB by alpha |
| `-unpremult` | RGB straight | Use as-is |
| `-premulrsa` | RGB pre-divided, alpha attached | Resolve-specific; treat as unpremult |

**Default for VFX deliverables**: `-premult`. Most comp nodes assume premultiplied input. If you ship unpremult, document it loudly in the description.

## 12. Round-Trip Audit Checklist

Before shipping a matte to a downstream artist:

- [ ] Type code is `matt` (not `comp`, `mp`, `el`…)
- [ ] Description carries the matte type (`hard`, `soft`, `key`, `core`, `edge`, `roto-<subject>`, `garbage`, `crypto-<variant>`, `clean`, `pw-<n>`, `qualifier-<n>`)
- [ ] Premult flag in the description (`-premult`, `-unpremult`, `-premulrsa`)
- [ ] Revision matches the paired beauty / plate (when shipped together)
- [ ] The parent plate's revision is recorded in the description, as the spec does (`mp-v023`)
- [ ] Frame padding matches the project convention
- [ ] Extension matches the channel model: EXR (single-frame alpha), PNG (single-frame alpha), MOV (rare, review only)
- [ ] EXR layer names follow the renderer convention (dot-separated) — independent of the filename
- [ ] No whitespace, no underscores in the description, no special characters
