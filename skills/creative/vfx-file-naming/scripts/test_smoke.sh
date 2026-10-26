#!/usr/bin/env bash
# vfx-file-naming skill — smoke test suite
#
# The filename fixtures in this suite are taken VERBATIM from the ETC@USC /
# MovieLabs "VFX Image Sequence Naming" specification (TR-VFX-IS v1.0), so the
# tests double as a conformance check against the primary source.
set -u
PASS=0; FAIL=0
check() {
  local name="$1"; local actual="$2"; local expected="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS  $name"
    PASS=$((PASS+1))
  else
    echo "  FAIL  $name"
    echo "        got:      '$actual'"
    echo "        expected: '$expected'"
    FAIL=$((FAIL+1))
  fi
}

cd "$(dirname "$0")"

echo "============================================================"
echo "  vfx-file-naming :: smoke test suite"
echo "============================================================"

echo ""
echo "--- build_name.py: spec examples (§3.2.1, dash separator) ---"
A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type bg --instance 01 --vendor dd --rev 1 --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "background plate" "$A" "un-ff25_ib_0100_bg01_dd_v001.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type el --instance 01 --vendor dd --rev 1 --description fire --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "fire element plate" "$A" "un-ff25_ib_0100_el01_dd_v001-fire.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type el --instance 02 --vendor dd --rev 1 --description smoke --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "smoke element plate" "$A" "un-ff25_ib_0100_el02_dd_v001-smoke.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type comp --vendor dd --rev 20 --frame 1000 --ext exr 2>/dev/null)
check "comp revision 20" "$A" "un-ff25_ib_0100_comp_dd_v020.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0000 --type cnpt --vendor dd --rev 1 --description dom-beard --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "concept, Dom's beard" "$A" "un-ff25_ib_0000_cnpt_dd_v001-dom-beard.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq act3 --shot 0000 --type cnpt --vendor ilm --rev 20 --description ice-charger --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "act 3 concept" "$A" "un-ff25_act3_0000_cnpt_ilm_v020-ice-charger.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0000 --type anim --vendor dd --rev 20 --description sub-explosion --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "generic animation" "$A" "un-ff25_ib_0000_anim_dd_v020-sub-explosion.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq show --shot 0000 --type ldev --vendor dd --rev 1 --description dom-old-age --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "look dev, whole show" "$A" "un-ff25_show_0000_ldev_dd_v001-dom-old-age.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq act1 --shot 0000 --type ldev --vendor dd --rev 1 --description dom-old-age --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "look dev, act one only" "$A" "un-ff25_act1_0000_ldev_dd_v001-dom-old-age.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq sc --shot 0000 --type ldev --vendor dd --rev 1 --description dom-old-age --frame 1000 --ext exr --desc-sep - 2>/dev/null)
check "look dev, generic sequence code" "$A" "un-ff25_sc_0000_ldev_dd_v001-dom-old-age.1000.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type mp --vendor dd --rev 23 --frame 1001 --ext exr 2>/dev/null)
check "main plate revision 23" "$A" "un-ff25_ib_0100_mp_dd_v023.1001.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --description mp-v023 --frame 1001 --ext exr --desc-sep - 2>/dev/null)
check "matte of plate rev 23" "$A" "un-ff25_ib_0100_matt_dd_v001-mp-v023.1001.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 2 --description mp-v023 --frame 1001 --ext exr --desc-sep - 2>/dev/null)
check "matte revised to v002" "$A" "un-ff25_ib_0100_matt_dd_v002-mp-v023.1001.exr"

echo ""
echo "--- build_name.py: other shapes ---"
A=$(python3 build_name.py --show gotr-s08e007 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --frame 1001 --ext exr 2>/dev/null)
check "episodic show id" "$A" "gotr-s08e007_ib_0100_matt_dd_v001.1001.exr"

A=$(python3 build_name.py --show hb-gotr-s08e007 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --frame 1001 --ext exr 2>/dev/null)
check "episodic show id with studio" "$A" "hb-gotr-s08e007_ib_0100_matt_dd_v001.1001.exr"

A=$(python3 build_name.py --show sw-rasp --seq ib --shot 0100 --type matt --vendor dd --rev 1 --frame 1001 --ext exr 2>/dev/null)
check "show id with franchise prefix" "$A" "sw-rasp_ib_0100_matt_dd_v001.1001.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type comp --vendor dd --rev 1 --frame 1001 --ext mov 2>/dev/null)
check "mov omits frame" "$A" "un-ff25_ib_0100_comp_dd_v001.mov"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --alternate 4k --frame 1001 --ext exr 2>/dev/null)
check "alternate version" "$A" "un-ff25_ib_0100_matt_dd_v001_a-4k.1001.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --camera L --frame 1001 --ext exr 2>/dev/null)
check "stereo left camera" "$A" "un-ff25_ib_0100_matt_dd_v001_L.1001.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --spec-version sv01.0 --frame 1001 --ext exr 2>/dev/null)
check "spec version slot" "$A" "un-ff25_ib_0100_matt_dd_v001_sv01.0.1001.exr"

A=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type other-magic --vendor dd --rev 1 --frame 1001 --ext exr 2>/dev/null)
check "custom type 'other-magic'" "$A" "un-ff25_ib_0100_other-magic_dd_v001.1001.exr"

A=$(python3 build_name.py un-ff25 ib 0100 matt dd 1 mp-v023 1001 exr 2>/dev/null)
check "positional form (underscore desc sep)" "$A" "un-ff25_ib_0100_matt_dd_v001_mp-v023.1001.exr"

echo ""
echo "--- build_name.py: failure cases (expect exit 1) ---"
python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --description "mp v023" --frame 1001 --ext exr >/dev/null 2>&1
check "whitespace in description rejected" "$?" "1"

python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type zzz --vendor dd --rev 1 --frame 1001 --ext exr >/dev/null 2>&1
check "unknown type rejected" "$?" "1"

python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --ext exr >/dev/null 2>&1
check "missing frame on .exr rejected" "$?" "1"

python3 build_name.py --show un-ff25 --seq ib --shot 010 --type matt --vendor dd --rev 1 --frame 1001 --ext exr >/dev/null 2>&1
check "3-digit shot rejected" "$?" "1"

python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dddd --rev 1 --frame 1001 --ext exr >/dev/null 2>&1
check "4-char vendor rejected" "$?" "1"

python3 build_name.py --show unff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --frame 1001 --ext exr >/dev/null 2>&1
check "malformed show id rejected" "$?" "1"

OUT=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --vendor dd --rev 1 --description mp_v023 --frame 1001 --ext exr 2>&1)
echo "$OUT" | grep -q "underscore"
check "underscore in description rejected" "$?" "0"

echo ""
echo "--- parse_name.py: spec examples ---"
P=$(python3 parse_name.py un-ff25_ib_0100_matt01_dd_v001_hard-premult.1001.exr --json 2>/dev/null)
check "matte parses" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["show"],d["seq"],d["shot"],d["type"],d["instance"],d["vendor"],d["rev"],d["description"],d["frame"])' 2>/dev/null)" "un-ff25 ib 0100 matt 01 dd 1 hard-premult 1001"

P=$(python3 parse_name.py un-ff25_ib_0100_el_dd_v001-fire.1000.exr --json 2>/dev/null)
check "dash-joined description parses (spec example form)" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["rev"],d["description"])' 2>/dev/null)" "1 fire"

P=$(python3 parse_name.py un-ff25_act3_0000_cnpt_ilm_v020_ice-charger.1000.exr --json 2>/dev/null)
check "act 3 concept parses" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["show"],d["seq"],d["shot"],d["type"],d["vendor"],d["description"])' 2>/dev/null)" "un-ff25 act3 0000 cnpt ilm ice-charger"

P=$(python3 parse_name.py un-ff25_ib_0100_matt_dd_v001_mp-v023.1001.exr --json 2>/dev/null)
check "matte of plate rev 23 parses" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["description"],d["frame"])' 2>/dev/null)" "mp-v023 1001"

P=$(python3 parse_name.py gotr-s08e007_ib_0100_matt_dd_v001.1001.exr --json 2>/dev/null)
check "episodic show id parses" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["show"])' 2>/dev/null)" "gotr-s08e007"

P=$(python3 parse_name.py un-ff25_ib_0100_matt_dd_v001_sv01.0.1001.exr --json 2>/dev/null)
check "spec version slot parses" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["spec_version"],d["frame"])' 2>/dev/null)" "sv01.0 1001"

# The spec's three 'ldev' examples place the description BEFORE the vendor.
# The parser must accept that form too.
P=$(python3 parse_name.py un-ff25_show_0000_ldev_dom-old-age_dd_v001.1000.exr --json 2>/dev/null)
check "description-before-vendor form parses (spec example)" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["show"],d["seq"],d["shot"],d["type"],d["vendor"],d["rev"],d["description"])' 2>/dev/null)" "un-ff25 show 0000 ldev dd 1 dom-old-age"

P=$(python3 parse_name.py un-ff25_ib_0100_other-magic_dd_v001.1001.exr --json 2>/dev/null)
check "custom type parses" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["type"],d["instance"])' 2>/dev/null)" "other magic"

P=$(python3 parse_name.py un-ff25_ib_0100_comp_dd_v001.mov --json 2>/dev/null)
check "mov: frame is None" "$(echo "$P" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["frame"],d["ext"])' 2>/dev/null)" "None mov"

echo ""
echo "--- parse_name.py: failure cases ---"
python3 parse_name.py "un-ff25 ib 0100 matt dd v001.1001.exr" >/dev/null 2>&1
check "whitespace rejected" "$?" "1"

python3 parse_name.py un-ff25_ib_010_matt_dd_v001.1001.exr >/dev/null 2>&1
check "3-digit shot rejected" "$?" "1"

python3 parse_name.py un-ff25_ib_0100_zzz_dd_v001.1001.exr >/dev/null 2>&1
check "unknown type rejected" "$?" "1"

python3 parse_name.py un-ff25_ib_0100_matt_dd_v1.1001.exr >/dev/null 2>&1
check "2-digit revision rejected" "$?" "1"

echo ""
echo "--- validate_name.py: OK / FAIL cases ---"
A=$(python3 validate_name.py un-ff25_ib_0100_matt01_dd_v001_hard-premult.1001.exr 2>/dev/null)
check "OK case" "$A" "OK"

# The spec's own examples use 'dd' (Digital Domain) — legal, but flagged.
A=$(python3 validate_name.py un-ff25_ib_0100_matt01_dd_v001_hard-premult.1001.exr 2>&1 >/dev/null | grep -c "known studio")
check "vendor 'dd' warns but does not fail" "$A" "1"

A=$(python3 validate_name.py "un-ff25 ib 0100 matt dd v001.1001.exr" 2>&1 | head -1)
check "FAIL: whitespace" "$A" "FAIL"

A=$(python3 validate_name.py un-ff25_ib_0100_comp_dd_v001.1001.mov 2>&1 | head -1)
check "FAIL: frame on mov" "$A" "FAIL"

A=$(python3 validate_name.py un-ff25_ib_0100_comp_dd_v001.exr 2>&1 | head -1)
check "FAIL: missing frame on exr" "$A" "FAIL"

A=$(python3 validate_name.py un-ff25_ib_010_comp_dd_v001.1001.exr 2>&1 | head -1)
check "FAIL: bad shot padding" "$A" "FAIL"

A=$(python3 validate_name.py un-ff25_ib_0100_zzz_dd_v001.1001.exr 2>&1 | head -1)
check "FAIL: unknown type" "$A" "FAIL"

echo ""
echo "--- Round-trip integrity (build → parse → rebuild) ---"
NAME=$(python3 build_name.py --show un-ff25 --seq ib --shot 0100 --type matt --instance 01 --vendor dd --rev 1 --description hard-premult --frame 1001 --ext exr 2>/dev/null)
PARSED=$(python3 parse_name.py "$NAME" --json 2>/dev/null)
REBUILT=$(python3 -c "
import json
d = json.loads('''$PARSED''')
import build_name
print(build_name.build(
    show=d['show'], seq=d['seq'], shot=d['shot'], type_=d['type'],
    instance=d['instance'], vendor=d['vendor'], rev=d['rev'],
    description=d['description'], alternate=d['alternate'], camera=d['camera'],
    spec_version=d['spec_version'], frame=d['frame'], ext=d['ext'],
))
" 2>/dev/null)
check "round-trip identical" "$REBUILT" "$NAME"

echo ""
echo "--- audit_folder.py ---"
TESTDIR=/tmp/vfx-audit-test
rm -rf "$TESTDIR" && mkdir -p "$TESTDIR"
touch "$TESTDIR/un-ff25_ib_0100_matt01_dd_v001_hard-premult.1001.exr"
touch "$TESTDIR/un-ff25_ib_0100_matt02_dd_v001_soft-unpremult.1001.exr"
touch "$TESTDIR/un-ff25_ib_0100_bg01_dd_v001.1000.exr"
touch "$TESTDIR/un-ff25_ib_0100_comp_dd_v001.mov"
touch "$TESTDIR/un-ff25_ib_0100_FINAL_dd_v001.mov"
touch "$TESTDIR/bad with space.exr"
touch "$TESTDIR/un-ff25_ib_010_comp_dd_v001.1001.exr"
touch "$TESTDIR/un-ff25_ib_0100_zzz_dd_v001.1001.exr"
touch "$TESTDIR/un-ff25_ib_0100_comp_dd_v001.1001.mov"
touch "$TESTDIR/random_unrelated.png"

OUT=$(python3 audit_folder.py "$TESTDIR" 2>&1)
check "audit reports 10 total" "$(echo "$OUT" | grep -E '^Total files[[:space:]]+:' | awk '{print $NF}')" "10"
check "audit reports 5 broken" "$(echo "$OUT" | grep -E '^Broken[[:space:]]+:' | awk '{print $NF}')" "5"
check "audit reports 5 compliant" "$(echo "$OUT" | grep -E '^Compliant[[:space:]]+:' | awk '{print $NF}')" "5"
check "audit reports 2 matte" "$(echo "$OUT" | grep -E '^  matte' | awk -F: '{print $2}' | tr -d ' ')" "2"
check "audit reports 2 comp" "$(echo "$OUT" | grep -E '^  comp' | awk -F: '{print $2}' | tr -d ' ')" "2"
check "audit reports 1 plate" "$(echo "$OUT" | grep -E '^  plate' | awk -F: '{print $2}' | tr -d ' ')" "1"
check "audit reports 5 warning files (all use vendor 'dd')" "$(echo "$OUT" | grep -E '^With warnings[[:space:]]+:' | awk '{print $NF}')" "5"

EXIT=$(python3 audit_folder.py "$TESTDIR" >/dev/null 2>&1; echo $?)
check "audit exit code = broken count" "$EXIT" "5"

echo ""
echo "============================================================"
echo "  RESULT:  $PASS passed,  $FAIL failed"
echo "============================================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
