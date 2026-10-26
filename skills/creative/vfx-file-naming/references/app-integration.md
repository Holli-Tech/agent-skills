# App Integration

How each DCC generates or interprets a VFX filename. The grammar itself is
app-agnostic — only the mechanics differ.

## Nuke

- **Where**: Write node → `file` knob. Use `####` for frame padding.
- **Gotcha**: set the `file type` knob to a literal extension (`.exr`), **not** a
  protocol prefix (`exr://`). Protocol prefixes are Nuke-specific and other
  applications cannot resolve them.
- Set `colorspace` to match the pipeline (typically linear or sRGB).
- Enable `read file` on the Write node to verify the render after the fact.

```
un-ff25_ib_0100_matt01_dd_v003_hard-premult.####.exr
```

Nuke scripts are workfiles: `.nk`, no frame token.

## Photoshop

- **Where**: `File > Export > Layers to Files` — the layer name becomes the
  output filename. `File > Export > Save for Web (Legacy)` for review PNGs.
- **Gotcha**: layer names with spaces or special characters get auto-stripped.
  Rename the layers to their matte type first: `hard-premult`, `soft-premult`,
  `garbage`, `key`, `core`, `edge`.
- Layer names must contain only `[a-zA-Z0-9-]` — no spaces, no underscores.
- For a PNG with transparency, use **PNG-24, Transparency on, Matte: None**.
  Any other matte colour premultiplies the alpha permanently and it cannot be
  recovered.
- PSD is a workfile: `.psd`, no frame token.

## Blender

- **Where**: File Output node (Compositor) — `###` for frame padding; or Output
  Properties (Render) for a full frame sequence.
- **Gotcha**: `//` at the start of the path is relative to the `.blend` file.
  Use an absolute path when a script is shared across machines.
- For Cryptomatte, enable the passes in `View Layer > Passes` (Cryptomatte
  Object / Material / Asset) and write OpenEXR Multilayer, 32-bit float, ZIP.
- The EXR **layer** names use a dot (`ViewLayer.CryptoAsset00`); the **file**
  name uses a dash. They are not the same thing and the Cryptomatte node in
  Nuke reads the layer name, not the filename.
- `.blend` is a workfile: no frame token.

## DaVinci Resolve

- **Where**: the Deliver page → render settings → custom name, using Resolve's
  `$Token` variables. Projects export as `.drp` (project), `.dra` (project +
  media) and `.drt` (a single timeline).
- **Gotcha**: Resolve does **not** save a project as a loose file next to the
  footage. Projects live inside a **Project Library** (a database), so the
  naming convention applies to the rendered image sequence, not to the project
  file.
- For a Power Window or Qualifier matte exported from the Color page, set the
  type to `matt` and the description to `pw-<n>` or `qualifier-<n>`.

## After Effects

- **Where**: Output Module → Name Template. `[compName]_#####` for frame
  padding (`[#####]` for 5 digits).
- **Gotcha**: same template syntax as Nuke, same `####` vs `%05d` distinction.
- For a Roto Brush matte, render as a PNG sequence with **Matte: None**, and
  leave the alpha interpretation as *Straight*.
- `.aep` is a workfile: no frame token.

## Houdini

- **Where**: a COP or Render Output node. `$F4` for 4-digit frame padding,
  `$F5` for 5.
- Set the COP to write OpenEXR with ZIP compression for matte review.

## Round-trip checklist per app

| App | Frame padding | Extension slot | Workfile extension |
|---|---|---|---|
| Nuke | `####` | `.exr` in the `file` knob | `.nk` |
| Photoshop | n/a (still) | export preset | `.psd` |
| Blender | `###` | `.exr` | `.blend` |
| DaVinci Resolve | `$Token` based | custom name | `.drp` / `.dra` / `.drt` |
| After Effects | `[####]` | output module | `.aep` |
| Houdini | `$F4` | `.exr` | `.hip` |
