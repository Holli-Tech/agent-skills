# Controlled Vocabulary

The complete token vocabulary for the ETC@USC / MovieLabs VFX Image Sequence Naming spec (TR-VFX-IS v1.0), plus the conventions this skill standardises on top of it (matte types, premult flags, vendor codes).

## Image Type Codes (`<type-name>`)

From spec §2.5, aligned with the VES Transfer Specification.

### Plates — inputs to VFX (§2.5.1)

| Code | Name | Use |
|---|---|---|
| `mp` | Main Plate | Only one element required to produce the final VFX work |
| `bg` | Background plate | Work requiring multiple elements; carries layer identification (`BG`, `BG02`) |
| `fg` | Foreground plate | Work requiring multiple elements; carries layer information (`FG12`) |
| `el` | Element plate | Isolated elements of the shot, partial composites in multi-vendor shots, rotoscoped elements, CG elements delivered at production's request |
| `cp` | Clean Plate | To be used for cleanup work |
| `rg` | Reference Plate | Such as a lighting reference |

`fg` and `el` overlap — where ambiguous, the choice is user preference.

### Other inputs / outputs (§2.5.2)

| Code | Name | Use |
|---|---|---|
| `anim` | Animation | Version for review — playblast, or animation over green for editorial to comp |
| `comp` | Comp | Composited VFX shots |
| `cnpt` | Concept | |
| `FINAL` | Final comp | Special designation for the delivered comp |
| `layo` | Layout | Versions generally sent for environment approval |
| `ldev` | Look dev | |
| `matt` | Mattes and masks | Any matte, mask, alpha, garbage, roto, key output — see §Matte descriptions below |
| `prev` | Pre vis | |
| `prox` | Proxy | Definition provided by user |
| `pstv` | Post vis | |
| `repo` | Repositioning | Sent for editorial approval |
| `spfx` | Effects pass | Can also be submitted as a playblast, or animation over green for editorial to comp |
| `test` | Test shots | Slap comps |
| `time` | Retime | Approvals sent for editorial approval |
| `vcam` | Virtual camera | |
| `other` + `<custom-code>` | Custom | Any category not addressed by the spec. Example: `other-magic` |

**Instance number**: an optional 2-digit zero-padded number attaches directly to the type code, no separator — `matt01`, `bg02`, `el12`. A different instance is a **distinct plate**, not a new version.

**Case**: the vocabulary is lower case except `FINAL`. The spec's §3.1 prefers lower case throughout and says case must not be used to distinguish terms.

## Matte Descriptions (`<identifying-description>` when `<type>` = `matt`)

The spec gives mattes a single type code (`matt`) and leaves the identifying description open. These are the values this skill standardises.

### By purpose

| Description | Matte type | Notes |
|---|---|---|
| `hard` | Hard matte | Binary alpha, silhouette only, no soft edge |
| `soft` | Soft matte / alpha | Grayscale alpha with anti-aliasing |
| `roto` | Roto matte | Frame-by-frame roto. Append the subject: `roto-subject`, `roto-hair` |
| `garbage` | Garbage matte | Cuts out unwanted elements (mics, booms, crew) |
| `key` | Key matte | Colour-key output (Primatte, Keylight, IBK…) |
| `core` | Core matte | Inner key — preserves hair, edges, fine detail |
| `edge` | Edge matte | Holds the transition zone only |
| `clean` | Clean plate | Repaint / paint-fix plate (often paired with a `cp` plate) |
| `crypto-object` | Cryptomatte — object | ID-matte by object (Blender Cycles, Arnold, VRay) |
| `crypto-material` | Cryptomatte — material | ID-matte by material |
| `crypto-asset` | Cryptomatte — asset | ID-matte by asset |
| `pw-<n>` | Power Window matte | DaVinci Resolve power-window export (n = window index) |
| `qualifier-<n>` | Qualifier matte | DaVinci Resolve qualifier export |

### Premultiplication flag

When the matte ships in a file separate from its beauty, the description carries the premult state of the RGB channels. When the matte is a layer in a multilayer EXR alongside the beauty, the flag describes the **matte layer's** RGB.

| Suffix | Meaning |
|---|---|
| `-premult` | RGB premultiplied (RGB includes the alpha; divide by alpha to unpremultiply) |
| `-unpremult` | RGB straight / unpremultiplied (full colour regardless of alpha) |
| `-premulrsa` | Premultiplied, RGB pre-divided by alpha (rare, Resolve-centric) |

Combine: `hard-premult`, `soft-unpremult`, `roto-subject-premult`, `garbage-unpremult`, `crypto-object-premult`.

### Pairing with a beauty

Both files carry the same revision, and the matte description records the parent when there is one:

```
un-ff25_ib_0100_mp_dd_v023.1001.exr            # the parent plate, revision 23
un-ff25_ib_0100_matt_dd_v001_mp-v023.1001.exr   # the matte that belongs to it
```

The spec's own note for this pair: "The reference to the main plate (i.e., parent) is in the description field."

## Vendor Codes (`<vendor-code>`)

Two alphanumeric characters, assigned by the production VFX department. The spec's examples: `dd` (Digital Domain), `ilm` (Industrial Light and Magic).

Common codes seen in the wild — **always confirm with the production**, they are not standardised:

| Code | Vendor |
|---|---|
| `dd` | Digital Domain |
| `ilm` | Industrial Light & Magic |
| `fr` | Framestore |
| `dneg` | DNEG |
| `weta` | Weta FX |
| `mpc` | MPC |
| `sp` | Sony Pictures Imageworks |
| `rsi` | Rising Sun Pictures |
| `lpi` | Lucasfilm / Industrial Light internal |
| `spi` | Sony Pictures Imageworks |

**For internal workfiles**: omit the slot or use a neutral code. The vendor code identifies who made the file *for delivery*; inventing a code that collides with a real studio is a known foot-gun, which is why the validator flags known studio codes as a warning.

## Identifying Description Conventions

The description slot is free text, with hard constraints:

- **Only** `[a-zA-Z0-9-]`. No underscores, no spaces, no other punctuation.
- **Words separated by `-`**, not `_`. The dash is "effectively white space inside the field".
- **Stable across the production**. If you call it `fog-removal` on Monday, do not call it `smoke-cleanup` on Friday for the same operation. Drift is the number-one cause of pipeline breakage.

Good: `mp-v023`, `old-age-dom`, `hair-line`, `fog-removal`, `bg-extension`, `ice-charger`.

Bad: `fog_removal` (underscore), `Fog Removal` (uppercase + space), `fog.removal` (the dot is reserved for frame and extension).

## Show ID Conventions

`<showid>` is 4 alphanum characters, optionally prefixed by a 2-character studio/franchise, joined with a **dash**.

| Code | Show |
|---|---|
| `ff25` | Fast and Furious 25 |
| `solo` | Solo |
| `rasp` | Rasputin (Iron Man 3 codename) |
| `un-ff25` | Fast and Furious 25, Universal (studio prefix) |
| `sw-rasp` | Rasputin, Star Wars franchise |
| `gotr-s08e007` | Game of Thrones S8E7 (episodic) |
| `hb-gotr-s08e007` | Game of Thrones S8E7, HBO (episodic + studio) |

The studio prefix exists for one reason: two studios might pick the same `<show>` value. Use it only when there is a real collision risk.

## Sequence Codes

2–4 alphanum, OR one of the portion designators.

### Regular sequences

2–4 characters. Examples: `sb` (Stone Ball), `ib`, `sc` (Scooter Chase), `CHAS`.

### Portion designators

| Code | Meaning |
|---|---|
| `show` | The complete show |
| `act<n>` | An act |
| `reel<n>` | A reel |
| `part<n>` | A part of the show |

`<n>` uses the worst-case digit count, zero-padded: 5 reels → `reel1`..`reel5`; 20 parts → `part01`..`part20`.

Do not start a regular sequence code with `show`, `act`, `reel` or `part` — those namespaces are reserved.

## Shot Numbers (`<vfx-shot>`)

4 digits, zero-padded. Starts at `0100`.

| Code | Meaning |
|---|---|
| `0000` | The concept of "shot" does not apply — a model, an effect spanning shots, work for a whole sequence, act or show |

## Revision Codes (`<revision-code>`)

`v` + at least 3 digits, consistent width across the production.

| Width | Use when |
|---|---|
| `v001`–`v999` | Up to 999 iterations expected (the usual case) |
| `v0001`–`v9999` | Beyond 999 iterations (long-running asset or series) |

Never mix widths in the same project.

## Frame Numbers (`<frame-number>`)

≥4 digits, zero-padded, consistent width. Present for single-frame files, absent for multi-frame files.

| Width | Use when |
|---|---|
| `1000`–`9999` | Up to 9999 frames |
| `01000`–`99999` | Beyond 9999 (feature-length, long-form TV) |

The spec's own examples use 1000, 1001, 1002 for previz sequences and 1001 for plates.

## File Extensions

Conventional only. The validator accepts:

| Extension | Format | Frame token |
|---|---|---|
| `.exr` | OpenEXR (single frame) | required |
| `.dpx` | DPX (single frame) | required |
| `.png` | PNG (single frame) | required |
| `.tif` / `.tiff` | TIFF (single frame) | required |
| `.tga` | TGA (single frame) | required |
| `.jpg` / `.jpeg` | JPEG (single frame, lossy — avoid for VFX) | required |
| `.psd` / `.psb` | Photoshop document | required |
| `.mov` | QuickTime (multi-frame) | OMIT |
| `.mp4` | MPEG-4 (multi-frame) | OMIT |
| `.nk` | Nuke script (workfile) | OMIT |
| `.blend` | Blender file (workfile) | OMIT |
| `.drp` / `.drt` / `.dra` | DaVinci Resolve project files | OMIT |
| `.aep` / `.aepx` | After Effects project | OMIT |
| `.ma` / `.mb` | Maya ASCII / binary | OMIT |
| `.hip` / `.hiplc` / `.hipnc` | Houdini scene | OMIT |
| `.uasset` | Unreal Engine asset | OMIT |

The frame token is required for single-frame image formats and omitted for multi-frame containers or workfiles. Putting `0042.mov` on a multi-frame file fails the validator.
