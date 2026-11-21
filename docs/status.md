# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF, relocation, small/narrow names, party list, banners,
  lint, popups and every renderer-2 caller measured; left: squad formation names need the D11 remedy, the palace
  speaker box, card 1B9 mid-shot, see Next 1-3).
  Last build: `build/heian_en.sfc` 2026-11-22 sha1 8eb9b3e58340 (2 MB, smoke ok); marker `build/heian_marker.sfc`
  2026-11-22 sha1 8fc4bcc4818f (FF/203 as 24-px fields; scenes below shot in `work/qa/marker_warp/`).
- **Done:**
  - **Width gate, this session** (windows.md table): 28D/28E confirm popup = 112 px per line (scene
    `confirm_prompt`; 28E is a yes/no line, Yes at +24 px and No at +72 px, row note); FF 価値 shop label = 24-px
    field (scene `shop`); 203 音楽 battle window title = 24-px field (scene `battle_music`); status-screen jutsu /
    shikigami pages = 48 px (scenes `status_jutsu`, `status_shikigami`; a too-wide string spills into the neighbour
    slot's tiles). `insert.FIELDS` has FF and 203 at 24; `lint.POPUPS` has no guesses left.
  - Event interpreter `C5:99E4` runs only in mode 0A sub 0D: poking `$34=0A,$36=0D,$1244=0,$129E=10` builds the
    squad formation screen (scene `squad_form`); `tools/lua/steplog.lua` logs the interpreter state.
  - **Lint** `tools/lint.py` (in `tools/check.py` via `tests/test_lint.py`): dialogue 176 px/line, 160 on a 3rd
    line before `{page}`, 3 lines/page, `{name}` = widest English name (64 until names exist), `{num}` = "99999";
    fields via `fit_field`; party via `party_fits`; popups; codes multiset, encodable, no JP, no ordinal after a
    variable, stub last line. `--max` fills the `max` column; `--strict` makes untranslated rows errors (phase 7+).
  - Banners (windows.md): title slot list 48 px; place/port and map-exit banners 72 px, re-centred by the build.
  - Phase 5 engine (`docs/re/hooks.md`): 2 MB ROM, strings relocated to `$D8-$DE` with 24-bit `PTRS`; VWF on both
    glyph paths; fonts `fonts/en16.png`, `fonts/en8.png`, `fonts/en_narrow.png` (D9, D10, D11); small mode (D10);
    party list 8 slots x 5 tiles narrow (D11, `PartyName` in `asm/main.asm`).
  - Phases 1-4: recon (`docs/re/`), warp tool + save editor + god mode, identity build, `tbl/jp.tbl` + `script/`.
  - Check: 40 passed.
- **Next:**
  1. **Squad formation screen names** (`C1:6011`, `C1:5FBC`, VRAM table `C1:E6CE`, slots $18 words = 3 tiles of
     16-px text, 8 slots in two panels, pitch 56 px on screen): the marker shows cut one-row names, the same problem
     the party list had. Apply the D11 remedy (route through `PartyName`, narrow font, wider VRAM slots + tilemap;
     the screen is built by event steps $12-$14, `C5:9F23`..`C5:A00F`), verify with scene `squad_form` and a
     `--qa 054=Sadamitsu` stress build. Id 100 (empty slot, `　　`) must stay blank in English.
  2. Opening palace scene (ids 297-2A5: speaker line + 3 lines): not in the title demo nor in New Game. Likely an
     event script run by the interpreter: search bank C1 scripts (format: `C5:9D30`, words at `[$12A6]`) for the
     message ids, or poke `$12A6` to a candidate script with `$34=0A,$36=0D,$1244=0,$129E=4`. Measure, and teach
     the lint the speaker line.
  3. Province card 1B9: shoot mid-card (`SHOTS_AFTER`) to confirm 176.
  4. Then phase 6 (glossary first; translators get the `max` column and `tools/lint.py`).
  5. Non-table Japanese (battle command labels, status labels, captions, help screen): graphics, phase 8.
  6. Leads kept: staff roll near `C2:CA80`, small-font tilemap text (`script/tilemaps.tsv`), story-progress flags
     unmapped, item inventory and squad roster not mapped in the save (`--qa ID=...` stands in). Which unit opens
     the 音楽 battle menu (`$1516=6`) is not mapped.
- **Open bugs:** none. Untranslated (Japanese) party names show only their top half in the party list until phase 6
  fills `en` (by design of the one-row slots).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
