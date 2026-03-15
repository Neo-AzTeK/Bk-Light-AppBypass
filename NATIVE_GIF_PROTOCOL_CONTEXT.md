# NATIVE GIF PROTOCOL CONTEXT (iPixel reverse engineering)

_Last updated: 2026-03-15 (Europe/Paris)_

## Why this exists

The frame-by-frame scroll path is merged but not sufficient long-term (screen freezes after sustained use).  
Goal is to reproduce **native animated/GIF upload path** used by iPixel app.

---

## Ground truth validated today

1. **Transport BLE works** (connect + write on `fa02`) and static text/image path works.
2. Panel model in use: **ACT1025 (64x16)**, BLE name observed: `LED_BLE_BD32147A`, address seen: `31:C3:BD:32:14:7A`.
3. Wrong geometry (`32x32`) caused misleading behavior; corrected to `64x16` in `config.yaml`.
4. "Write success" is **not** success criterion.
   - Success criterion = **panel visibly renders expected content**.

---

## Files and scripts used

### Captures / extracted sequences
- `tmp/btmon_current.txt`
- `tmp/fa02_from_current.txt`
- `tmp/last_animA_candidate_seq.txt` (44 chunks)
- `tmp/animB_seq.txt` (39 chunks)
- Other historical sequences in `tmp/` (`animA_seq.txt`, `animB_*.txt`, etc.)

### Tools
- `scripts/extract_fa02_sequence.py`  
  Extracts `fa02` write payloads from btmon text logs.
- `scripts/replay_fa02_sequence.py`  
  Replays raw hex chunks to `fa02`.
- `scripts/native_scroll_inject_gif.py`  
  Replaces GIF region in a captured sequence (length-preserving patch).
- `scripts/native_scroll_build_from_template.py`  
  Template-based patcher that updates GIF bytes + selected metadata (`total_len`, `crc32`, optional channel).
- `scripts/native_protocol_tools.py`  
  Recover embedded GIF from sequence (`recover-gif`).

---

## What we currently understand about native animated path

## 1) There is a control/upload envelope in `fa02` traffic
Observed recurring structure in some chunks:

`0f 10 03 00 [chunk_idx] [total_len:4 LE] [crc32:4 LE] 02 [channel] ...`

Interpretation (best current hypothesis):
- `chunk_idx` = upload segment index
- `total_len` = full GIF payload length
- `crc32` = CRC32 of GIF payload
- `channel` = logical slot/layer/index for animation storage/playback

## 2) Additional mode/select packets exist
Examples seen around starts:
- `05 00 12 80 06`
- `07 00 08 80 01 00 XX`
- long config packets (`a9...`) that likely define rendering mode/slot/palette/meta

These are probably required to put firmware in correct state before payload is accepted/displayed.

## 3) Embedded GIF bytes are visible in captured payloads
Signatures found:
- `GIF89a` header
- trailer `0x3b`

So payload does carry actual GIF byte stream at some point.

## 4) CRC/len patch alone is not sufficient (so far)
We tested:
- raw replay of captured sequences
- GIF injection without metadata patch
- GIF injection with metadata patch (`total_len` + `crc32`)

Result often: no visual animation (panel remains LED/Bluetooth/default), meaning likely:
- more integrity fields than currently patched,
- or session/state sequencing constraints,
- or timing/ack/order constraints.

---

## What is still unknown

1. **Full integrity model**
   - Is there header checksum besides GIF CRC32?
   - Is there per-chunk checksum/MAC?
   - Is there final commit checksum across all chunks?

2. **State machine requirements**
   - Exact order of mode/select/start/upload/commit/play packets
   - Whether an explicit “apply/play” command is mandatory after upload

3. **Slot/channel semantics**
   - How slot IDs map to display behavior
   - Whether stale slot metadata blocks playback

4. **ACK/notify semantics in native path**
   - Which notifications correspond to accepted upload vs rejected silently

5. **Tail/finalization packets**
   - Candidate “tail” packets are observed but acceptance conditions are unclear

---

## Why we got misleading “success” signals before

- BLE write completion only confirms transport-level delivery.
- Firmware can silently reject payload at application layer.
- Therefore, each test must be judged by **visual render on panel**.

---

## Current recommended testing protocol (strict)

For each test case, do exactly this:

1. Confirm panel visible in scan (`LED_BLE_*`) and no competing phone app connected.
2. Send exactly one scenario (no mixed runs):
   - baseline static text,
   - or native sequence replay,
   - or patched native sequence.
3. Record both:
   - transport outcome (connect/write/errors)
   - visual outcome (`rendered` / `LED` / `Bluetooth icon` / other)
4. Do not mark success unless visual outcome matches expected content.
5. Keep all test artifacts:
   - input sequence file
   - patch parameters
   - exact command run
   - observed panel output

---

## Immediate next steps

1. Build a **single canonical native test-case bundle**:
   - one known-good capture with exact expected visual output,
   - extracted chunks,
   - annotations by phase (init/meta/upload/tail/play).

2. Add a parser script to decode chunk fields into a table:
   - detect all `0f100300` headers,
   - print offsets, indices, lengths, CRCs,
   - compare original vs patched sequences.

3. Add a “visual verdict log” template to avoid ambiguity.

4. Iterate on minimal-diff patches:
   - change one field family at a time,
   - replay,
   - confirm visual behavior.

---

## Acceptance criteria for project goal

Target capability is achieved only when:
1. We can upload a custom animation (derived from GIF or equivalent native payload),
2. Panel visibly plays it,
3. Reproducible across multiple retries without freezing,
4. Procedure/scripted enough to be reused.

---

## Note on today's mixed outputs

During troubleshooting, a red `1` display appeared due to identify/test overlap.  
Future runs should remain one-scenario-at-a-time to avoid cross-effects.
