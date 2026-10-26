# vfx-file-naming

A file-naming grammar for VFX image sequences, anchored in the **ETC@USC / MovieLabs "VFX Image Sequence Naming"** specification (TR-VFX-IS v1.0, June 2020) and aligned with the **VES Transfer Specification** vocabulary.

## What's here

```
SKILL.md                                # core grammar (the agent-facing skill)
references/
  etc-image-sequence-spec.md            # structured digest of the ETC@USC spec
  etc-image-sequence-spec-v1.0.pdf      # the original spec (offline copy)
  controlled-vocabulary.md              # full image-type / vendor / matte vocabulary
  matte-types.md                        # deep-dive on every matte variant
scripts/
  build_name.py                         # programmatic filename builder
  parse_name.py                         # filename → structured dict
  validate_name.py                      # filename → OK / FAIL, with reasons and warnings
  audit_folder.py                       # folder auditor, reports breakage
  app_presets.py                        # ready-to-paste output templates per app
  test_smoke.sh                         # 58-case smoke test suite
  check_examples.sh                     # validates every filename in the docs
```

## Run the tests

```bash
cd scripts/
bash test_smoke.sh
```

Expected: **58 passed, 0 failed**.

The fixtures are the specification's own worked examples, transcribed from the PDF, so the suite doubles as a conformance check against the primary source.

A second script checks that every filename printed in the documentation still validates — the docs and the implementation cannot drift apart:

```bash
bash check_examples.sh
# → Found 39 candidate filename examples in the docs
# → 39/39 examples validate
```

## Use the scripts

```bash
# Build a spec-compliant name
python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt \
    --instance 01 --vendor dd --rev 3 --description hard-premult \
    --frame 1001 --ext exr
# → un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr

# The spec's examples join the description with a dash; ask for that form
python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt \
    --vendor dd --rev 1 --description mp-v023 --frame 1001 --ext exr --desc-sep -
# → un-ff25_ib_0100_matt_dd_v001-mp-v023.1001.exr

# Parse a name back into a dict
python3 parse_name.py un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr

# Validate (exit 0 = compliant, 1 = not)
python3 validate_name.py un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr

# Audit a folder (exit code = number of broken files)
python3 audit_folder.py /path/to/shots --json
```

## As a Python library

```python
from build_name import build
from parse_name import parse
from validate_name import validate, validate_detailed

# Build
name = build(show="un-ff25", seq="ib", shot="0100", type_="matt", instance="01",
             vendor="dd", rev=3, description="hard-premult",
             frame=1001, ext="exr")

# Parse
tokens = parse(name)
# {'show': 'un-ff25', 'seq': 'ib', 'shot': '0100', 'type': 'matt',
#  'instance': '01', 'vendor': 'dd', 'rev': 3, 'alternate': None,
#  'camera': None, 'description': 'hard-premult', 'spec_version': None,
#  'frame': 1001, 'ext': 'exr'}

# Validate — reasons are failures, warnings are advisory
ok, reasons = validate(name)
assert ok, reasons
detail = validate_detailed(name)
```

## The grammar in one line

```
<show>_<seq>_<shot>_<type>_<vendor>_v<rev>{_<description>}.<frame>.<ext>
```

```
un-ff25_ib_0100_matt01_dd_v003_hard-premult.1001.exr
```

*Show `un-ff25` (Universal's Fast and Furious 25), sequence `ib`, shot `0100`, matte #01, made by `dd` (Digital Domain), revision 3, a hard premultiplied matte, frame 1001, OpenEXR.*

## Sources

- **Primary** — *VFX Image Sequence Naming*, TR-VFX-IS v1.0, June 23 2020, ETC@USC / MovieLabs. PDF in `references/`. Online: <https://movielabs.com/prodtech/sdw/vfx/ETC-ImageSequenceNaming-v1.0-063020-FINAL.pdf>
- **VES Transfer Specification** — <https://vestransferspec.org/>
- **MovieLabs Common Metadata** — <https://movielabs.com/md/md/>
- **Digital Cinema Naming Conventions (ISDCF)** — <https://isdcf.com/dcnc/>
