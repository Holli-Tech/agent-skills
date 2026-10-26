# ETC@USC / MovieLabs — VFX Image Sequence Naming (TR-VFX-IS v1.0)

Structured digest of the **primary source** for this skill: the ETC@USC Adaptive Production VFX Working Group white paper, *VFX Image Sequence Naming*, ref `TR-VFX-IS v1.0`, dated **June 23 2020**, chaired by Horst Sarubin (Universal), co-chair Erik Weaver (ETC), with MovieLabs as editorial liaison (Craig Seidel).

Full PDF (1.4 MB, 19 pages): <https://movielabs.com/prodtech/sdw/vfx/ETC-ImageSequenceNaming-v1.0-063020-FINAL.pdf> — mirrored in `etc-image-sequence-spec-v1.0.pdf` next to this file.

> **Note on transcription.** The spec's example filenames are set in an embedded font that plain text extraction cannot read. Every literal example quoted below was transcribed by rendering the PDF pages to images and reading them. Where the spec contradicts itself, the discrepancy is called out rather than silently resolved.

---

## 1. Scope & Principles

The spec defines a method for naming image sequences used in VFX review and delivery — primarily plates and comps delivered as OpenEXR or DPX frames. The same grammar extends to virtually any image sequence: pre-vis, lookdev, anim, post-vis, retimes, test shots, mattes, proxies.

**Guiding principles** (§Executive Summary):

> - The data and image sequences should be delivered in a format, layout, and storage system that can be easily understood and ingested regardless of production-specific knowledge.
> - Standardized naming conventions and development of best practices for data handling should be enacted as the data and assets are generated.
> - These specifications should allow for easy parsing and ingestion while remaining agnostic.

**Inheritance / alignment**: consistent with the **VES Transfer Specification** [VES-TS], and descends from the **Digital Cinema Naming Conventions** [DCNC] tradition (ISDCF). Identifier concepts align with the broader **MovieLabs Common Metadata** `md:` namespace [MD].

---

## 2. Parameter Definitions

### 2.1 Version Information (`<spec-version>`)

Identifies the version of the specification used to encode, so a parser can know how to interpret the name.

```
<spec-version> = "sv" + <major-version> + "." + <minor-version>
```

- `<major-version>`: two alphanumeric digits, leading zeros if necessary.
- `<minor-version>`: two alphanumeric digits, leading zeros if necessary.

Spec's examples: version 1.0 → `sv01.0`, version 1.2 → `sv01.2`.

> **Spec inconsistency.** The prose says the minor version is *two* digits; both worked examples use *one* (`sv01.0`, `sv01.2`). This skill's tooling accepts one or two digits.

### 2.2 Show ID (`<showid>`)

An abbreviated code uniquely identifying a feature, episode or other work. The term "show" is used broadly to cover what is often called "title" or "project". Must be unique across all titles.

**Individual work** (features, shorts):

```
<showid> = {<studio-or-franchise> + "-" +} <show>
```

- `<show>`: a 4-character alphanumeric identifier.
- `<studio-or-franchise>`: optional alphanumeric identifier, **2 characters recommended**, used only where the same `<show>` value might collide across studios.

Examples: `ff25` (Fast and Furious 25), `solo` (Solo), `rasp` (Rasputin — the codename for Iron Man 3). With a studio/franchise: `sw-rasp` (Star Wars), `un-ff25` (Universal).

**Episodic**:

```
<showid> = {<studio-or-franchise> + "-" +} <production-sequence>
<production-sequence> = <series> + "-" + "s" + <season> + "e" + <episode>
```

- `<series>`: a 4-character alphanumeric identifier of the series.
- `<season>`: 2 numeric digits, leading zeros.
- `<episode>`: 3 numeric digits, leading zeros.

Examples: `gotr-s08e007` (Game of Thrones S8E7), `hb-gotr-s08e007`.

> **Spec note.** The spec's own prose flags `got` (three characters) as invalid because `<series>` must be four; the examples use the four-character `gotr`.

> **The dash is meaningful.** "Although the Show ID can have multiple parts it is still one field. Because it is one field, parts are separated by dashes ('-') which are effectively white space inside the field." The same convention governs the identifying description.

### 2.3 VFX Sequence (`<vfx-sequence>`)

An abbreviation of the sequence name — generally an easily remembered description of a sequence in the film. Designated by the production VFX staff, typically organised by the unity of the VFX work.

- 2–4 alphanumeric characters, e.g. `sb` for the "Stone Ball" sequence in *Raiders of the Lost Ark*.
- Or one of the following, for work applying to a well-defined portion of the whole:

| Code | Meaning |
|---|---|
| `show` | the complete show |
| `act<n>` | an act |
| `reel<n>` | a reel |
| `part<n>` | a part of the show |

`<n>` must use the same number of digits for all show-related deliveries: 5 reels → 1 digit; 20 parts → 2 digits, zero-padded.

> One must avoid using sequence values starting with `show`, `act`, `reel` or `part` unless they are one of those designators.

### 2.4 VFX Shot (`<vfx-shot>`)

A 4-digit number, unique within the VFX sequence. Organises shots sequentially.

- `0000` is **reserved**: used when the concept of "shot" does not apply — a model, an effect that spans shots, work for a whole sequence, an act, or the entire work. Examples: `sb_0000` (entire Stone Ball sequence), `act1_0000` (all of Act 1), `show_0000` (the entire work).
- Otherwise, numbering starts at `0100`. "Shot is 1, but by convention numbering starts at 100."

### 2.5 Image Type (`<type-name>` + optional `<instance-number>`)

Indicates the purpose of the image sequence. Format:

```
<type-name> + {<instance-number>}
```

- `<instance-number>`: optional 2-digit zero-padded number differentiating image sequences. **A different instance number is a distinct plate, not a different version.** e.g. `EL01` might be fire and `EL02` might be smoke.

**Plates — inputs to VFX** (§2.5.1, values consistent with VES-TS):

| Code | Meaning |
|---|---|
| `mp` | Main Plate — only one element required to produce the final VFX work |
| `bg` | Background plate — for work requiring multiple elements, carries layer identification (`BG`, `BG02`) |
| `fg` | Foreground plate — for work requiring multiple elements, carries layer information (`FG12`) |
| `el` | Element plate — isolated elements of the shot, partial composites in multi-vendor shots, rotoscoped elements, CG elements delivered at production's request |
| `cp` | Clean Plate — to be used for cleanup work |
| `rg` | Reference Plate — such as a lighting reference |

> There is some redundancy between `fg` and `el`. Where ambiguous, the choice is user preference.

**Other inputs / outputs** (§2.5.2):

| Code | Meaning |
|---|---|
| `anim` | Animation version for review — playblast, or animation over green for editorial to comp |
| `comp` | Compositited VFX shots |
| `cnpt` | Concept |
| `FINAL` | Special designation for final comp |
| `layo` | Layout versions, generally sent for environment approval |
| `ldev` | Look dev |
| `matt` | Mattes and masks |
| `prev` | Pre vis |
| `prox` | Proxy (definition provided by user) |
| `pstv` | Post vis |
| `repo` | Repositioning, sent for editorial approval |
| `spfx` | Effects pass — can also be submitted as a playblast, or animation over green for editorial to comp |
| `test` | Test shots, slap comps |
| `time` | Retime approvals, sent for editorial approval |
| `vcam` | Virtual camera |
| `other` + `<custom-code>` | Other custom category not addressed here. `<custom-code>` is any code defined by parties exchanging data. Example: `other-magic` |

> For the types given, the controlled vocabulary **should** be used. For types not anticipated by the specification, a custom term is acceptable.

### 2.6 Identifying Description (`<identifying-description>`)

Optional context for the image sequence — what has been done in the latest pass, the subject of the image, a specific effect performed, or non-show reference material.

- Shall contain **only alphanumeric characters and dash** (`-`).
- Words are separated by the dash, which "is intended for words to be separate by the dash" — the same "effectively white space inside the field" convention as the Show ID.
- **Must stay consistent throughout the production.** If something is labelled `doms-beard`, that naming must remain constant — do not sometimes use `doms-beard` and other times use `doms-facialhair` or `torretos-beard`.

### 2.7 Vendor Code (`<vendor-code>`)

Two alphanumeric characters uniquely identifying a vendor, typically assigned by the production VFX department. Should be encoded for readability. Spec examples: `dd` (Digital Domain), `ilm` (Industrial Light and Magic).

### 2.8 Revision Code (`<revision-code>`)

```
<revision-code> = "v" + <nnn>
```

- `<nnn>` is at least 3 numerals, always the same number of digits, padded with zeros. With 3 digits, revision 10 is `v010`; with 4 digits it would be `v0010`.
- Use the maximum number of digits needed for the production.

### 2.9 Alternate (`<alternate>`)

When multiple versions or variations of an image sequence exist (e.g. 4K and 6K plates) and must be told apart.

- Encoded as `a-` + a free identifier (e.g. `a-4k`, `a-6k`).
- **The primary (best) version does not include this field.**
- If only one version exists, the field is not needed.

### 2.10 Multi-Camera Reference (`<camera-label>`)

Associates images with cameras when more than one camera films simultaneously (stereo pair, camera array). Not used when only one camera is filming.

| Code | Camera |
|---|---|
| `L` | Left eye of a stereo pair |
| `R` | Right eye of a stereo pair |
| `C` | Centre camera |
| `N<n>` | Camera N — at least 1 alphanumeric character, zero-padded to a consistent width |

### 2.11 Frame Number (`<frame-number>`)

- At least 4 numeric digits, leading zeros, always the same number of digits across the production.
- **Present** when the file contains a single frame (DPX, OpenEXR).
- **Absent** when the file contains all frames (MOV, MP4).
- The spec's previz examples use 1000, 1001, 1002; the plate example uses 1001.

### 2.12 File Extension (`<file-extension>`)

The conventional extension for the file type. The spec's example: `exr` for an OpenEXR file. "File type is considered part of the file name."

---

## 3. File Name Encoding

### 3.1 General Syntax Rules (§3.1)

- **Only allowed characters**: alphanumeric and dash. No whitespace.
- **Metadata parameters are separated by an underscore** (`_`).
- **File type is considered part of the file name** — the extension follows a dot.
- **If a parameter is missing, the underscore is still present** as if the parameter were there. `{p1}_{p2}_{p3}` with `p2` missing encodes as `{p1}__{p3}`.
- **Use of all lower case is preferable.** Case shall be used consistently, so filename sorting works. Case shall not be used to distinguish terms. (`FINAL` is the one vocabulary entry printed in upper case.)
- **Filenames more than 255 characters should be avoided** (exFAT limit is 256, Linux is 255).
- There is a general trade-off between clarity and brevity; brevity often wins for filenames.

### 3.2 Full Syntax (§3.2)

```
<showid> + "_" +
<vfx-sequence> + "_" +
<vfx-shot> + "_" +
<image-type> + "_" +
<vendor-code> + "_" +
<revision-code> +
{ "_" + "a-<alternate>"}
{ "_" + <camera-reference>}
{ "_" + <identifying-description>}
{ "_" + <spec-version>}
{ "." + <frame-number>}
+ "." + <file-extension>
```

The convention can also be used for files that contain multiple frames (e.g. MOV); only in that case is the frame number omitted.

> **The spec's own inconsistencies about the description.** The spec does not agree with itself about where the identifying description goes or how it is separated:
>
> 1. **Separator.** The §3.2 syntax block puts an underscore before the description. Several §3.2.1 examples join it to the revision with a **dash** (`v001-fire`, `v001-mp-v023`), annotated "the use of dash because the description is one field". Other examples in the same section use an underscore (`v001_dom_beard`, `v020_ice-charger`).
> 2. **Position.** The §3.2 syntax block puts the description *after* the revision. But three §3.2.1 examples put it *before* the vendor:
>    ```
>    un-ff25_show_0000_ldev_dom-old-age_dd_v001.1000.exr
>    un-ff25_act1_0000_ldev_dom-old-age_dd_v001.1000.exr
>    un-ff25_sc_0000_ldev_dom-old-age_dd_v001.1000.exr
>    ```
>    i.e. `<type>_<description>_<vendor>_v<rev>` rather than `<type>_<vendor>_v<rev>_<description>`.
>
> This skill's tooling resolves it as follows:
>
> - The **builder emits the normative form** — description last, underscore-separated — and has a `--desc-sep -` flag for the dash variant.
> - The **parser accepts all of it**: underscore or dash separator, description before or after the vendor. Names copied from the specification parse correctly, which is the point.

### 3.2.1 Examples (§3.2.1)

Setup for all examples: show `ff25` (possibly `un-ff25`), sequence `ib`, shot `0100`, vendor `dd`, `.exr` extension, revision 1 unless stated.

**Background plates** (three frame sequences: 1000, 1001, 1002):
```
un-ff25_ib_0100_bg_dd_v001.1000.exr
un-ff25_ib_0100_bg_dd_v001.1001.exr
un-ff25_ib_0100_bg_dd_v001.1002.exr
```

**Fire and smoke element plates**:
```
un-ff25_ib_0100_el_dd_v001-fire.1000.exr
un-ff25_ib_0100_el_dd_v001-fire.1001.exr
un-ff25_ib_0100_el_dd_v001-fire.1002.exr
un-ff25_ib_0100_el_dd_v001-smoke.1000.exr
un-ff25_ib_0100_el_dd_v001-smoke.1001.exr
un-ff25_ib_0100_el_dd_v001-smoke.1002.exr
```

**Other image sequences** (one frame shown):

| Caption | Filename |
|---|---|
| Comp, revision 20 | `un-ff25_ib_0100_comp_dd_v020.1000.exr` |
| Concept, Dom's beard correction | `un-ff25_ib_0000_cnpt_dd_v001_dom_beard.1000.exr` |
| Ice charger concept that applies to all of Act 3 | `un-ff25_act3_0000_cnpt_ilm_v020_ice-charger.1000.exr` |
| Generic animation for the sub explosion, revision 20 | `un-ff25_ib_0000_anim_dd_v020_sub-explosion.1000.exr` |
| VFX ID for look dev and old age version of the character Dominic Toretto — used throughout the film | `un-ff25_show_0000_ldev_dom-old-age_dd_v001.1000.exr` |
| …was only meant for act one | `un-ff25_act1_0000_ldev_dom-old-age_dd_v001.1000.exr` |
| Where work was generic for a sequence in the film but not shot specific, the appropriate sequence code is used but still the generic number code — `SC` for "Scooter Chase" | `un-ff25_sc_0000_ldev_dom-old-age_dd_v001.1000.exr` |
| The main plate, version 23 | `un-ff25_ib_0100_mp_dd_v023.1001.exr` |
| The matte plate (type = `matt`) — revision 1, but refers to revision 23 of the main plate. The reference to the main plate (the "parent") is in the description field. *Note the use of dash because the description is one field.* | `un-ff25_ib_0100_matt_dd_v001_mp-v023.1001.exr` |
| If the matte is revised, the revision would be updated to `v002` | `un-ff25_ib_0100_matt_dd_v002_mp-v023.1001.exr` |

### 3.3 Directory Naming (§3.3)

**File naming is independent of directory path naming.** The file name remains the same regardless of whether some elements are redundant with the directory path.

Given the file `FF25_ib_0100_BG_dd_v020.1000`, the name remains the same in these two cases:
```
resource/ff25_ib_0100_bg_dd_v020.1000.exr
resource/ff25/ib_0100/bg/dd/v020/FF25_ib_0100_bg_dd_v020.1000.exr
```

The following is **incorrect** — the directory carries information the filename does not:
```
resource/ff25/ib_0100/bg/dd/v020/1000.exr
```

---

## 4. Spec Metadata

- **Reference**: TR-VFX-IS · **Version**: 1.0 · **Date**: June 23, 2020
- **Publisher**: Entertainment Technology Center at USC (ETC@USC) / MovieLabs
- **Working group**: ETC Adaptive Production VFX Working Group
- **Chair**: Horst Sarubin (Universal Pictures) · **Co-chair**: Erik Weaver (ETC@USC)
- **Executive Editor**: Craig Seidel (MovieLabs)
- **Status** (§1.6): Ready for implementation. Changes are expected to be backwards compatible.

**Normative references** (§1.4): OpenEXR File Layout (Kainz, 2013); SMPTE ST 268:2014 (DPX).

**Informative references** (§1.5): C4 Identification System (ETC, 2015); Digital Cinema Naming Conventions (ISDCF); EIDR; VES Transfer Specification.
